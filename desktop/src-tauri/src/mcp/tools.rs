//! Tool schemas, install resolution, and the four tool implementations.
//!
//! Every tool resolves the real install: app_config.json for the model, language and transcript
//! folder; the bundled engine next to the app binary; and Documents/Sada for saved transcripts.
//! Only the transcription settings named below are copied into a tool result -- provider API
//! keys and other unrelated config values never leave the app.

use super::transcripts::{
    display_path, entry_name, format_centiseconds, read_record, resolve_record_path, scan_transcripts,
};
use super::model_caps::{self, LanguageChoice};
use super::Ctx;
use crate::arabic;
use serde_json::{json, Value};
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

pub(super) const TOOL_NAMES: [&str; 4] = [
    "sada_transcribe",
    "sada_transcripts",
    "sada_transcript",
    "sada_info",
];

const DEFAULT_LIMIT: usize = 10;
const MAX_LIMIT: usize = 50;

/// Everything the tools need to know about one install, resolved once per MCP process.
#[derive(Clone, Debug)]
pub struct SadaInfo {
    pub config_path: PathBuf,
    pub config_present: bool,
    pub config: Value,
    pub engine: Option<PathBuf>,
    pub ffmpeg: Option<PathBuf>,
    pub model: Option<PathBuf>,
    pub models_folder: PathBuf,
    pub transcripts_dir: PathBuf,
    pub language: String,
}

/// The MCP tool list handed to tools/list.
pub fn tool_definitions() -> Vec<Value> {
    vec![
        json!({
            "name": "sada_transcribe",
            "description": "Transcribe a local audio or video file with Sada's configured model (Whisper, Parakeet or Nemotron). Arabic-first: defaults to the user's configured language (Arabic unless changed), never uploads media, and normalises Arabic punctuation and Latin acronyms. The model's capabilities decide whether translation, prompts and a Silero VAD model are used. Returns the transcript text; set timestamps for [start --> end] lines.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": { "type": "string", "description": "Absolute path to a local audio or video file (mp3, wav, m4a, mp4, mkv, ...). URLs are not supported." },
                    "language": { "type": "string", "description": "Language to transcribe: a Whisper code such as 'ar' or 'en', a model code such as 'ar-AR', or 'auto' to detect. Base codes are mapped onto what the configured model advertises. Defaults to the user's Sada language setting." },
                    "translate": { "type": "boolean", "description": "Translate the speech to English instead of transcribing it in the source language (Whisper only; models without translation ignore it). Off by default." },
                    "timestamps": { "type": "boolean", "description": "Prefix every segment with its [start --> end] timecode. Off by default." },
                    "normalize": { "type": "boolean", "description": "Apply Sada's Arabic normalization (Arabic punctuation, Latin acronyms). Default true." },
                    "model": { "type": "string", "description": "Absolute path of a ggml model to use instead of the configured one (advanced)." },
                    "prompt": { "type": "string", "description": "Initial prompt passed to the engine (Whisper only; models without text prompts ignore it). Defaults to the app's configured prompt." },
                    "threads": { "type": "integer", "description": "CPU threads for the engine; 0 or omitted uses the app's configured/default value." },
                    "enhance_audio": { "type": "boolean", "description": "Normalise loudness with FFmpeg before transcribing. Off by default." },
                    "vad_model": { "type": "string", "description": "Absolute path of a Silero VAD model, for engines that need one (advanced; found automatically next to the configured model when omitted)." }
                },
                "required": ["path"],
                "additionalProperties": false
            }
        }),
        json!({
            "name": "sada_transcripts",
            "description": "List the transcripts the user saved from Sada, newest first, with the folder, record path and a short preview. Use the paths with sada_transcript.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": { "type": "integer", "minimum": 1, "maximum": 50, "description": "How many transcripts to return. Default 10, maximum 50." },
                    "folder": { "type": "string", "description": "Read a different transcripts folder instead of the configured one (advanced)." }
                },
                "additionalProperties": false
            }
        }),
        json!({
            "name": "sada_transcript",
            "description": "Read one saved Sada transcript as text, optionally with [start --> end] timecodes and speaker labels. Defaults to the newest transcript.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": { "type": "string", "description": "Path to a transcript.vibe.json file or its project folder. Omit to read the newest transcript." },
                    "timestamps": { "type": "boolean", "description": "Prefix each line with its [start --> end] timecode. Off by default." },
                    "speakers": { "type": "boolean", "description": "Label diarized lines as [speaker 1], [speaker 2], ... Off by default." },
                    "include_summary": { "type": "boolean", "description": "Append the transcript's last saved summary, when there is one. Off by default." }
                },
                "additionalProperties": false
            }
        }),
        json!({
            "name": "sada_info",
            "description": "Report Sada's version, configured model, engine, transcript folder and config path, and whether each file resolves. Use it first when a tool reports a missing model or engine.",
            "inputSchema": { "type": "object", "properties": {}, "additionalProperties": false }
        }),
    ]
}

