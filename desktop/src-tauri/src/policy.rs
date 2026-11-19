//! Machine-wide managed policy for managed PCs.
//!
//! An administrator (GPO, Intune, SCCM, or a plain registry script) writes values under
//! HKEY_LOCAL_MACHINE\SOFTWARE\Sada\Policy. The app reads them on every decision that could
//! reach the network or degrade offline-only operation, so a policy change takes effect without
//! reinstalling or restarting (the next guarded action sees it).
//!
//! A JSON file is also supported for testing and for deployments that prefer files over the
//! registry: set SADA_POLICY_PATH to the file path, or place the file at
//! %ProgramData%\Sada\policy.json. Registry values win when both exist.
//!
//! This module is deliberately dependency-free beyond serde/winreg so it can be unit-tested on a
//! machine with no policy configured.

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Registry path (under HKEY_LOCAL_MACHINE) that an administrator writes.
pub const POLICY_REGISTRY_PATH: &str = r"SOFTWARE\Sada\Policy";

/// Environment variable that points at a JSON policy file instead of the registry.
pub const POLICY_ENV: &str = "SADA_POLICY_PATH";

pub const VALUE_OFFLINE_MODE: &str = "OfflineMode";
pub const VALUE_DISABLE_AI: &str = "DisableAi";
pub const VALUE_DISABLE_URL_IMPORT: &str = "DisableUrlImport";
pub const VALUE_DISABLE_MODEL_DOWNLOADS: &str = "DisableModelDownloads";
pub const VALUE_TRANSCRIPTS_DIR: &str = "TranscriptsDir";

/// Effective restrictions for this machine. Every field defaults to false / unset so a machine
/// without policy behaves exactly like an unmanaged install.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default)]
pub struct ManagedPolicy {
    /// No feature may contact the network. Implies every other disable flag below.
    pub offline_mode: bool,
    /// Hide and refuse AI providers (Claude, OpenAI, Ollama) and the AI settings page.
    pub disable_ai: bool,
    /// Hide and refuse the URL import tab / yt-dlp binary and media downloads.
    pub disable_url_import: bool,
    /// Hide and refuse model downloads from the model catalog and the download deep link.
    pub disable_model_downloads: bool,
    /// When set, transcripts are written here and cannot be changed in Settings.
    pub transcripts_dir: Option<String>,
}

impl ManagedPolicy {
    /// AI providers are unreachable when AI is disabled or the machine is fully offline.
    #[allow(dead_code)]
    pub fn ai_disabled(&self) -> bool {
        self.offline_mode || self.disable_ai
    }

    /// URL import is unavailable when it is disabled or the machine is fully offline.
    pub fn url_import_disabled(&self) -> bool {
        self.offline_mode || self.disable_url_import
    }

    /// Model downloads are unavailable when disabled or the machine is fully offline.
    pub fn model_downloads_disabled(&self) -> bool {
        self.offline_mode || self.disable_model_downloads
    }

    /// Phone handoff needs the network, so offline mode always turns it off.
    pub fn handoff_disabled(&self) -> bool {
        true
    }

    /// Whether anything at all is managed, used by the UI to show the "managed by your
    /// organization" note once instead of scattering hints.
    #[allow(dead_code)]
    pub fn any_restriction(&self) -> bool {
        self.offline_mode
            || self.disable_ai
            || self.disable_url_import
            || self.disable_model_downloads
            || self.transcripts_dir.as_deref().is_some_and(|value| !value.trim().is_empty())
    }

    /// Transcripts directory after trimming; empty values are treated as unset.
    pub fn transcripts_dir(&self) -> Option<&str> {
        self.transcripts_dir
            .as_deref()
            .map(str::trim)
            .filter(|value| !value.is_empty())
    }

    /// Merge with a lower-priority source (registry beats the JSON file): booleans OR together
    /// so neither source can switch a restriction off, and the higher-priority path wins.
    pub fn merge(self, lower: ManagedPolicy) -> ManagedPolicy {
        ManagedPolicy {
            offline_mode: self.offline_mode || lower.offline_mode,
            disable_ai: self.disable_ai || lower.disable_ai,
            disable_url_import: self.disable_url_import || lower.disable_url_import,
            disable_model_downloads: self.disable_model_downloads || lower.disable_model_downloads,
            transcripts_dir: self.transcripts_dir.or(lower.transcripts_dir),
        }
    }
}

/// The JSON policy file path: SADA_POLICY_PATH when set, otherwise %ProgramData%\Sada\policy.json.
pub fn policy_file_path() -> PathBuf {
    if let Some(path) = std::env::var_os(POLICY_ENV) {
        return PathBuf::from(path);
    }
    let program_data = std::env::var_os("PROGRAMDATA").map(PathBuf::from).unwrap_or_else(|| PathBuf::from(r"C:\ProgramData"));
    program_data.join("Sada").join("policy.json")
}

/// Parse a JSON policy. Unknown fields are ignored so a newer policy schema cannot break an older
/// app, and a malformed file is treated as "no policy" rather than blocking the app.
pub fn parse_policy(json: &str) -> ManagedPolicy {
    serde_json::from_str(json).unwrap_or_default()
}

/// Read the optional JSON policy file, tolerating a missing or unreadable file.
pub fn load_file(path: &std::path::Path) -> ManagedPolicy {
    match std::fs::read_to_string(path) {
        Ok(json) => parse_policy(&json),
        Err(_) => ManagedPolicy::default(),
    }
}

