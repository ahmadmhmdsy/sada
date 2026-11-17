//! What the selected model can do, read without starting the HTTP server.
//!
//! The GUI asks `POST /v1/models/metadata` because it already runs the engine
//! server. MCP is headless and must never open a port, so it reads the same GGUF
//! metadata keys the engine reads and mirrors the engine's capability table.
//! Whisper files are not GGUF and keep the historical Whisper behaviour.
//!
//! Everything here is pure file parsing plus two small mappings (language and
//! VAD location), so the whole module is covered by unit tests.

use std::fs::File;
use std::io::{BufReader, Read};
use std::path::{Path, PathBuf};

/// Silero VAD file name, kept in sync with `lib/config.ts` and `handoff/transcribe.rs`.
pub const VAD_MODEL_FILENAME: &str = "ggml-silero-v6.2.0.bin";

/// Parakeet v3 ships no `general.languages` list; the engine falls back to this
/// fixed list (ported from `server/crates/parakeet-rs/src/load.rs`).
const PARAKEET_V3_LANGUAGES: &[&str] = &[
    "bg", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "de", "el", "hu", "it", "lv", "lt", "mt", "pl", "pt", "ro",
    "ru", "sk", "sl", "es", "sv", "uk",
];

const GGUF_MAGIC: &[u8; 4] = b"GGUF";
/// A malformed length field must not allocate gigabytes before the parser gives up.
const MAX_STRING_LEN: u64 = 16 * 1024 * 1024;
const MAX_ARRAY_LEN: u64 = 1_000_000;

/// Which inference engine will load the file.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EngineKind {
    Whisper,
    Nemotron,
    Parakeet,
}

impl EngineKind {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Whisper => "whisper",
            Self::Nemotron => "nemotron",
            Self::Parakeet => "parakeet",
        }
    }
}

/// The subset of the engine's `EngineCapabilities` the CLI needs.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ModelCaps {
    pub engine: EngineKind,
    pub requires_vad: bool,
    /// Advertised language codes; empty for Whisper, which accepts any base code.
    pub languages: Vec<String>,
    pub language_detection: bool,
    pub translation: bool,
    pub text_prompts: bool,
}

/// One resolved `--language` argument.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LanguageChoice {
    Detect,
    Code(String),
}

/// Read the model's capabilities the same way the engine's metadata endpoint does.
pub fn model_caps(path: &Path) -> Result<ModelCaps, String> {
    if !is_gguf(path) {
        return Ok(ModelCaps {
            engine: EngineKind::Whisper,
            requires_vad: false,
            languages: Vec::new(),
            language_detection: true,
            translation: true,
            text_prompts: true,
        });
    }

    let meta = read_gguf_meta(path).map_err(|error| {
        format!("Could not read the model's GGUF metadata from {}: {error}", path.display())
    })?;
    let architecture = meta.architecture.ok_or_else(|| {
        format!("{} is a GGUF file without a `general.architecture` key", path.display())
    })?;
    let head_kind = meta.head_kind.clone().unwrap_or_default();
    let variant = meta.variant.clone().unwrap_or_default();
    let head_kind = head_kind.to_ascii_lowercase();
    let variant_lower = variant.to_ascii_lowercase();

    // Both GGUF engines use general.architecture = parakeet; the head separates them. An
    // absent head falls to Parakeet v3 because its fixed language list is the safer guess, and
    // the engine loads exactly these two families, so no parakeet file is rejected here.
    if architecture == "parakeet" {
        if head_kind == "rnnt" || variant_lower.contains("nemotron") {
            return Ok(ModelCaps {
                engine: EngineKind::Nemotron,
                requires_vad: true,
                languages: meta.languages,
                language_detection: meta.language_detection.unwrap_or(false),
                translation: false,
                text_prompts: false,
            });
        }
        let languages = if meta.languages.is_empty() {
            PARAKEET_V3_LANGUAGES.iter().map(|code| (*code).to_string()).collect()
        } else {
            meta.languages
        };
        return Ok(ModelCaps {
            engine: EngineKind::Parakeet,
            requires_vad: true,
            languages,
            language_detection: meta.language_detection.unwrap_or(true),
            translation: false,
            text_prompts: false,
        });
    }
    Err(format!(
        "Unsupported GGUF model: architecture '{architecture}' with head '{head_kind}'. Sada's engine loads Whisper GGML, Parakeet v3 and Nemotron GGUF models."
    ))
}