/// Dispatch a tools/call. Errors become isError results, never process exits.
pub fn call_tool(name: &str, arguments: &Value, ctx: &mut Ctx) -> Result<String, String> {
    let info = ctx.info();
    match name {
        "sada_transcribe" => transcribe(arguments, &info),
        "sada_transcripts" => list_transcripts(arguments, &info),
        "sada_transcript" => read_transcript(arguments, &info),
        "sada_info" => info_text(&info),
        other => Err(format!("Unknown tool: {other}")),
    }
}

// ---------------------------------------------------------------------------------------------
// Install resolution
// ---------------------------------------------------------------------------------------------

/// The app config first, then known install locations, so this works both for an installed Sada
/// and for a developer running the app out of target/debug.
pub fn resolve_info(config_override: Option<PathBuf>) -> SadaInfo {
    let candidates = config_candidates(config_override);
    let config_path = candidates
        .iter()
        .find(|path| path.is_file())
        .cloned()
        .unwrap_or_else(|| candidates.first().cloned().unwrap_or_default());
    let config_present = config_path.is_file();
    let config = fs::read_to_string(&config_path)
        .ok()
        .and_then(|text| serde_json::from_str::<Value>(&text).ok())
        .filter(Value::is_object)
        .unwrap_or_else(|| json!({}));

    let model = config_string(&config, "model.path").map(PathBuf::from);
    let transcripts_dir = config_string(&config, "transcription.projectsPath")
        .map(PathBuf::from)
        .or_else(|| env::var_os("SADA_TRANSCRIPTS_DIR").map(PathBuf::from))
        .unwrap_or_else(|| documents_dir().join("Sada"));
    let language = config
        .get("transcription.modelOptions")
        .and_then(|options| config_string(options, "lang"))
        .unwrap_or_else(|| "ar".to_string());
    // The GUI stores the models folder in the same app_config.json; its default is the app's
    // local data folder, which is where download_model() writes when nothing was chosen.
    let models_folder = config_string(&config, "models_folder")
        .map(PathBuf::from)
        .or_else(|| app_local_data_dir())
        .unwrap_or_else(|| PathBuf::from("."));
    let engine = find_engine();
    let ffmpeg = find_ffmpeg(engine.as_deref());

    SadaInfo {
        config_path,
        config_present,
        config,
        engine,
        ffmpeg,
        model,
        models_folder,
        transcripts_dir,
        language,
    }
}

/// The default models folder on this platform: the app-local data directory Tauri hands
/// the GUI when no custom folder was chosen.
fn app_local_data_dir() -> Option<PathBuf> {
    if let Some(base) = env::var_os("LOCALAPPDATA").map(PathBuf::from) {
        return Some(base.join("app.sada.desktop"));
    }
    if let Some(base) = env::var_os("APPDATA").map(PathBuf::from) {
        return Some(base.join("app.sada.desktop"));
    }
    None
}