/// Read policy values from the registry. Missing key or values mean unmanaged; a value that is not
/// a DWORD is also ignored rather than guessed at.
#[cfg(windows)]
fn load_registry() -> ManagedPolicy {
    use winreg::enums::HKEY_LOCAL_MACHINE;
    use winreg::RegKey;

    let Ok(key) = RegKey::predef(HKEY_LOCAL_MACHINE).open_subkey(POLICY_REGISTRY_PATH) else {
        return ManagedPolicy::default();
    };

    fn dword(key: &RegKey, name: &str) -> Option<bool> {
        key.get_value::<u32, _>(name).ok().map(|value| value != 0)
    }

    let transcripts_dir = key
        .get_value::<String, _>(VALUE_TRANSCRIPTS_DIR)
        .ok()
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty());

    ManagedPolicy {
        offline_mode: dword(&key, VALUE_OFFLINE_MODE).unwrap_or(false),
        disable_ai: dword(&key, VALUE_DISABLE_AI).unwrap_or(false),
        disable_url_import: dword(&key, VALUE_DISABLE_URL_IMPORT).unwrap_or(false),
        disable_model_downloads: dword(&key, VALUE_DISABLE_MODEL_DOWNLOADS).unwrap_or(false),
        transcripts_dir,
    }
}

#[cfg(not(windows))]
fn load_registry() -> ManagedPolicy {
    ManagedPolicy::default()
}

/// The effective policy for this machine: registry values OR-ed with the JSON file.
pub fn load() -> ManagedPolicy {
    let from_registry = load_registry();
    let from_file = load_file(&policy_file_path());
    from_registry.merge(from_file)
}

/// Exposed to the webview once at boot; the UI hides guarded features from this snapshot.
#[tauri::command]
pub fn get_managed_policy() -> ManagedPolicy {
    let policy = load();
    tracing::debug!(
        offline_mode = policy.offline_mode,
        disable_ai = policy.disable_ai,
        disable_url_import = policy.disable_url_import,
        disable_model_downloads = policy.disable_model_downloads,
        transcripts_dir = policy.transcripts_dir().unwrap_or(""),
        "managed policy loaded"
    );
    policy
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_policy_means_everything_enabled() {
        let policy = parse_policy("{}");
        assert_eq!(policy, ManagedPolicy::default());
        assert!(!policy.any_restriction());
        assert!(!policy.ai_disabled());
        assert!(!policy.url_import_disabled());
        assert!(!policy.model_downloads_disabled());
        assert_eq!(policy.transcripts_dir(), None);
    }

    #[test]
    fn camel_case_json_fields_are_parsed() {
        let policy = parse_policy(
            r#"{"offlineMode": true, "disableAi": true, "disableUrlImport": true, "disableModelDownloads": true, "transcriptsDir": " D:\\Transcripts "}"#,
        );
        assert!(policy.offline_mode);
        assert!(policy.disable_ai);
        assert!(policy.disable_url_import);
        assert!(policy.disable_model_downloads);
        assert_eq!(policy.transcripts_dir(), Some(r"D:\Transcripts"));
        assert!(policy.any_restriction());
    }

    #[test]
    fn offline_mode_implies_every_network_guard() {
        let policy = ManagedPolicy { offline_mode: true, ..ManagedPolicy::default() };
        assert!(policy.ai_disabled());
        assert!(policy.url_import_disabled());
        assert!(policy.model_downloads_disabled());
        assert!(policy.handoff_disabled());
    }

    #[test]
    fn phase_flags_do_not_leak_into_each_other() {
        let policy = ManagedPolicy { disable_ai: true, ..ManagedPolicy::default() };
        assert!(policy.ai_disabled());
        assert!(!policy.url_import_disabled());
        assert!(!policy.model_downloads_disabled());
    }

    #[test]
    fn blank_transcripts_dir_is_unset() {
        let policy = parse_policy(r#"{"transcriptsDir": "   "}"#);
        assert_eq!(policy.transcripts_dir(), None);
        assert!(!policy.any_restriction());
    }

    #[test]
    fn malformed_policy_is_ignored() {
        assert_eq!(parse_policy("not json"), ManagedPolicy::default());
        assert_eq!(parse_policy(r#"{"offlineMode": "yes"}"#), ManagedPolicy::default());
        assert_eq!(parse_policy(r#"{"unknownFutureField": 1}"#), ManagedPolicy::default());
    }

    #[test]
    fn merge_or_combines_restrictions_and_keeps_high_priority_path() {
        let registry = ManagedPolicy { disable_ai: true, transcripts_dir: Some("R:\\".into()), ..ManagedPolicy::default() };
        let file = ManagedPolicy {
            disable_url_import: true,
            transcripts_dir: Some("F:\\".into()),
            ..ManagedPolicy::default()
        };
        let merged = registry.merge(file);
        assert!(merged.disable_ai);
        assert!(merged.disable_url_import);
        assert_eq!(merged.transcripts_dir(), Some("R:\\"));
    }

    #[test]
    fn merging_never_switches_a_restriction_off() {
        let enabled = ManagedPolicy { offline_mode: true, ..ManagedPolicy::default() };
        let merged = enabled.merge(ManagedPolicy::default());
        assert!(merged.offline_mode);
    }
}
