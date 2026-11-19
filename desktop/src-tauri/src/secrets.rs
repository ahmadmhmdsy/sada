//! DPAPI (Windows Data Protection API) helpers for user secrets at rest.
//!
//! Claude/OpenAI API keys used to sit in clear text in app_config.json. They are now stored as
//! opaque DPAPI blobs that only the Windows account that wrote them can decrypt, so a copied
//! profile folder or a roaming backup does not leak the keys. DPAPI is called through the
//! crypt32 exports directly to keep the build free of extra crates; on non-Windows targets the
//! commands fail closed instead of silently storing plaintext.

use eyre::{bail, eyre, Result};

/// DPAPI flag: refuse to show a UI prompt from a background call.
#[cfg(windows)]
const CRYPTPROTECT_UI_FORBIDDEN: u32 = 0x1;

#[cfg(windows)]
mod ffi {
    use std::ffi::c_void;

    #[repr(C)]
    pub struct DataBlob {
        pub cb_data: u32,
        pub pb_data: *mut u8,
    }

    #[link(name = "crypt32")]
    extern "system" {
        pub fn CryptProtectData(
            data_in: *const DataBlob,
            data_descr: *const u16,
            optional_entropy: *const DataBlob,
            reserved: *const c_void,
            prompt: *const c_void,
            flags: u32,
            data_out: *mut DataBlob,
        ) -> i32;
        pub fn CryptUnprotectData(
            data_in: *const DataBlob,
            data_descr: *mut *mut u16,
            optional_entropy: *const DataBlob,
            reserved: *const c_void,
            prompt: *const c_void,
            flags: u32,
            data_out: *mut DataBlob,
        ) -> i32;
    }

    #[link(name = "kernel32")]
    extern "system" {
        pub fn LocalFree(memory: *mut c_void) -> *mut c_void;
    }
}

/// Encrypt bytes for the current Windows user. The blob is safe to store as text (hex).
#[cfg(windows)]
pub fn protect(data: &[u8]) -> Result<Vec<u8>> {
    use ffi::*;
    use std::ptr::{null, null_mut};

    let input = DataBlob { cb_data: data.len() as u32, pb_data: data.as_ptr() as *mut u8 };
    let mut output = DataBlob { cb_data: 0, pb_data: null_mut() };
    let ok = unsafe {
        CryptProtectData(
            &input,
            null(),
            null(),
            null(),
            null(),
            CRYPTPROTECT_UI_FORBIDDEN,
            &mut output,
        )
    };
    if ok == 0 {
        return Err(eyre!("CryptProtectData failed: {}", std::io::Error::last_os_error()));
    }
    let safe = unsafe { std::slice::from_raw_parts(output.pb_data, output.cb_data as usize) }.to_vec();
    unsafe {
        LocalFree(output.pb_data as *mut std::ffi::c_void);
    }
    Ok(safe)
}

/// Decrypt a blob produced by protect on the same Windows user and machine.
#[cfg(windows)]
pub fn unprotect(data: &[u8]) -> Result<Vec<u8>> {
    use ffi::*;
    use std::ptr::{null, null_mut};

    let input = DataBlob { cb_data: data.len() as u32, pb_data: data.as_ptr() as *mut u8 };
    let mut output = DataBlob { cb_data: 0, pb_data: null_mut() };
    let ok = unsafe {
        CryptUnprotectData(
            &input,
            null_mut(),
            null(),
            null(),
            null(),
            CRYPTPROTECT_UI_FORBIDDEN,
            &mut output,
        )
    };
    if ok == 0 {
        return Err(eyre!("CryptUnprotectData failed: {}", std::io::Error::last_os_error()));
    }
    let safe = unsafe { std::slice::from_raw_parts(output.pb_data, output.cb_data as usize) }.to_vec();
    unsafe {
        LocalFree(output.pb_data as *mut std::ffi::c_void);
    }
    Ok(safe)
}

#[cfg(not(windows))]
pub fn protect(_data: &[u8]) -> Result<Vec<u8>> {
    bail!("DPAPI is only available on Windows");
}

#[cfg(not(windows))]
pub fn unprotect(_data: &[u8]) -> Result<Vec<u8>> {
    bail!("DPAPI is only available on Windows");
}

/// Encrypt a UTF-8 secret and return it as lowercase hex, the form stored in app_config.json.
#[tauri::command]
pub fn protect_secret(value: String) -> Result<String, String> {
    protect(value.as_bytes()).map(hex::encode).map_err(|error| error.to_string())
}

/// Decrypt a hex-encoded DPAPI blob back to UTF-8.
#[tauri::command]
pub fn unprotect_secret(value: String) -> Result<String, String> {
    let bytes = hex::decode(value.trim()).map_err(|_| "saved secret is not valid hex".to_string())?;
    let plain = unprotect(&bytes).map_err(|error| error.to_string())?;
    String::from_utf8(plain).map_err(|_| "saved secret is not valid UTF-8".to_string())
}

#[cfg(all(test, windows))]
mod tests {
    use super::*;

    #[test]
    fn round_trips_ascii_and_arabic_secrets() {
        for secret in ["sk-test-1234567890", "مفتاح-سري-عربي"] {
            let blob = protect(secret.as_bytes()).unwrap();
            assert_ne!(blob, secret.as_bytes(), "ciphertext must differ from plaintext");
            assert_eq!(unprotect(&blob).unwrap(), secret.as_bytes());
        }
    }

    #[test]
    fn same_plaintext_produces_different_blobs() {
        // DPAPI mixes in a random IV, so identical keys never produce identical files.
        let first = protect(b"same-key").unwrap();
        let second = protect(b"same-key").unwrap();
        assert_ne!(first, second);
    }

    #[test]
    fn rejects_tampered_ciphertext() {
        let mut blob = protect(b"hello").unwrap();
        blob[0] ^= 0xff;
        assert!(unprotect(&blob).is_err());
    }

    #[test]
    fn command_round_trip_uses_hex() {
        let encrypted = protect_secret("sk-abc".to_string()).unwrap();
        assert!(encrypted.chars().all(|c| c.is_ascii_hexdigit()));
        assert_eq!(unprotect_secret(encrypted).unwrap(), "sk-abc");
    }

    #[test]
    fn rejects_non_hex_secret() {
        assert!(unprotect_secret("not-hex".to_string()).is_err());
    }
}
