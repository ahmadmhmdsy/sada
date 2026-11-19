//! Transcript retention: delete only the app's own transcript files older than N days.
//!
//! The purge is deliberately narrow. It walks the configured transcripts folder and removes:
//! - project folders that contain the app's transcript.vibe.json marker,
//! - legacy flat <name>.vibe.json transcript files.
//! Anything else in the folder (audio the user moved there, exports, notes) is left untouched.
//! Audio lives inside a project folder and is deleted with it, which is what a retention policy
//! means for the app's own store; exports written elsewhere are never reached from here.

use serde::Serialize;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

pub const TRANSCRIPT_FILENAME: &str = "transcript.vibe.json";
pub const TRANSCRIPT_EXTENSION: &str = ".vibe.json";

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PurgeResult {
    pub deleted: u32,
    pub freed_bytes: u64,
    pub cutoff_days: u32,
}

fn older_than(modified: SystemTime, cutoff: SystemTime) -> bool {
    match cutoff.duration_since(modified) {
        Ok(age) => age > Duration::ZERO,
        // A timestamp in the future (clock skew) is not old; never delete on it.
        Err(_) => false,
    }
}

fn dir_size(path: &Path) -> u64 {
    let Ok(entries) = std::fs::read_dir(path) else { return 0 };
    entries
        .filter_map(Result::ok)
        .map(|entry| match entry.file_type() {
            Ok(file_type) if file_type.is_dir() => dir_size(&entry.path()),
            Ok(file_type) if file_type.is_file() => entry.metadata().map(|meta| meta.len()).unwrap_or(0),
            _ => 0,
        })
        .sum()
}

/// Purge transcript files older than days. days == 0 disables purging.
pub fn purge(root: &Path, days: u32, now: SystemTime) -> Result<PurgeResult, String> {
    let mut result = PurgeResult { deleted: 0, freed_bytes: 0, cutoff_days: days };
    if days == 0 {
        return Ok(result);
    }
    if !root.is_dir() {
        return Ok(result);
    }
    let cutoff = now.checked_sub(Duration::from_secs(u64::from(days) * 24 * 60 * 60)).ok_or_else(|| "retention window is too large".to_string())?;

    let entries = std::fs::read_dir(root).map_err(|error| format!("cannot read transcripts folder: {error}"))?;
    for entry in entries.filter_map(Result::ok) {
        let path = entry.path();
        let Ok(file_type) = entry.file_type() else { continue };
        // Never follow a symlink/junction out of the transcripts folder.
        if file_type.is_symlink() {
            continue;
        }
        if file_type.is_dir() {
            let marker = path.join(TRANSCRIPT_FILENAME);
            let Ok(meta) = std::fs::metadata(&marker) else { continue };
            if !meta.is_file() {
                continue;
            }
            let Ok(modified) = meta.modified() else { continue };
            if !older_than(modified, cutoff) {
                continue;
            }
            let size = dir_size(&path);
            if std::fs::remove_dir_all(&path).is_ok() {
                result.deleted += 1;
                result.freed_bytes += size;
            }
        } else if file_type.is_file() {
            let name = path.file_name().and_then(|name| name.to_str()).unwrap_or_default();
            if !name.ends_with(TRANSCRIPT_EXTENSION) || name.ends_with(".part") {
                continue;
            }
            let Ok(meta) = std::fs::metadata(&path) else { continue };
            let Ok(modified) = meta.modified() else { continue };
            if !older_than(modified, cutoff) {
                continue;
            }
            if std::fs::remove_file(&path).is_ok() {
                result.deleted += 1;
                result.freed_bytes += meta.len();
            }
        }
    }
    Ok(result)
}

/// Tauri entry point. The parent passes the effective transcripts folder and retention days from
/// the same settings the app uses, so managed-policy overrides are respected.
#[tauri::command]
pub fn purge_old_transcripts(dir: String, days: u32) -> Result<PurgeResult, String> {
    let root = PathBuf::from(&dir);
    if dir.trim().is_empty() {
        return Err("transcripts folder is empty".to_string());
    }
    let result = purge(&root, days, SystemTime::now())?;
    if result.deleted > 0 {
        tracing::info!(
            deleted = result.deleted,
            freed_bytes = result.freed_bytes,
            days,
            "purged old transcripts"
        );
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp_root(name: &str) -> PathBuf {
        let root = std::env::temp_dir().join(format!("sada-retention-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(&root).unwrap();
        root
    }

    fn project(root: &Path, name: &str) {
        let dir = root.join(name);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join(TRANSCRIPT_FILENAME), "{}").unwrap();
        std::fs::write(dir.join("audio.wav"), vec![0u8; 32]).unwrap();
    }

    #[test]
    fn zero_days_keeps_everything() {
        let root = temp_root("zero");
        project(&root, "keep-me");
        let result = purge(&root, 0, SystemTime::now()).unwrap();
        assert_eq!(result.deleted, 0);
        assert!(root.join("keep-me").exists());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn huge_window_keeps_recent_transcripts() {
        let root = temp_root("recent");
        project(&root, "recent");
        let result = purge(&root, 3650, SystemTime::now()).unwrap();
        assert_eq!(result.deleted, 0);
        assert!(root.join("recent").exists());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn deletes_projects_once_the_cutoff_passes() {
        let root = temp_root("past");
        project(&root, "old-project");
        let now = SystemTime::now();
        let result = purge(&root, 1, now + Duration::from_secs(3 * 24 * 60 * 60)).unwrap();
        assert_eq!(result.deleted, 1);
        assert!(result.freed_bytes >= 32);
        assert!(!root.join("old-project").exists());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn leaves_foreign_files_and_folders_alone() {
        let root = temp_root("foreign");
        project(&root, "old-project");
        std::fs::create_dir_all(root.join("my-notes")).unwrap();
        std::fs::write(root.join("my-notes").join("audio.mp3"), vec![7u8; 64]).unwrap();
        std::fs::write(root.join("export.txt"), b"keep").unwrap();
        std::fs::write(root.join("loose.vibe.json"), b"legacy").unwrap();
        let now = SystemTime::now();
        let result = purge(&root, 1, now + Duration::from_secs(3 * 24 * 60 * 60)).unwrap();
        // Project folder + legacy transcript are the app's own store; notes and exports are not.
        assert_eq!(result.deleted, 2);
        assert!(root.join("my-notes").exists());
        assert!(root.join("export.txt").exists());
        assert!(!root.join("loose.vibe.json").exists());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn missing_folder_is_not_an_error() {
        let missing = std::env::temp_dir().join("sada-retention-does-not-exist");
        let result = purge(&missing, 30, SystemTime::now()).unwrap();
        assert_eq!(result.deleted, 0);
    }

    #[test]
    fn empty_folder_returns_empty_result() {
        let root = temp_root("empty");
        let result = purge(&root, 30, SystemTime::now()).unwrap();
        assert_eq!(result, PurgeResult { deleted: 0, freed_bytes: 0, cutoff_days: 30 });
        std::fs::remove_dir_all(&root).unwrap();
    }
}
