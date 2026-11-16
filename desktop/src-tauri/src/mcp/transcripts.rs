//! Reading the Sada transcript store from outside the app.
//!
//! The store is a folder of project folders: <name>-<yyyyMMdd-HHmmss>/transcript.vibe.json
//! next to a copy of the audio, plus legacy flat <name>-<yyyyMMdd-HHmmss>.vibe.json files.
//! There is no index, so listing scans the folder and sorts on the stamp in the entry name --
//! mtimes drift when files are copied or renamed, the stamp never does.

use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};

pub(crate) const TRANSCRIPT_FILENAME: &str = "transcript.vibe.json";
pub(crate) const TRANSCRIPT_EXTENSION: &str = ".vibe.json";

/// One stored transcript, as far as listing needs to know it.
#[derive(Debug, Clone)]
pub(crate) struct TranscriptEntry {
    pub(crate) name: String,
    pub(crate) path: PathBuf,
    pub(crate) created_at: Option<String>,
    pub(crate) language: Option<String>,
    pub(crate) audio: Option<PathBuf>,
    pub(crate) preview: String,
    pub(crate) stamp: u64,
}

/// Find every transcript directly in the folder, newest first.
pub(crate) fn scan_transcripts(folder: &Path) -> Result<Vec<TranscriptEntry>, String> {
    if !folder.is_dir() {
        return Err(format!(
            "No transcripts folder at {}.\n\nSave a transcript from Sada first, or pass a folder argument.",
            display_path(folder),
        ));
    }
    let mut entries = Vec::new();
    let read_dir = fs::read_dir(folder)
        .map_err(|error| format!("Could not list {}: {error}", display_path(folder)))?;
    for entry in read_dir.flatten() {
        let entry_path = entry.path();
        let entry_name = entry.file_name().to_string_lossy().into_owned();
        if entry_path.is_dir() {
            let record_path = entry_path.join(TRANSCRIPT_FILENAME);
            if !record_path.is_file() {
                continue;
            }
            let Some(record) = read_record(&record_path)? else {
                continue;
            };
            entries.push(transcript_entry(&entry_name, record_path, &record));
        } else if entry_name.ends_with(TRANSCRIPT_EXTENSION) {
            let Some(record) = read_record(&entry_path)? else {
                continue;
            };
            let name = entry_name.trim_end_matches(TRANSCRIPT_EXTENSION).to_string();
            entries.push(transcript_entry(&name, entry_path, &record));
        }
    }
    entries.sort_by(|left, right| {
        right
            .stamp
            .cmp(&left.stamp)
            .then_with(|| right.created_at.cmp(&left.created_at))
            .then_with(|| right.name.cmp(&left.name))
    });
    Ok(entries)
}

fn transcript_entry(entry_name: &str, path: PathBuf, record: &Value) -> TranscriptEntry {
    let folder = path.parent().map(Path::to_path_buf).unwrap_or_default();
    let name = record
        .get("name")
        .and_then(Value::as_str)
        .filter(|name| !name.trim().is_empty())
        .map(str::to_string)
        .unwrap_or_else(|| display_name(entry_name));
    let audio = record
        .get("audioFile")
        .and_then(Value::as_str)
        .map(|file| folder.join(file))
        .filter(|path| path.is_file())
        .or_else(|| record.get("sourcePath").and_then(Value::as_str).map(PathBuf::from));
    TranscriptEntry {
        name,
        stamp: stamp_from_name(entry_name),
        created_at: record.get("createdAt").and_then(Value::as_str).map(str::to_string),
        language: record.get("language").and_then(Value::as_str).map(str::to_string),
        audio,
        preview: preview_of(record),
        path,
    }
}

/// Accept either a project folder or the record file itself.
pub(crate) fn resolve_record_path(path: &Path) -> Result<PathBuf, String> {
    if path.is_dir() {
        let record = path.join(TRANSCRIPT_FILENAME);
        if record.is_file() {
            return Ok(record);
        }
        return Err(format!("{} is a folder without {TRANSCRIPT_FILENAME}.", display_path(path)));
    }
    if path.is_file() {
        if path.file_name().is_some_and(|name| name.to_string_lossy().ends_with(TRANSCRIPT_EXTENSION)) {
            return Ok(path.to_path_buf());
        }
        return Err(format!(
            "Not a Sada transcript: {}\n\nExpected a {} file or the project folder that holds it.",
            display_path(path),
            TRANSCRIPT_EXTENSION,
        ));
    }
    Err(format!("Transcript not found: {}", display_path(path)))
}

pub(crate) fn read_record(path: &Path) -> Result<Option<Value>, String> {
    let text = match fs::read_to_string(path) {
        Ok(text) => text,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(format!("Could not read {}: {error}", display_path(path))),
    };
    Ok(serde_json::from_str::<Value>(&text).ok().filter(Value::is_object))
}

fn preview_of(record: &Value) -> String {
    let mut preview = String::new();
    if let Some(segments) = record.get("segments").and_then(Value::as_array) {
        for segment in segments {
            let Some(text) = segment.get("text").and_then(Value::as_str) else {
                continue;
            };
            let text = text.trim();
            if text.is_empty() {
                continue;
            }
            if !preview.is_empty() {
                preview.push(' ');
            }
            preview.push_str(text);
            if preview.chars().count() > 160 {
                break;
            }
        }
    }
    let preview: String = preview.chars().take(160).collect();
    if preview.chars().count() >= 160 {
        format!("{preview}...")
    } else {
        preview
    }
}