/// Map the app's configured language onto what this engine accepts.
///
/// Whisper uses two-letter codes; the GGUF engines advertise full codes such as
/// `ar-AR`, so a base match is enough. When the requested code cannot be mapped,
/// language detection is the useful fallback; a model without detection gets the
/// nearest supported language and the caller sees why.
pub fn resolve_language(requested: &str, caps: &ModelCaps) -> Result<LanguageChoice, String> {
    let requested = requested.trim().to_lowercase();
    let wants_detect = matches!(requested.as_str(), "auto" | "detect" | "automatic");
    if wants_detect {
        return Ok(if caps.language_detection {
            LanguageChoice::Detect
        } else if let Some(first) = caps.languages.first() {
            LanguageChoice::Code(first.clone())
        } else {
            LanguageChoice::Detect
        });
    }

    if caps.engine == EngineKind::Whisper {
        let base = requested.split(['-', '_']).next().unwrap_or_default();
        if base.chars().count() == 2 && base.chars().all(|character| character.is_ascii_alphabetic()) {
            return Ok(LanguageChoice::Code(base.to_string()));
        }
        return Err(format!(
            "language must be a two-letter Whisper code such as 'ar' or 'en', or 'auto' to detect. Got: {requested}"
        ));
    }

    if let Some(exact) = caps.languages.iter().find(|code| code.eq_ignore_ascii_case(&requested)) {
        return Ok(LanguageChoice::Code(exact.clone()));
    }
    let requested_base = requested.split(['-', '_']).next().unwrap_or_default();
    let nearest = caps.languages.iter().find(|code| {
        code.eq_ignore_ascii_case(requested_base) || code.split(['-', '_']).next().is_some_and(|base| base.eq_ignore_ascii_case(requested_base))
    });
    if let Some(code) = nearest {
        return Ok(LanguageChoice::Code(code.clone()));
    }
    if caps.language_detection {
        return Ok(LanguageChoice::Detect);
    }
    Err(format!(
        "{} does not support the language '{requested}' and cannot detect it. Supported codes: {}",
        caps.engine.as_str(),
        supported_list(&caps.languages),
    ))
}

/// Locate the Silero VAD file a VAD-requiring model needs, next to the model or in
/// the configured models folder. Returns `None` when the engine does not need one.
pub fn resolve_vad_model(caps: &ModelCaps, model: &Path, models_folder: &Path) -> Result<Option<PathBuf>, String> {
    if !caps.requires_vad {
        return Ok(None);
    }
    let mut candidates: Vec<PathBuf> = Vec::new();
    if let Some(folder) = model.parent() {
        candidates.push(folder.join(VAD_MODEL_FILENAME));
    }
    candidates.push(models_folder.join(VAD_MODEL_FILENAME));
    if let Some(found) = candidates.iter().find(|path| {
        path.metadata().is_ok_and(|metadata| metadata.is_file() && metadata.len() > 0)
    }) {
        return Ok(Some(found.clone()));
    }
    Err(format!(
        "The selected {} model requires Silero VAD, but {} was not found.\n\nOpen Sada -> Settings -> Models and select the model again so the VAD file is downloaded, or save the file next to the model:\n  {}",
        caps.engine.as_str(),
        VAD_MODEL_FILENAME,
        candidates.first().map(|path| path.display().to_string()).unwrap_or_default(),
    ))
}

fn supported_list(languages: &[String]) -> String {
    if languages.is_empty() {
        return "none advertised".to_string();
    }
    const SHOWN: usize = 24;
    let listed = languages.iter().take(SHOWN).cloned().collect::<Vec<_>>().join(", ");
    if languages.len() > SHOWN {
        format!("{listed}, ... ({} total)", languages.len())
    } else {
        listed
    }
}

fn is_gguf(path: &Path) -> bool {
    let mut magic = [0u8; 4];
    File::open(path).is_ok_and(|mut file| file.read_exact(&mut magic).is_ok()) && &magic == GGUF_MAGIC
}

/// The GGUF keys this app cares about. Everything else is skipped unread.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct GgufMeta {
    pub architecture: Option<String>,
    pub variant: Option<String>,
    pub head_kind: Option<String>,
    pub languages: Vec<String>,
    pub language_detection: Option<bool>,
}