fn config_candidates(config_override: Option<PathBuf>) -> Vec<PathBuf> {
    if let Some(path) = config_override {
        return vec![path];
    }
    let mut candidates = Vec::new();
    if let Some(path) = env::var_os("SADA_CONFIG_PATH").map(PathBuf::from) {
        candidates.push(path);
    }
    // Tauri v2 stores app_config.json under the app data dir, keyed by the app identifier.
    for root in ["APPDATA", "LOCALAPPDATA"] {
        if let Some(base) = env::var_os(root).map(PathBuf::from) {
            candidates.push(base.join("app.sada.desktop").join("app_config.json"));
        }
    }
    // A profile that once ran an upstream Vibe build keeps its settings in a different folder;
    // read it as a fallback instead of pretending the user never configured a model.
    for legacy in ["github.com.thewh1teagle.vibe", "com.vibe.desktop"] {
        for root in ["APPDATA", "LOCALAPPDATA"] {
            if let Some(base) = env::var_os(root).map(PathBuf::from) {
                candidates.push(base.join(legacy).join("app_config.json"));
            }
        }
    }
    if candidates.is_empty() {
        candidates.push(PathBuf::from("app_config.json"));
    }
    candidates
}

/// The Documents folder Windows actually redirects Sada's saves to. OneDrive redirection is
/// common enough on Windows 11 that checking it first matters more than the literal path.
fn documents_dir() -> PathBuf {
    for variable in ["OneDrive", "OneDriveCommercial", "OneDriveConsumer"] {
        if let Some(root) = env::var_os(variable).map(PathBuf::from) {
            let documents = root.join("Documents");
            if documents.is_dir() {
                return documents;
            }
        }
    }
    env::var_os("USERPROFILE")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
        .join("Documents")
}

