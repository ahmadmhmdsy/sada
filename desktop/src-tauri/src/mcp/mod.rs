//! Sada as an MCP server: the app binary in stdio mode (Sada.exe --mcp).
//!
//! Agents already had two ways into Sada — the per-run local HTTP API and the bundled engine
//! binary. Both need something an agent cannot always supply: a live port (and a server toggle
//! somebody remembered to flip), or a pile of CLI flags. MCP removes that: the MCP client starts
//! this process, speaks JSON-RPC over its stdio, and gets transcription and saved transcripts
//! through four tools. Nothing listens on a network port and the GUI does not need to be running.
//!
//! The protocol is deliberately the small, widely supported subset of MCP: initialize,
//! notifications/initialized, ping, tools/list and tools/call. Requests are handled one at a
//! time; a transcription can take minutes, and a client that pipelined several would otherwise
//! race two engine processes for the same model file.
//!
//! stdout carries protocol frames and nothing else. Engine output is captured, logging goes to
//! stderr, and every response is written as one flushed line, which is what stdio transports
//! expect.

mod model_caps;
mod tools;
mod transcripts;

use serde_json::{json, Value};
use std::io::{self, BufRead, Write};
use std::path::PathBuf;

use tools::SadaInfo;

/// Argument that turns the app into an MCP stdio server instead of the GUI.
pub const MCP_ARG: &str = "--mcp";
/// Optional override for the app config file, used by tests and non-standard installs.
pub const CONFIG_ARG: &str = "--config";

/// Protocol revisions this server can speak, newest first. Unknown requests fall back to the
/// oldest one, which every current client accepts.
const PROTOCOL_VERSIONS: [&str; 3] = ["2025-06-18", "2025-03-26", "2024-11-05"];

const JSON_RPC_VERSION: &str = "2.0";

/// Everything a tool call may need from the app, resolved once per process.
pub struct Ctx {
    config_override: Option<PathBuf>,
    info: Option<SadaInfo>,
}

impl Ctx {
    fn info(&mut self) -> SadaInfo {
        if self.info.is_none() {
            self.info = Some(tools::resolve_info(self.config_override.clone()));
        }
        self.info.clone().expect("info was just resolved")
    }
}

/// Entry point used by main(): returns Some(exit code) when argv asks for MCP mode.
pub fn run_if_requested() -> Option<i32> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if !args.iter().any(|arg| arg == MCP_ARG) {
        return None;
    }
    let config_override = args
        .iter()
        .position(|arg| arg == CONFIG_ARG)
        .and_then(|index| args.get(index + 1))
        .map(PathBuf::from);
    Some(run(config_override))
}

/// Serve MCP over stdin/stdout until the client closes the stream. Returns the process exit code.
pub fn run(config_override: Option<PathBuf>) -> i32 {
    eprintln!(
        "sada-mcp {} ready (stdio; tools: sada_transcribe, sada_transcripts, sada_transcript, sada_info)",
        env!("CARGO_PKG_VERSION")
    );
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut output = stdout.lock();
    let mut ctx = Ctx { config_override, info: None };

    for line in stdin.lock().lines() {
        let line = match line {
            Ok(line) => line,
            Err(error) => {
                eprintln!("sada-mcp: stdin read failed: {error}");
                break;
            }
        };
        if line.trim().is_empty() {
            continue;
        }
        let Some(response) = handle_line(&line, &mut ctx) else {
            continue;
        };
        if writeln!(output, "{response}").and_then(|_| output.flush()).is_err() {
            eprintln!("sada-mcp: stdout closed, stopping");
            break;
        }
    }
    0
}