pub fn read_gguf_meta(path: &Path) -> Result<GgufMeta, String> {
    let file = File::open(path).map_err(|error| error.to_string())?;
    let mut reader = BufReader::new(file);
    let mut magic = [0u8; 4];
    reader.read_exact(&mut magic).map_err(|error| error.to_string())?;
    if &magic != GGUF_MAGIC {
        return Err("not a GGUF file".to_string());
    }
    let version = read_u32(&mut reader)?;
    if !matches!(version, 2 | 3) {
        return Err(format!("unsupported GGUF version {version}"));
    }
    let _tensor_count = read_u64(&mut reader)?;
    let kv_count = read_u64(&mut reader)?;
    if kv_count > MAX_ARRAY_LEN {
        return Err(format!("implausible metadata count {kv_count}"));
    }

    let mut meta = GgufMeta::default();
    for _ in 0..kv_count {
        let key = read_string(&mut reader)?;
        let value_type = read_u32(&mut reader)?;
        let wanted = matches!(
            key.as_str(),
            "general.architecture" | "stt.variant" | "stt.parakeet.head_kind" | "general.languages" | "stt.capability.lang_detect"
        );
        match value_type {
            7 => {
                let value = read_u8(&mut reader)? != 0;
                if key == "stt.capability.lang_detect" {
                    meta.language_detection = Some(value);
                }
            }
            8 => {
                let value = read_string(&mut reader)?;
                if wanted {
                    match key.as_str() {
                        "general.architecture" => meta.architecture = Some(value),
                        "stt.variant" => meta.variant = Some(value),
                        "stt.parakeet.head_kind" => meta.head_kind = Some(value),
                        _ => {}
                    }
                }
            }
            9 => {
                let element_type = read_u32(&mut reader)?;
                let count = read_u64(&mut reader)?;
                if count > MAX_ARRAY_LEN {
                    return Err(format!("implausible array length {count} for {key}"));
                }
                if key == "general.languages" && element_type == 8 {
                    meta.languages.reserve(count as usize);
                    for _ in 0..count {
                        meta.languages.push(read_string(&mut reader)?);
                    }
                } else {
                    skip_array(&mut reader, element_type, count)?;
                }
            }
            other => skip_scalar(&mut reader, other)?,
        }
    }
    Ok(meta)
}

fn skip_scalar(reader: &mut impl Read, value_type: u32) -> Result<(), String> {
    let size = match value_type {
        0 | 1 | 7 => 1,
        2 | 3 => 2,
        4 | 5 | 6 => 4,
        10 | 11 | 12 => 8,
        other => return Err(format!("unknown GGUF value type {other}")),
    };
    let mut buffer = [0u8; 8];
    reader.read_exact(&mut buffer[..size]).map_err(|error| error.to_string())
}

fn skip_array(reader: &mut impl Read, element_type: u32, count: u64) -> Result<(), String> {
    if element_type == 8 {
        for _ in 0..count {
            let length = read_u64(reader)?;
            skip_bytes(reader, length)?;
        }
        return Ok(());
    }
    let size = match element_type {
        0 | 1 | 7 => 1,
        2 | 3 => 2,
        4 | 5 | 6 => 4,
        10 | 11 | 12 => 8,
        other => return Err(format!("unknown GGUF array element type {other}")),
    };
    skip_bytes(reader, (size as u64).saturating_mul(count))
}

fn skip_bytes(reader: &mut impl Read, count: u64) -> Result<(), String> {
    if count > MAX_STRING_LEN * 64 {
        return Err(format!("implausible byte length {count}"));
    }
    let skipped = std::io::copy(&mut reader.take(count), &mut std::io::sink()).map_err(|error| error.to_string())?;
    if skipped != count {
        return Err("unexpected end of file".to_string());
    }
    Ok(())
}

fn read_u8(reader: &mut impl Read) -> Result<u8, String> {
    let mut buffer = [0u8; 1];
    reader.read_exact(&mut buffer).map_err(|error| error.to_string())?;
    Ok(buffer[0])
}

fn read_u32(reader: &mut impl Read) -> Result<u32, String> {
    let mut buffer = [0u8; 4];
    reader.read_exact(&mut buffer).map_err(|error| error.to_string())?;
    Ok(u32::from_le_bytes(buffer))
}

fn read_u64(reader: &mut impl Read) -> Result<u64, String> {
    let mut buffer = [0u8; 8];
    reader.read_exact(&mut buffer).map_err(|error| error.to_string())?;
    Ok(u64::from_le_bytes(buffer))
}