/// Entry names end in -yyyyMMdd-HHmmss; sorting on that stamp is stable even when files are
/// copied or renamed and mtimes drift.
pub(crate) fn stamp_from_name(name: &str) -> u64 {
    let bytes = name.as_bytes();
    let mut best = 0u64;
    let mut index = 0usize;
    while index + 15 <= bytes.len() {
        let date = &bytes[index..index + 8];
        let time = &bytes[index + 9..index + 15];
        if bytes[index + 8] == b'-'
            && date.iter().all(u8::is_ascii_digit)
            && time.iter().all(u8::is_ascii_digit)
        {
            let mut value = 0u64;
            for byte in date.iter().chain(time.iter()) {
                value = value * 10 + u64::from(byte - b'0');
            }
            best = value;
        }
        index += 1;
    }
    best
}

/// Drop the -yyyyMMdd-HHmmss suffix a project folder or legacy file name carries.
pub(crate) fn display_name(entry_name: &str) -> String {
    let name = entry_name.trim_end_matches(TRANSCRIPT_EXTENSION);
    if name.len() > 15 {
        let split = name.len() - 15;
        let (head, stamp) = name.split_at(split);
        if head.ends_with('-') && stamp_from_name(stamp) > 0 {
            return head.trim_end_matches('-').to_string();
        }
    }
    name.to_string()
}

pub(crate) fn entry_name(path: &Path) -> String {
    path.parent()
        .and_then(Path::file_name)
        .map(|name| name.to_string_lossy().into_owned())
        .unwrap_or_else(|| "transcript".to_string())
}

/// Segments store timestamps as centiseconds; render them as HH:MM:SS.mmm.
pub(crate) fn format_centiseconds(centiseconds: i64) -> String {
    let milliseconds = centiseconds.max(0) * 10;
    let hours = milliseconds / 3_600_000;
    let minutes = (milliseconds % 3_600_000) / 60_000;
    let seconds = (milliseconds % 60_000) / 1_000;
    let millis = milliseconds % 1_000;
    format!("{hours:02}:{minutes:02}:{seconds:02}.{millis:03}")
}

pub(crate) fn display_path(path: &Path) -> String {
    path.display().to_string()
}

#[cfg(test)]
mod tests {
    use super::{display_name, format_centiseconds, scan_transcripts, stamp_from_name};
    use serde_json::json;
    use std::fs;
    use std::path::PathBuf;

    fn scratch(name: &str) -> PathBuf {
        let folder = std::env::temp_dir().join(format!("sada-mcp-{name}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&folder);
        fs::create_dir_all(&folder).expect("create scratch folder");
        folder
    }

    #[test]
    fn stamps_sort_lexicographically_like_the_app() {
        assert_eq!(stamp_from_name("team-standup-20260820-093015"), 20260820093015);
        assert_eq!(stamp_from_name("notes-20260101-000000.vibe.json"), 20260101000000);
        assert_eq!(stamp_from_name("imported-audio"), 0);
        assert!(stamp_from_name("a-20260101-000000") < stamp_from_name("a-20260102-000000"));
    }

    #[test]
    fn display_names_drop_the_stamp_suffix() {
        assert_eq!(display_name("team-standup-20260820-093015"), "team-standup");
        assert_eq!(display_name("notes-20260101-000000.vibe.json"), "notes");
        assert_eq!(display_name("imported"), "imported");
    }

    #[test]
    fn centiseconds_render_as_hms_milliseconds() {
        assert_eq!(format_centiseconds(0), "00:00:00.000");
        assert_eq!(format_centiseconds(12345), "00:02:03.450");
        assert_eq!(format_centiseconds(360_000), "01:00:00.000");
    }

    #[test]
    fn scans_project_folders_and_legacy_files_newest_first() {
        let folder = scratch("scan");
        let projects = folder.join("Sada");
        let older = projects.join("older-20260101-010101");
        let newer = projects.join("newer-20260202-020202");
        fs::create_dir_all(&older).unwrap();
        fs::create_dir_all(&newer).unwrap();
        fs::write(
            older.join("transcript.vibe.json"),
            json!({"version":1,"name":"older","createdAt":"2026-01-01T01:01:01Z","segments":[{"start":0,"stop":100,"text":"First note"}]}).to_string(),
        )
        .unwrap();
        fs::write(
            newer.join("transcript.vibe.json"),
            json!({"version":1,"name":"newer","createdAt":"2026-02-02T02:02:02Z","segments":[{"start":0,"stop":100,"text":"Second note"}]}).to_string(),
        )
        .unwrap();
        fs::write(
            projects.join("legacy-20250101-000000.vibe.json"),
            json!({"version":1,"name":"legacy","segments":[{"start":0,"stop":50,"text":"Old flat save"}]}).to_string(),
        )
        .unwrap();
        fs::write(projects.join("not-a-transcript.txt"), "ignore me").unwrap();

        let entries = scan_transcripts(&projects).expect("scan");
        assert_eq!(entries.len(), 3);
        assert_eq!(entries[0].name, "newer");
        assert_eq!(entries[1].name, "older");
        assert_eq!(entries[2].name, "legacy");
        assert_eq!(entries[0].preview, "Second note");

        fs::remove_dir_all(&folder).unwrap();
    }

    #[test]
    fn scanning_a_missing_folder_explains_how_to_create_one() {
        let folder = scratch("missing");
        let error = scan_transcripts(&folder.join("Sada")).expect_err("must fail");
        assert!(error.contains("No transcripts folder"));
        fs::remove_dir_all(&folder).unwrap();
    }
}
