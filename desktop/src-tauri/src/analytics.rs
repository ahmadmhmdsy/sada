//! Analytics is compiled out of this fork.
//!
//! The promise of the Arabic-first build is that a recording never leaves the machine, so the
//! phone-home module is not merely switched off at runtime: the Aptabase plugin, its build-time
//! keys and its capability are gone from the dependency graph and from the webview. The function
//! surface is kept so the rest of the code — which reports lifecycle events — needs no edits;
//! every one of those calls is a no-op in this build.

use std::time::Duration;

use tauri::{App, AppHandle};

pub const APTABASE_APP_KEY: &str = "";
pub const APTABASE_BASE_URL: &str = "";

pub mod events {
    pub const APP_STARTED: &str = "app_started";
    pub const APP_EXITED: &str = "app_exited";
    pub const CLI_STARTED: &str = "cli_started";
    pub const CLI_FINISHED: &str = "cli_finished";
    pub const CLI_SPAWN_FAILED: &str = "cli_spawn_failed";
    pub const SERVER_SPAWN_FAILED: &str = "sona_spawn_failed";
    pub const SERVER_CPU_BASELINE_FALLBACK: &str = "server_cpu_baseline_fallback";

    pub const HANDOFF_ENABLED: &str = "handoff_enabled";
    pub const HANDOFF_DISABLED: &str = "handoff_disabled";
    pub const HANDOFF_TRANSCRIBE: &str = "handoff_transcribe";
    pub const HANDOFF_CAPABILITIES: &str = "handoff_capabilities";
    pub const HANDOFF_PAIRING_REGENERATED: &str = "handoff_pairing_regenerated";
}

pub fn is_aptabase_configured() -> bool {
    false
}

pub fn flush_events_bounded(_app_handle: &AppHandle, _timeout: Duration) {}

pub fn track_event(_app: &App, _event_name: &str) {}

pub fn track_event_handle(_app_handle: &AppHandle, _event_name: &str) {}

pub fn track_event_handle_with_props(
    _app_handle: &AppHandle,
    _event_name: &str,
    _props: Option<serde_json::Value>,
) {
}