/// One JSON-RPC frame in, zero or one JSON-RPC frame out (notifications get no answer).
fn handle_line(line: &str, ctx: &mut Ctx) -> Option<String> {
    let message: Value = match serde_json::from_str(line) {
        Ok(message) => message,
        Err(error) => {
            return Some(json_rpc_error(Value::Null, -32700, &format!("parse error: {error}")));
        }
    };
    let id = message.get("id").cloned().filter(|id| !id.is_null());
    let method = message.get("method").and_then(Value::as_str).unwrap_or_default();

    match method {
        // Notifications: initialized is the only one the protocol requires us to accept, and it
        // needs no answer. Unknown notifications are ignored rather than treated as errors.
        "notifications/initialized" | "notifications/cancelled" => None,
        "initialize" => Some(handle_initialize(id, message.get("params").cloned())),
        "ping" => id.map(|id| json_rpc_result(id, json!({}))),
        "tools/list" => id.map(|id| json_rpc_result(id, json!({ "tools": tools::tool_definitions() }))),
        "tools/call" => Some(handle_tools_call(id, message.get("params").cloned(), ctx)),
        // Advertised capabilities are tools-only; answer the discovery probes some clients send
        // anyway with empty lists instead of an error they would surface to the user.
        "resources/list" => id.map(|id| json_rpc_result(id, json!({ "resources": [] }))),
        "prompts/list" => id.map(|id| json_rpc_result(id, json!({ "prompts": [] }))),
        other => id.map(|id| json_rpc_error(id, -32601, &format!("method not found: {other}"))),
    }
}

fn handle_initialize(id: Option<Value>, params: Option<Value>) -> String {
    let requested = params
        .as_ref()
        .and_then(|params| params.get("protocolVersion"))
        .and_then(Value::as_str);
    let version = negotiate_protocol_version(requested);
    let result = json!({
        "protocolVersion": version,
        "capabilities": { "tools": { "listChanged": false } },
        "serverInfo": {
            "name": "sada",
            "title": "Sada — Arabic-first offline transcription",
            "version": env!("CARGO_PKG_VERSION"),
        },
        "instructions": instructions(),
    });
    json_rpc_result(id.unwrap_or(Value::Null), result)
}

/// Text an MCP client shows its model once, at initialize.
fn instructions() -> &'static str {
    "Sada is an Arabic-first, fully offline speech-to-text app for Windows. \
Prefer sada_transcribe to transcribe a local audio or video file: it uses the user's configured \
model, never uploads media, and normalises Arabic punctuation and Latin acronyms. \
Read saved transcripts with sada_transcript, list them with sada_transcripts, and check paths \
with sada_info. Media must be local absolute file paths. The user's UI is Arabic (RTL); keep \
any Arabic text you return in Arabic."
}

fn negotiate_protocol_version(requested: Option<&str>) -> &'static str {
    match requested {
        Some(requested) if PROTOCOL_VERSIONS.contains(&requested) => PROTOCOL_VERSIONS
            .iter()
            .find(|version| **version == requested)
            .expect("requested version is in the list"),
        _ => PROTOCOL_VERSIONS[PROTOCOL_VERSIONS.len() - 1],
    }
}

fn handle_tools_call(id: Option<Value>, params: Option<Value>, ctx: &mut Ctx) -> String {
    let Some(id) = id else {
        // A notification for tools/call is malformed; nothing to answer without an id.
        return String::new();
    };
    let params = params.unwrap_or(Value::Null);
    let name = params.get("name").and_then(Value::as_str).unwrap_or_default();
    if name.is_empty() {
        return json_rpc_error(id, -32602, "tools/call needs a tool name");
    }
    if !tools::TOOL_NAMES.contains(&name) {
        return json_rpc_error(id, -32602, &format!("unknown tool: {name}"));
    }
    let arguments = params
        .get("arguments")
        .cloned()
        .filter(Value::is_object)
        .unwrap_or_else(|| json!({}));

    let result = match tools::call_tool(name, &arguments, ctx) {
        Ok(text) => json!({
            "content": [{ "type": "text", "text": text }],
            "isError": false,
        }),
        Err(message) => json!({
            "content": [{ "type": "text", "text": message }],
            "isError": true,
        }),
    };
    json_rpc_result(id, result)
}

