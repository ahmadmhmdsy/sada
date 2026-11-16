# Verification report — Sada 3.2.2

This page summarises how the Windows build in this repository was verified before its first public
release. It is written in English for reviewers; the Arabic summary follows.

- **Date:** 16 November 2026 (Asia/Baghdad)
- **Source:** commit `f10d2b6` (tree verified before the release; later commits touch docs, CI and the
  site only)
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · AVX2 available
- **Build:** Tauri 2.10.3, sidecar `vibe-server` v0.6.10 (whisper.cpp), FFmpeg 9.0.1 essentials
  (gyan.dev, GPLv3), pnpm 10.4.1, Node 24, Rust stable.

## Artifacts

| Artifact | SHA-256 |
| --- | --- |
| `Sada_3.2.2_x64-setup.exe` (local verification build, 43,914,975 bytes) | `39C327B6D8BB2CE24D78158B47042EEC23565089479C5F128DB5574C9F32FE96` |
| Installed `Sada.exe` (15,770,624 bytes) | `9DB6A8081AE651550001E0B3285B5DF42A49998832BB0A0EB6BD6F0AFF67AC84` |
| Installed `vibe-server.exe` (75,623,424 bytes) | `BCA00C2F91E6056B4A283801C2D57A74AA3A7109A2DADCCA8B4E68D66D89AD76` |

The GitHub release installer is rebuilt by CI from the same source; its hash is recorded in the
release's `SHA256SUMS.txt` and can differ from the local build above because of build paths and
timestamps. Verify whatever file you download against the checksum shipped with it.

## Build

- Frontend: `pnpm build` (paraglide compile → `tsc` → `vite build`), exit 0.
- Desktop: `pnpm exec tauri build`, log ends with `Finished 1 bundle`; NSIS installer produced.
- No binary sidecar or model is committed to git; both are fetched/adopted at build/run time.

## Arabic-first launch

A fresh profile was verified by deleting the application data folders, launching the installed app
and inspecting the running WebView over the DevTools protocol:

- `document.documentElement.lang = "ar-IQ"`, `dir = "rtl"`
- paraglide locale `ar-IQ`; UI copy Arabic; Arabic setup screen with model download progress
- second launch kept Arabic (locale persisted)

Screenshots: [main](media/sada-main.png), [first run](media/sada-first-run.png),
[settings](media/sada-settings.png).

> A real bug was found and fixed here: the hidden `meeting-prompt` window shares localStorage and
> could win a race that reset the locale to English on first paint. The shared default is now
> `ar-IQ` in every window, and the final build was re-verified from a fresh profile.

## Arabic transcription

Transcribed with the shipped engine (same `vibe-server` binary the app uses), Arabic language
setting, `large-v3-turbo` model:

| Clip | Content | Result |
| --- | --- | --- |
| `msa_news` | Modern Standard Arabic news | Accurate transcript; one Latin acronym (`PDF`) misheard as "BDF" |
| `iraqi_dialog` | Iraqi Arabic dialogue | Accurate; dialect understood |
| `silence` | Digital silence | Hallucination (invented phrase) — known Whisper limitation |
| `tech_mix` | Arabic + technical terms | Mixed accuracy on English tech terms |
| `numbers` | Numbers and dates | Correct values, sometimes written as words; occasional duplicate word |

The app's CLI path (`Sada.exe transcribe … -l ar`) exited 0 in the installed build. The transcript
is printed by the sidecar on stdout; the GUI redirect does not produce console output on Windows.

## Arabic PDF

Export produced a real PDF with an embedded IBM Plex Sans Arabic font and correct Arabic shaping;
visual render was checked. Note that automated text extraction (e.g. `pdftotext`) can scramble
intra-word ordering for shaped Arabic even when the visual output is correct.

## Tests

`pnpm test` → **26 test files / 130 tests passed, exit 0**, including:

- Arabic transcript normalization (`arabic-text.test.ts`, 10 tests)
- Arabic PDF font selection and shaping tests
- boot-locale test: no stored language → app boots `ar-IQ`/`rtl`
- existing upstream tests for bidi, PDF, projects and dialogs

## Network

With the app installed and idle, an inspection found only loopback sockets opened by the app's own
IPC; no external endpoint, no telemetry. The updater and analytics code paths are removed from
source.

## Known limitations

- The installer is **not code-signed**; SmartScreen may warn. Verify `SHA256SUMS.txt`.
- Models are **not bundled**; the first run downloads ~1.6GB (or you pick a local `ggml-*.bin`).
- Silence/noise hallucinations; occasional acronym and number normalization gaps.
- PDF text extraction by third-party tools can be imperfect, though the visual PDF is correct.
- The fork ships for Windows only.
- The sidebar switch controls stay on the physical left even in RTL (deliberate layout choice).

Raw logs and screenshots are kept by the maintainer; the files in [docs/media](media/) are the
public copies used in the README and the website.

---

## ملخص عربي

تم التحقق من بناء Windows قبل أول إصدار عام: بناء نظيف من المصدر، ثم تثبيت وفتح من ملف تعريف
نظيف والواجهة عربية RTL فعلاً (`lang=ar-IQ`، `dir=rtl`)، وتفريغ فصحى ولهجة عراقية بمحرّك
التطبيق نفسه، وتصدير PDF عربي بخط مضمّن، واختبارات 130/130 ناجحة، وفحص شبكة عند الخمول يُظهر
loopback فقط. القيود المعلنة: مثبّت غير موقّع، النموذج غير مضمّن (~1.6GB)، هلوسة على الصمت،
وقصور في الأكرونيمات والأرقام، والاستخراج الآلي لنص PDF قد يشوّش داخل الكلمات رغم صحة العرض.