/// The engine ships next to the app binary (externalBin), so look there first; the ancestor
/// walks keep cargo run and the repository layout working without any configuration.
fn find_engine() -> Option<PathBuf> {
    if let Some(path) = env::var_os("SADA_ENGINE").map(PathBuf::from).filter(|path| path.is_file()) {
        return Some(path);
    }
    let names = [
        "vibe-server.exe",
        "vibe-server-x86_64-pc-windows-msvc.exe",
        "vibe-server",
    ];
    let mut folders: Vec<PathBuf> = Vec::new();
    if let Ok(executable) = env::current_exe() {
        if let Some(folder) = executable.parent() {
            folders.push(folder.to_path_buf());
            folders.push(folder.join("resources"));
            for ancestor in folder.ancestors().take(5) {
                folders.push(ancestor.to_path_buf());
                folders.push(ancestor.join("binaries"));
                folders.push(ancestor.join("desktop").join("src-tauri").join("binaries"));
                folders.push(ancestor.join("src-tauri").join("binaries"));
            }
        }
    }
    if let Ok(current) = env::current_dir() {
        for ancestor in current.ancestors().take(5) {
            folders.push(ancestor.join("binaries"));
            folders.push(ancestor.join("desktop").join("src-tauri").join("binaries"));
        }
    }
    for folder in &folders {
        for name in names {
            let candidate = folder.join(name);
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }
    if let Some(paths) = env::var_os("PATH") {
        for folder in env::split_paths(&paths) {
            for name in names {
                let candidate = folder.join(name);
                if candidate.is_file() {
                    return Some(candidate);
                }
            }
        }
    }
    None
}

fn find_ffmpeg(engine: Option<&Path>) -> Option<PathBuf> {
    if let Some(path) = env::var_os("VIBE_SERVER_FFMPEG_PATH").map(PathBuf::from).filter(|path| path.is_file()) {
        return Some(path);
    }
    let names = [
        "ffmpeg.exe",
        "ffmpeg-x86_64-pc-windows-msvc.exe",
        "ffmpeg",
    ];
    let mut folders: Vec<PathBuf> = Vec::new();
    if let Some(engine) = engine {
        if let Some(folder) = engine.parent() {
            folders.push(folder.to_path_buf());
            for ancestor in folder.ancestors().take(5) {
                folders.push(ancestor.join("binaries"));
                folders.push(ancestor.join("desktop").join("src-tauri").join("binaries"));
            }
        }
    }
    if let Ok(executable) = env::current_exe() {
        if let Some(folder) = executable.parent() {
            folders.push(folder.to_path_buf());
        }
    }
    for folder in &folders {
        for name in names {
            let candidate = folder.join(name);
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }
    None
}

fn config_string(config: &Value, key: &str) -> Option<String> {
    config
        .get(key)
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(ToString::to_string)
}

fn config_bool(config: &Value, key: &str) -> Option<bool> {
    config.get(key).and_then(Value::as_bool)
}

fn config_i64(config: &Value, key: &str) -> Option<i64> {
    config.get(key).and_then(Value::as_i64)
}

fn config_number(config: &Value, key: &str) -> Option<f64> {
    config.get(key).and_then(Value::as_f64)
}

// ---------------------------------------------------------------------------------------------
// sada_info
// ---------------------------------------------------------------------------------------------

fn info_text(info: &SadaInfo) -> Result<String, String> {
    let payload = json!({
        "app": "Sada",
        "version": env!("CARGO_PKG_VERSION"),
        "platform": env::consts::OS,
        "arabic_first": true,
        "engine": {
            "path": info.engine.as_ref().map(|path| display_path(path)),
            "present": info.engine.as_ref().is_some_and(|path| path.is_file()),
        },
        "ffmpeg": {
            "path": info.ffmpeg.as_ref().map(|path| display_path(path)),
            "present": info.ffmpeg.as_ref().is_some_and(|path| path.is_file()),
        },
        "model": {
            "path": info.model.as_ref().map(|path| display_path(path)),
            "present": info.model.as_ref().is_some_and(|path| path.is_file()),
            "capabilities": model_capabilities(info),
        },
        "models_folder": display_path(&info.models_folder),
        "transcription": {
            "default_language": info.language,
            "normalizes_arabic": true,
            "media_stays_local": true,
        },
        "config_path": display_path(&info.config_path),
        "config_present": info.config_present,
        "transcripts_dir": display_path(&info.transcripts_dir),
        "tools": TOOL_NAMES,
        "notes": [
            "No network is used: media is transcribed on this machine and never uploaded.",
            "MCP is stdio-only; Sada opens no port for it and the GUI does not need to be running.",
            "If the model is missing, open Sada -> Settings -> Models and download or select a ggml model, then retry.",
        ],
    });
    serde_json::to_string_pretty(&payload).map_err(|error| format!("Could not serialise info: {error}"))
}

/// Capabilities of the configured model, probed from the file itself. A probe failure is
/// reported as a value rather than an error: sada_info must still describe the rest of the
/// install when the selected model happens to be unreadable.
fn model_capabilities(info: &SadaInfo) -> Value {
    let Some(model) = info.model.as_ref().filter(|path| path.is_file()) else {
        return Value::Null;
    };
    match model_caps::model_caps(model) {
        Ok(caps) => json!({
            "engine": caps.engine.as_str(),
            "requires_vad": caps.requires_vad,
            "languages": caps.languages,
            "language_detection": caps.language_detection,
            "translation": caps.translation,
            "text_prompts": caps.text_prompts,
        }),
        Err(error) => json!({ "error": error }),
    }
}

// ---------------------------------------------------------------------------------------------
// sada_transcribe
// ---------------------------------------------------------------------------------------------

fn transcribe(arguments: &Value, info: &SadaInfo) -> Result<String, String> {
    let audio = resolve_media_path(arguments)?;
    let model = string_argument(arguments, "model")
        .map(PathBuf::from)
        .or_else(|| info.model.clone())
        .ok_or_else(|| model_missing_error(info))?;
    if !model.is_file() {
        return Err(format!(
            "The configured model does not exist:\n  {}\n\nOpen Sada -> Settings -> Models, download or select a model, then retry. If the config file was edited by hand, check its model.path value:\n  {}",
            display_path(&model),
            display_path(&info.config_path),
        ));
    }
    let engine = info
        .engine
        .as_ref()
        .filter(|path| path.is_file())
        .ok_or_else(engine_missing_error)?;

    // What the configured model can do decides the command line: the GGUF engines reject
    // Whisper-only flags, need a Silero VAD model, and advertise full language codes instead
    // of Whisper's two-letter ones. Reading this from the file keeps MCP port-free.
    let caps = model_caps::model_caps(&model)?;
    let requested_language = string_argument(arguments, "language").unwrap_or_else(|| info.language.clone());
    let language = model_caps::resolve_language(&requested_language, &caps).map_err(|error| {
        format!(
            "{error}\n\nThe configured model is {} ({}). Open Sada -> Settings -> Models to change it, or Settings -> Transcription to change the language.",
            caps.engine.as_str(),
            display_path(&model),
        )
    })?;
    let vad_model = match string_argument(arguments, "vad_model") {
        Some(path) => Some(PathBuf::from(path)),
        None => model_caps::resolve_vad_model(&caps, &model, &info.models_folder)?,
    };
    if let Some(path) = vad_model.as_ref() {
        let usable = path.metadata().is_ok_and(|metadata| metadata.is_file() && metadata.len() > 0);
        if !usable {
            return Err(format!(
                "The VAD model at {} is missing or empty. Open Sada -> Settings -> Models and select the model again so the VAD file is downloaded.",
                display_path(path),
            ));
        }
    }

    let options = model_options(info);
    let mut command = Command::new(engine);
    command.arg("transcribe").arg(&model).arg(&audio);
    match language {
        LanguageChoice::Detect => {
            command.arg("--detect-language");
        }
        LanguageChoice::Code(code) => {
            command.args(["--language", &code]);
        }
    }

    let translate = bool_argument(arguments, "translate")
        .or_else(|| config_bool(options, "translate"))
        .unwrap_or(false);
    if translate && caps.translation {
        command.arg("--translate");
    }

    let threads = integer_argument(arguments, "threads")
        .or_else(|| config_i64(options, "n_threads"))
        .unwrap_or(0);
    if threads > 0 {
        command.args(["--threads", &threads.to_string()]);
    }

    let timestamps = bool_argument(arguments, "timestamps").unwrap_or(false);
    if timestamps {
        // With word timestamps the engine prints timed segments; a segment length turns the
        // word list into readable lines instead of one timecode per word.
        command.args(["--word-timestamps", "--max-segment-len", "32"]);
    }

    let prompt = string_argument(arguments, "prompt").or_else(|| config_string(options, "init_prompt"));
    if let Some(prompt) = prompt.filter(|prompt| !prompt.trim().is_empty()) {
        // Nemotron and Parakeet reject --prompt; the capability probe knows which engine this is.
        if caps.text_prompts {
            command.args(["--prompt", &prompt]);
        }
    }

    // Match the app's decoding settings, so MCP output is what the same file produces in the UI
    // rather than the engine's own defaults.
    match config_string(options, "sampling_strategy").as_deref() {
        Some("greedy") => {
            if let Some(best_of) = config_i64(options, "best_of").filter(|value| *value > 0) {
                command.args(["--best-of", &best_of.to_string()]);
            }
        }
        _ => {
            if let Some(beam_size) = config_i64(options, "beam_size").filter(|value| *value > 0) {
                command.args(["--beam-size", &beam_size.to_string()]);
            }
        }
    }
    if let Some(temperature) = config_number(options, "temperature").filter(|value| *value > 0.0) {
        command.args(["--temperature", &temperature.to_string()]);
    }
    if let Some(max_text_ctx) = config_i64(options, "max_text_ctx").filter(|value| *value > 0) {
        command.args(["--max-text-ctx", &max_text_ctx.to_string()]);
    }
    if bool_argument(arguments, "enhance_audio").unwrap_or(false) {
        command.arg("--enhance-audio");
    }
    if let Some(vad_model) = vad_model.as_ref() {
        command.args(["--vad-model", &vad_model.to_string_lossy().into_owned()]);
    }
    if let Some(ffmpeg) = info.ffmpeg.as_ref().filter(|path| path.is_file()) {
        command.env("VIBE_SERVER_FFMPEG_PATH", ffmpeg);
    }
    command.stdin(Stdio::null());

    let output = command.output().map_err(|error| {
        format!(
            "Could not start Sada's transcription engine at {}: {error}\n\nReinstall Sada, or point the SADA_ENGINE environment variable at the vibe-server binary.",
            display_path(engine),
        )
    })?;
    if !output.status.success() {
        return Err(format!(
            "Transcription failed ({}):\n\n{}",
            output.status,
            tail(&String::from_utf8_lossy(&output.stderr), 1200),
        ));
    }
    let text = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if text.is_empty() {
        return Err(format!(
            "The engine returned no text for {}.\n\nThe file may be silent, truncated or in a format the bundled FFmpeg cannot decode.",
            display_path(&audio),
        ));
    }
    let normalize = bool_argument(arguments, "normalize").unwrap_or(true);
    Ok(if normalize { arabic::normalize_arabic(&text) } else { text })
}

fn resolve_media_path(arguments: &Value) -> Result<PathBuf, String> {
    let raw = string_argument(arguments, "path")
        .ok_or_else(|| "sada_transcribe needs a path to a local audio or video file.".to_string())?;
    if raw.starts_with("http://") || raw.starts_with("https://") || raw.starts_with("www.") {
        return Err(format!(
            "Only local files can be transcribed; nothing is downloaded from {raw}.\n\nDownload or import the media into Sada first (Home -> Files), then pass its local path."
        ));
    }
    let path = PathBuf::from(&raw);
    if !path.exists() {
        return Err(format!("File not found: {raw}"));
    }
    if !path.is_file() {
        return Err(format!("Path is not a file: {raw}"));
    }
    fs::canonicalize(&path).map_err(|error| format!("Could not resolve {raw}: {error}"))
}

fn engine_missing_error() -> String {
    "Sada's transcription engine (vibe-server.exe) was not found next to the app or on PATH.\n\nReinstall Sada, or set the SADA_ENGINE environment variable to the engine binary.".to_string()
}

fn model_missing_error(info: &SadaInfo) -> String {
    format!(
        "No model is configured for Sada, so transcription cannot start.\n\nOpen Sada -> Settings -> Models, download or select a model (large-v3-turbo is the recommendation), then retry.\n\nConfig file checked:\n  {}",
        display_path(&info.config_path),
    )
}

// ---------------------------------------------------------------------------------------------
// sada_transcripts / sada_transcript
// ---------------------------------------------------------------------------------------------

fn list_transcripts(arguments: &Value, info: &SadaInfo) -> Result<String, String> {
    let folder = string_argument(arguments, "folder")
        .map(PathBuf::from)
        .unwrap_or_else(|| info.transcripts_dir.clone());
    let limit = integer_argument(arguments, "limit")
        .unwrap_or(DEFAULT_LIMIT as i64)
        .clamp(1, MAX_LIMIT as i64) as usize;
    let entries = scan_transcripts(&folder)?;
    let transcripts: Vec<Value> = entries
        .iter()
        .take(limit)
        .map(|entry| {
            json!({
                "name": entry.name,
                "created_at": entry.created_at,
                "language": entry.language,
                "path": display_path(&entry.path),
                "audio": entry.audio.as_ref().map(|path| display_path(path)),
                "preview": entry.preview,
            })
        })
        .collect();
    let payload = json!({
        "folder": display_path(&folder),
        "total": entries.len(),
        "shown": transcripts.len(),
        "transcripts": transcripts,
        "hint": "Read one with sada_transcript and its path, or call sada_transcript with no path for the newest.",
    });
    serde_json::to_string_pretty(&payload).map_err(|error| format!("Could not serialise transcripts: {error}"))
}

fn read_transcript(arguments: &Value, info: &SadaInfo) -> Result<String, String> {
    let explicit = string_argument(arguments, "path").map(PathBuf::from);
    let record_path = match explicit {
        Some(path) => resolve_record_path(&path)?,
        None => {
            let entries = scan_transcripts(&info.transcripts_dir)?;
            let latest = entries.into_iter().next().ok_or_else(|| {
                format!(
                    "No saved transcripts yet in {}. Transcribe something in Sada and save it, then retry.",
                    display_path(&info.transcripts_dir),
                )
            })?;
            latest.path
        }
    };
    let record = read_record(&record_path)?.ok_or_else(|| {
        format!(
            "Could not read {} as a Sada transcript (expected a JSON object with segments).",
            display_path(&record_path),
        )
    })?;
    let folder = record_path.parent().map(Path::to_path_buf).unwrap_or_default();
    let name = record
        .get("name")
        .and_then(Value::as_str)
        .filter(|name| !name.trim().is_empty())
        .map(str::to_string)
        .unwrap_or_else(|| entry_name(&record_path));
    let created_at = record.get("createdAt").and_then(Value::as_str).unwrap_or("unknown");
    let language = record.get("language").and_then(Value::as_str).unwrap_or("unknown");
    let audio = record
        .get("audioFile")
        .and_then(Value::as_str)
        .map(|file| folder.join(file))
        .filter(|path| path.is_file())
        .or_else(|| record.get("sourcePath").and_then(Value::as_str).map(PathBuf::from));

    let timestamps = bool_argument(arguments, "timestamps").unwrap_or(false);
    let speakers = bool_argument(arguments, "speakers").unwrap_or(false);
    let segments = record.get("segments").and_then(Value::as_array).cloned().unwrap_or_default();
    let mut body = String::new();
    for segment in &segments {
        let text = segment.get("text").and_then(Value::as_str).unwrap_or("").trim();
        if text.is_empty() {
            continue;
        }
        if timestamps {
            let start = segment.get("start").and_then(Value::as_i64).unwrap_or(0).max(0);
            let stop = segment.get("stop").and_then(Value::as_i64).unwrap_or(0).max(0);
            body.push_str(&format!("[{} --> {}] ", format_centiseconds(start), format_centiseconds(stop)));
        }
        if speakers {
            if let Some(speaker) = segment.get("speaker").and_then(Value::as_i64) {
                body.push_str(&format!("[speaker {}] ", speaker + 1));
            }
        }
        body.push_str(text);
        body.push('\n');
    }

    let mut document = format!(
        "# {name}\n\n- saved: {created_at}\n- language: {language}\n- record: {}\n",
        display_path(&record_path),
    );
    if let Some(audio) = audio {
        document.push_str(&format!("- audio: {}\n", display_path(&audio)));
    }
    document.push('\n');
    document.push_str(&body);

    if bool_argument(arguments, "include_summary").unwrap_or(false) {
        if let Some(summary) = record
            .get("summary")
            .and_then(Value::as_str)
            .filter(|summary| !summary.trim().is_empty())
        {
            document.push_str("\n## Summary\n\n");
            document.push_str(summary.trim());
            document.push('\n');
        }
    }
    Ok(document)
}

// ---------------------------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------------------------

fn model_options(info: &SadaInfo) -> &Value {
    static EMPTY: Value = Value::Null;
    info.config
        .get("transcription.modelOptions")
        .unwrap_or(&EMPTY)
}

fn tail(text: &str, max_chars: usize) -> String {
    let text = text.trim();
    let count = text.chars().count();
    if count <= max_chars {
        text.to_string()
    } else {
        text.chars().skip(count - max_chars).collect::<String>()
    }
}

fn string_argument(arguments: &Value, key: &str) -> Option<String> {
    arguments
        .get(key)
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(ToString::to_string)
}

fn bool_argument(arguments: &Value, key: &str) -> Option<bool> {
    arguments.get(key).and_then(Value::as_bool)
}

fn integer_argument(arguments: &Value, key: &str) -> Option<i64> {
    arguments.get(key).and_then(Value::as_i64)
}

#[cfg(test)]
mod tests {
    use super::{call_tool, resolve_info};
    use crate::mcp::Ctx;
    use serde_json::json;
    use std::fs;
    use std::path::PathBuf;

    fn scratch(name: &str) -> PathBuf {
        let folder = std::env::temp_dir().join(format!("sada-mcp-tools-{name}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&folder);
        fs::create_dir_all(&folder).expect("create scratch folder");
        folder
    }

    fn ctx(folder: &PathBuf) -> Ctx {
        Ctx {
            config_override: Some(folder.join("app_config.json")),
            info: None,
        }
    }

    #[test]
    fn resolves_model_language_and_transcripts_folder_from_the_app_config() {
        let folder = scratch("config");
        let transcripts = folder.join("Sada");
        fs::create_dir_all(&transcripts).unwrap();
        fs::write(
            folder.join("app_config.json"),
            json!({
                "model.path": "C:/models/ggml-tiny.bin",
                "transcription.projectsPath": transcripts,
                "transcription.modelOptions": { "lang": "ar", "beam_size": 5 },
            })
            .to_string(),
        )
        .unwrap();

        let info = resolve_info(Some(folder.join("app_config.json")));
        assert!(info.config_present);
        assert_eq!(info.model, Some(PathBuf::from("C:/models/ggml-tiny.bin")));
        assert_eq!(info.language, "ar");
        assert_eq!(info.transcripts_dir, transcripts);

        fs::remove_dir_all(&folder).unwrap();
    }

    #[test]
    fn missing_config_falls_back_to_arabic_and_documents_sada() {
        let folder = scratch("empty-config");
        let info = resolve_info(Some(folder.join("app_config.json")));
        assert!(!info.config_present);
        assert_eq!(info.language, "ar");
        assert!(info.transcripts_dir.ends_with("Sada"));
        fs::remove_dir_all(&folder).unwrap();
    }

    #[test]
    fn transcribe_explains_a_missing_model_instead_of_spawning_the_engine() {
        let folder = scratch("no-model");
        fs::write(folder.join("app_config.json"), json!({"model.path": ""}).to_string()).unwrap();
        let audio = folder.join("clip.mp3");
        fs::write(&audio, b"not really audio").unwrap();

        let error = call_tool("sada_transcribe", &json!({ "path": audio }), &mut ctx(&folder))
            .expect_err("must fail before starting the engine");
        assert!(error.contains("No model is configured"), "unexpected error: {error}");

        fs::remove_dir_all(&folder).unwrap();
    }

    #[test]
    fn transcribe_rejects_urls_and_missing_files() {
        let folder = scratch("bad-path");
        fs::write(folder.join("app_config.json"), "{}").unwrap();
        let mut context = ctx(&folder);

        let url = call_tool(
            "sada_transcribe",
            &json!({ "path": "https://example.com/a.mp3" }),
            &mut context,
        )
        .expect_err("URLs must be rejected");
        assert!(url.contains("Only local files"));

        let missing = call_tool(
            "sada_transcribe",
            &json!({ "path": folder.join("absent.wav") }),
            &mut context,
        )
        .expect_err("missing files must be rejected");
        assert!(missing.contains("File not found"));

        fs::remove_dir_all(&folder).unwrap();
    }

    #[test]
    fn read_transcript_renders_the_newest_saved_record() {
        let folder = scratch("read");
        let projects = folder.join("Sada");
        let project = projects.join("standup-20261116-140000");
        fs::create_dir_all(&project).unwrap();
        fs::write(
            project.join("transcript.vibe.json"),
            json!({
                "version": 1,
                "name": "standup",
                "createdAt": "2026-11-16T14:00:00Z",
                "language": "ar",
                "segments": [
                    { "start": 0, "stop": 1234, "text": "مرحبا بالجميع" },
                    { "start": 1300, "stop": 2500, "text": "نبدأ الآن" },
                ],
            })
            .to_string(),
        )
        .unwrap();
        fs::write(
            folder.join("app_config.json"),
            json!({ "transcription.projectsPath": projects }).to_string(),
        )
        .unwrap();

        let text = call_tool("sada_transcript", &json!({}), &mut ctx(&folder)).expect("read newest");
        assert!(text.contains("# standup"));
        assert!(text.contains("مرحبا بالجميع"));
        assert!(text.contains("نبدأ الآن"));

        let timed = call_tool(
            "sada_transcript",
            &json!({ "timestamps": true }),
            &mut ctx(&folder),
        )
        .expect("read with timecodes");
        assert!(timed.contains("[00:00:00.000 --> 00:00:12.340] مرحبا بالجميع"));

        let listed = call_tool("sada_transcripts", &json!({}), &mut ctx(&folder)).expect("list");
        assert!(listed.contains("standup"));

        fs::remove_dir_all(&folder).unwrap();
    }

    #[test]
    fn info_reports_arabic_first_and_the_four_tools() {
        let folder = scratch("info");
        fs::write(folder.join("app_config.json"), "{}").unwrap();
        let text = call_tool("sada_info", &json!({}), &mut ctx(&folder)).expect("info");
        let info: serde_json::Value = serde_json::from_str(&text).expect("info is JSON");
        assert_eq!(info["app"], "Sada");
        assert_eq!(info["arabic_first"], true);
        assert_eq!(info["tools"].as_array().map(Vec::len), Some(4));
        assert!(info["config_path"].as_str().is_some_and(|path| path.ends_with("app_config.json")));
        fs::remove_dir_all(&folder).unwrap();
    }
}