fn read_string(reader: &mut impl Read) -> Result<String, String> {
    let length = read_u64(reader)?;
    if length > MAX_STRING_LEN {
        return Err(format!("implausible string length {length}"));
    }
    let mut bytes = vec![0u8; length as usize];
    reader.read_exact(&mut bytes).map_err(|error| error.to_string())?;
    String::from_utf8(bytes).map_err(|error| error.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn scratch(name: &str) -> PathBuf {
        let folder = std::env::temp_dir().join(format!("sada-mcp-caps-{name}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&folder);
        fs::create_dir_all(&folder).expect("create scratch folder");
        folder
    }

    /// Build the smallest GGUF file holding the keys a capability probe reads.
    fn gguf_bytes(kv: &[(&str, GgufValue)]) -> Vec<u8> {
        let mut out = Vec::new();
        out.extend_from_slice(GGUF_MAGIC);
        out.extend_from_slice(&3u32.to_le_bytes());
        out.extend_from_slice(&0u64.to_le_bytes());
        out.extend_from_slice(&(kv.len() as u64).to_le_bytes());
        for (key, value) in kv {
            write_string(&mut out, key);
            match value {
                GgufValue::Text(text) => {
                    out.extend_from_slice(&8u32.to_le_bytes());
                    write_string(&mut out, text);
                }
                GgufValue::Bool(flag) => {
                    out.extend_from_slice(&7u32.to_le_bytes());
                    out.push(u8::from(*flag));
                }
                GgufValue::Texts(items) => {
                    out.extend_from_slice(&9u32.to_le_bytes());
                    out.extend_from_slice(&8u32.to_le_bytes());
                    out.extend_from_slice(&(items.len() as u64).to_le_bytes());
                    for item in *items {
                        write_string(&mut out, item);
                    }
                }
            }
        }
        out
    }

    enum GgufValue {
        Text(&'static str),
        Bool(bool),
        Texts(&'static [&'static str]),
    }

    fn write_string(out: &mut Vec<u8>, value: &str) {
        out.extend_from_slice(&(value.len() as u64).to_le_bytes());
        out.extend_from_slice(value.as_bytes());
    }

    fn nemotron_file(folder: &Path, detection: bool) -> PathBuf {
        let path = folder.join("nemotron.gguf");
        fs::write(
            &path,
            gguf_bytes(&[
                ("general.architecture", GgufValue::Text("parakeet")),
                ("stt.variant", GgufValue::Text("nemotron-3.5")),
                ("stt.parakeet.head_kind", GgufValue::Text("rnnt")),
                ("general.languages", GgufValue::Texts(&["ar-AR", "en-US", "fr-FR"])),
                ("stt.capability.lang_detect", GgufValue::Bool(detection)),
                ("stt.parakeet.encoder.n_layers", GgufValue::Bool(true)),
            ]),
        )
        .expect("write GGUF fixture");
        path
    }

    #[test]
    fn whisper_files_keep_the_whisper_capabilities() {
        let folder = scratch("whisper");
        let path = folder.join("ggml-tiny.bin");
        fs::write(&path, b"ggml fixture").unwrap();
        let caps = model_caps(&path).expect("whisper caps");
        assert_eq!(caps.engine, EngineKind::Whisper);
        assert!(!caps.requires_vad);
        assert!(caps.translation && caps.text_prompts && caps.language_detection);
        assert_eq!(
            resolve_language("ar", &caps).expect("arabic"),
            LanguageChoice::Code("ar".to_string())
        );
        assert_eq!(resolve_language("auto", &caps).expect("detect"), LanguageChoice::Detect);
        // A full BCP-47 code degrades to its Whisper base code.
        assert_eq!(
            resolve_language("ar-IQ", &caps).expect("base"),
            LanguageChoice::Code("ar".to_string())
        );
        assert!(resolve_language("arabic", &caps).is_err());
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn nemotron_gguf_reports_vad_and_no_translation() {
        let folder = scratch("nemotron");
        let path = nemotron_file(&folder, true);
        let caps = model_caps(&path).expect("nemotron caps");
        assert_eq!(caps.engine, EngineKind::Nemotron);
        assert!(caps.requires_vad);
        assert!(!caps.translation && !caps.text_prompts);
        assert_eq!(caps.languages, vec!["ar-AR", "en-US", "fr-FR"]);
        assert!(caps.language_detection);
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn languages_map_between_base_and_advertised_codes() {
        let folder = scratch("languages");
        let path = nemotron_file(&folder, false);
        let caps = model_caps(&path).expect("nemotron caps");
        assert_eq!(
            resolve_language("ar", &caps).expect("base maps"),
            LanguageChoice::Code("ar-AR".to_string())
        );
        assert_eq!(
            resolve_language("AR-ar", &caps).expect("case-insensitive"),
            LanguageChoice::Code("ar-AR".to_string())
        );
        assert_eq!(
            resolve_language("en-US", &caps).expect("exact"),
            LanguageChoice::Code("en-US".to_string())
        );
        // Without detection, an unmapped language is a clear error instead of an engine crash.
        let error = resolve_language("ja", &caps).expect_err("unsupported language");
        assert!(error.contains("ar-AR"), "unexpected error: {error}");
        // Detection is only used when advertised.
        assert!(resolve_language("auto", &caps).is_ok());
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn auto_prefers_detection_then_the_first_language() {
        let folder = scratch("auto");
        let detected = nemotron_file(&folder, true);
        let caps = model_caps(&detected).expect("caps");
        assert_eq!(resolve_language("auto", &caps).expect("auto"), LanguageChoice::Detect);
        let undetected = model_caps(&detected).map(|mut caps| {
            caps.language_detection = false;
            caps
        });
        let caps = undetected.expect("caps");
        assert_eq!(
            resolve_language("auto", &caps).expect("auto fallback"),
            LanguageChoice::Code("ar-AR".to_string())
        );
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn parakeet_v3_without_a_variant_uses_the_known_language_list() {
        let folder = scratch("parakeet");
        let path = folder.join("parakeet.gguf");
        fs::write(
            &path,
            gguf_bytes(&[
                ("general.architecture", GgufValue::Text("parakeet")),
                ("parakeet.n_layers", GgufValue::Bool(true)),
            ]),
        )
        .unwrap();
        let caps = model_caps(&path).expect("parakeet caps");
        assert_eq!(caps.engine, EngineKind::Parakeet);
        assert!(caps.requires_vad);
        assert!(caps.languages.iter().any(|code| code == "en"));
        assert!(!caps.languages.iter().any(|code| code == "ar"), "Parakeet v3 has no Arabic");
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn unsupported_gguf_architectures_are_rejected_with_a_readable_message() {
        let folder = scratch("unsupported");
        let path = folder.join("other.gguf");
        fs::write(
            &path,
            gguf_bytes(&[
                ("general.architecture", GgufValue::Text("llama")),
                ("stt.variant", GgufValue::Text("chat")),
            ]),
        )
        .unwrap();
        let error = model_caps(&path).expect_err("must reject");
        assert!(error.contains("Unsupported GGUF"), "unexpected error: {error}");

        let text_path = folder.join("broken.gguf");
        fs::write(&text_path, b"GGUF\xFF\xFF\xFF\xFF").unwrap();
        let error = model_caps(&text_path).expect_err("must reject a truncated header");
        assert!(error.contains("GGUF metadata"), "unexpected error: {error}");
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn vad_is_required_only_for_vad_engines_and_found_next_to_the_model() {
        let folder = scratch("vad");
        let models = folder.join("models");
        fs::create_dir_all(&models).unwrap();
        let model = nemotron_file(&models, false);
        let caps = model_caps(&model).expect("caps");

        let error = resolve_vad_model(&caps, &model, &models).expect_err("missing VAD must fail");
        assert!(error.contains(VAD_MODEL_FILENAME), "unexpected error: {error}");

        let vad = models.join(VAD_MODEL_FILENAME);
        fs::write(&vad, b"vad fixture").unwrap();
        assert_eq!(resolve_vad_model(&caps, &model, &models).expect("found"), Some(vad));

        // A Whisper model never needs one, even when the file is absent.
        let whisper = models.join("ggml-tiny.bin");
        fs::write(&whisper, b"ggml fixture").unwrap();
        let whisper_caps = model_caps(&whisper).expect("whisper caps");
        assert_eq!(resolve_vad_model(&whisper_caps, &whisper, &models).expect("not needed"), None);
        fs::remove_dir_all(folder).unwrap();
    }

    #[test]
    fn a_vad_file_that_was_never_downloaded_counts_as_missing() {
        let folder = scratch("empty-vad");
        let models = folder.join("models");
        fs::create_dir_all(&models).unwrap();
        let model = nemotron_file(&models, false);
        let caps = model_caps(&model).expect("caps");
        let vad = models.join(VAD_MODEL_FILENAME);
        fs::write(&vad, []).unwrap();
        assert!(resolve_vad_model(&caps, &model, &models).is_err(), "zero-byte downloads are not usable");
        fs::remove_dir_all(folder).unwrap();
    }
}