fn json_rpc_result(id: Value, result: Value) -> String {
    json!({ "jsonrpc": JSON_RPC_VERSION, "id": id, "result": result }).to_string()
}

fn json_rpc_error(id: Value, code: i64, message: &str) -> String {
    json!({
        "jsonrpc": JSON_RPC_VERSION,
        "id": id,
        "error": { "code": code, "message": message },
    })
    .to_string()
}

#[cfg(test)]
mod tests {
    use super::{handle_line, negotiate_protocol_version, Ctx};
    use serde_json::Value;

    fn ctx() -> Ctx {
        Ctx { config_override: None, info: None }
    }

    fn request(line: &str) -> Value {
        let response = handle_line(line, &mut ctx()).expect("request must be answered");
        serde_json::from_str(&response).expect("response must be JSON")
    }

    fn call(params: &str) -> Value {
        let params: Value = serde_json::from_str(params).expect("params must be JSON");
        request(&serde_json::json!({ "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": params }).to_string())
    }

    #[test]
    fn initialize_reports_tools_and_echoes_a_known_protocol_version() {
        let response = request(r#"{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26"}}"#);
        assert_eq!(response["id"], 1);
        assert_eq!(response["result"]["protocolVersion"], "2025-03-26");
        assert_eq!(response["result"]["serverInfo"]["name"], "sada");
        assert!(response["result"]["instructions"].as_str().unwrap().contains("Arabic-first"));
    }

    #[test]
    fn initialize_falls_back_to_the_oldest_protocol_version_for_an_unknown_one() {
        assert_eq!(negotiate_protocol_version(Some("1999-01-01")), "2024-11-05");
        assert_eq!(negotiate_protocol_version(None), "2024-11-05");
    }

    #[test]
    fn tools_list_contains_the_four_tools() {
        let response = request(r#"{"jsonrpc":"2.0","id":2,"method":"tools/list"}"#);
        let tools = response["result"]["tools"].as_array().expect("tools array");
        let names: Vec<&str> = tools.iter().filter_map(|tool| tool["name"].as_str()).collect();
        assert_eq!(names, vec!["sada_transcribe", "sada_transcripts", "sada_transcript", "sada_info"]);
        for tool in tools {
            assert!(tool["description"].as_str().is_some_and(|text| text.contains("Sada") || text.contains("transcript")));
            assert_eq!(tool["inputSchema"]["type"], "object");
        }
    }

    #[test]
    fn notifications_get_no_response() {
        assert!(handle_line(r#"{"jsonrpc":"2.0","method":"notifications/initialized"}"#, &mut ctx()).is_none());
    }

    #[test]
    fn unknown_methods_are_json_rpc_errors() {
        let response = request(r#"{"jsonrpc":"2.0","id":9,"method":"tools/execute"}"#);
        assert_eq!(response["error"]["code"], -32601);
    }

    #[test]
    fn malformed_json_is_a_parse_error() {
        let response = request("{not json");
        assert_eq!(response["error"]["code"], -32700);
        assert_eq!(response["id"], Value::Null);
    }

    #[test]
    fn unknown_tools_are_invalid_params() {
        let response = call(r#"{"name":"sada_missing","arguments":{}}"#);
        assert_eq!(response["error"]["code"], -32602);
    }

    #[test]
    fn sada_info_returns_json_about_this_install() {
        let response = call(r#"{"name":"sada_info","arguments":{}}"#);
        assert_eq!(response["result"]["isError"], false);
        let text = response["result"]["content"][0]["text"].as_str().unwrap();
        let info: Value = serde_json::from_str(text).expect("info is JSON");
        assert_eq!(info["app"], "Sada");
        assert_eq!(info["arabic_first"], true);
        assert!(info["tools"].as_array().is_some_and(|tools| tools.len() == 4));
    }
}
