# Production readiness — Sada 3.8.0

An evidence-based answer to "can we use this, and is it production ready?", written 2026-11-18 for
Sada 3.8.0 on Windows 10/11 x64. It is deliberately unflattering where the evidence is thin: every
claim below links to committed evidence, and every gap is named. If a category is not listed, it was
not assessed.

Related documents: [VERIFICATION.md](VERIFICATION.md) (per-release evidence and hashes),
[ACCEPTANCE.md](ACCEPTANCE.md) (the manual acceptance matrix), [SECURITY.md](../SECURITY.md)
(security model), [SIGNING.md](SIGNING.md) (unsigned status), [P5-PLAN.md](P5-PLAN.md) (what v3.8.0
changed).

## Verdict

| Audience | Verdict | What still blocks a stronger claim |
| --- | --- | --- |
| **Individual / personal use** | **Ready** | Unsigned installer shows a SmartScreen warning; Windows 10 without WebView2 needs the offline installer; some dialects are unmeasured (below). |
| **Small team / office, manual installs** | **Ready with conditions** | Same as above, plus: verify SHA-256 before installing, no central configuration, no automatic updates (by design), no support contract. |
| **Managed / enterprise deployment** | **Not yet** | No code signing, no MSI/GPO deployment packaging, no central update or configuration channel, clean-machine acceptance rows B–E not executed by the maintainer, no support commitment. |
| **Sensitive / regulated data** | **Conditional** | The offline, no-telemetry design is a genuine advantage, but an unsigned binary, plaintext local storage (protected only by the Windows user profile) and the absence of an external security audit must be accepted explicitly. |

In one sentence: **it works today for Arabic transcription on a personal or small-team Windows
machine, offline, with no account and no telemetry; it is not yet a managed-deployment product, and
that is a distribution-and-evidence gap, not a "the app does not work" gap.**

## What "production ready" means here

For this project the bar is: it installs and runs on the target hardware (including offline), Arabic
output is predictable and measured rather than asserted, no data leaves the machine, the release
pipeline is repeatable and checked, upgrades keep user data, and limitations are documented before
users hit them. The categories below test that bar.

## 1. Build and release pipeline — strong

- CI (`.github/workflows/ci.yml`) runs on every push to master and every pull request: frontend
  type-check/build, **193 vitest tests in 31 files**, **101 Rust tests** (app, MCP, Arabic
  normaliser), plus the Python benchmark harness suite. The release workflow
  (`.github/workflows/release.yml`) additionally builds the engine from `server/`, runs the
  **8 loopback request-guard tests**, builds both NSIS installers, and publishes the GitHub release
  only if the tag matches the app version and release notes exist.
- Every published asset is accompanied by `SHA256SUMS.txt` and the three licence files; release
  notes state the exact size and hash. Evidence: [VERIFICATION.md](VERIFICATION.md).
- Pinned inputs: lockfiles, `.server-version` engine pin, vendored FFmpeg sidecar, catalogue
  model hashes. A rebuild is not bit-identical (MSVC/NSIS builds are not reproducible
  byte-for-byte), so the published hash is the reference, not a rebuild.

**Gap:** no supply-chain attestation/SLSA provenance, no signed builds (see below).

## 2. Automated tests — good, with named holes

| Area | Evidence | What it proves |
| --- | --- | --- |
| Frontend/UI logic | 193 vitest tests / 31 files (`cd desktop && pnpm test`) | Arabic text pipeline, PDF layout, settings, transcript state, exports |
| Rust shell | 101 tests (`cd desktop/src-tauri && cargo test --release`) | MCP stdio server, Arabic normaliser, file/URL handling, app commands |
| Engine guard | 8 tests (`cd server && cargo test --release -p vibe-server guard::`) | loopback Host/Origin rejection |
| Benchmark harness | 62 tests (`cd benchmarks/arabic-asr && python -m unittest discover -s tests`) | WER/CER, normalisation, manifest integrity, regression gate |
| i18n | `python scripts/check_i18n.py` | Arabic locale coverage against en-US |
| Type-level | `cargo check --tests` | test-only code in the Rust workspace compiles |

**What is not covered:** there is no automated end-to-end UI test on a clean machine, no
installer-upgrade automation beyond the documented silent-install smoke check, no load test for very
long audio, no fuzzing of media/import parsing, and no automated run of the benchmark (it needs
model weights, so it is a release-checklist step guarded by `sadabench compare`). The
clean-machine acceptance rows B–E are still unexecuted (#17).

## 3. Security and privacy posture — strong design, unsigned binary

Design (see [SECURITY.md](../SECURITY.md)):

- The app is a local Tauri shell; the engine is a bundled sidecar reachable only through a loopback
  connection guarded by a Host/Origin check (unit-tested). No inbound service is exposed.
- The webview runs with a strict CSP and a minimal Tauri capability set; no remote content is
  loaded, and there is no auto-updater, telemetry, account system, analytics or phone relay.
- Model downloads are verified against catalogue SHA-256; imported files stay local; the optional
  summary provider (Claude/Ollama) is off unless the user configures their own key.
- MCP mode is stdio-only: no port, so no firewall rule and no network surface.

**Gaps:** the released binaries are **unsigned** (owner decision 2026-11-18 while the project is
open-source-only; pipeline staged, see [SIGNING.md](SIGNING.md)) — SmartScreen shows an
unknown-publisher warning and tamper evidence relies on the separately published hash. There is no
third-party security audit, and dependency advisories are not scanned in CI (report them through
SECURITY.md).

## 4. Data handling — local and simple, no backup feature

Transcripts, projects, settings and logs live under the user profile
(`%LOCALAPPDATA%\Sada\`); models live in the app's model directory. Nothing is synchronised or
uploaded. Windows user-profile ACLs are the only access control — **there is no encryption at
rest** and no built-in backup/restore. Deleting the app data folder deletes the user's history.
For sensitive audio this is acceptable only if the Windows account is trusted and the disk is
encrypted (BitLocker).

## 5. Arabic accuracy — measured, not perfect, honestly bounded

The committed 90-clip suite (30 MSA + 10 Latin-mixed + 20 Egyptian + 15 Gulf + 15 technical
code-switch) measures the default engine at **30.27% WER / 18.84% CER** (Whisper large-v3-turbo,
word timestamps 100%, 27.3% of Latin names kept, RTF 0.38). Per-slice: MSA 22.09%, Egyptian
11.03%, Gulf 42.74%, technical 46.18%, Latin-mixed 48.96%. Tables, raw transcripts and method:
`benchmarks/arabic-asr/results/results-2026-11-18-v2.json`/`.md`, decisions in
[MODELS-DECISIONS.md](MODELS-DECISIONS.md).

- Conversation/code-switch Arabic is **much harder** than read MSA/Egyptian; the app does not claim
  otherwise, and the recognised term set is limited (`desktop/src/lib/arabic-text.ts`).
- **Iraqi and Levantine are unmeasured** — no commercial-use-permissive corpus with human
  transcripts was found (matrix in [P4-PLAN.md](P4-PLAN.md)). No accuracy claim is made for them.
- 15-clip slices have wide confidence intervals; treat sub-2 pp slice deltas as unresolved.
- From v3.8.0, `sadabench compare` fails a release when a re-run regresses more than 1.0 pp WER
  overall or on any slice, so accuracy cannot silently rot.

## 6. Installation and distribution — usable, with prerequisites

- Per-user NSIS install into `%LOCALAPPDATA%\Sada\`, no administrator rights. Upgrade by running
  the newer installer; user data is kept.
- Two Windows x64 assets from v3.8.0: the small installer (~45 MB, Tauri `downloadBootstrapper`)
  and the **offline WebView2 variant** (~250 MB, embeds the WebView2 Evergreen installer). Both are
  the same app with one SHA-256 line each.
- **Prerequisites/caveats:** the VC++ 2015-2022 runtime is installed by an NSIS hook that downloads
  it from Microsoft when missing or older than 14.40 — on a machine with no network, pre-install
  `vc_redist.x64.exe` (or let WebView2 setup provide it) before running the installer. The installer
  is unsigned. There is no auto-update: users download the next release deliberately (a privacy
  feature that is also an operational burden).
- Canonical steps and verification commands: [VERIFICATION.md](VERIFICATION.md); build variants:
  [BUILDING.md](BUILDING.md).

## 7. Support and maintenance — the honest weak point

- **Single maintainer** (fork) — bus factor 1. Issue tracker and SECURITY.md are the support
  channels; there is no SLA and no paid support.
- Upstream drift: upstream Vibe's latest release is v3.3.5 while the fork is based on v3.2.2 plus
  hand-ported changes ([UPSTREAM-PATCHES.md](UPSTREAM-PATCHES.md)); an incremental rebase is planned
  as v3.9.0.
- Model/engine redistribution is documented: MIT app, MIT/Apache models, **FFmpeg GPLv3** — good for
  commercial use of the app, but the GPL obligations for the bundled FFmpeg must be kept
  (NOTICE / THIRD-PARTY-NOTICES.md).

## 8. Field evidence — real, but only from the maintainer

- v3.6.0 and v3.7.0 (and v3.8.0 once published) installers were re-downloaded from the release page,
  hash-matched against `SHA256SUMS.txt`, silently installed, and checked for the expected
  `Sada.exe` product version, sidecar version and MCP banner — see [VERIFICATION.md](VERIFICATION.md).
- The maintainer's machine (Windows 11, GPU) is row A of [ACCEPTANCE.md](ACCEPTANCE.md). Rows B–E
  (offline Windows 10, CPU-only, AVX-only, AVX-less SSE4.2) remain unexecuted (#17) — that is the
  single biggest field-evidence gap, and the offline installer variant now makes running it easier.
- By design there is **no analytics or crash reporting**, so real-user field data does not exist.
  Feedback must come from users through the issue tracker (privacy-preserving, but slow).

## Go/no-go checklist

- [x] repeatable release pipeline, both installers, published hashes
- [x] automated suites (frontend, Rust, engine guard, benchmark harness, i18n)
- [x] offline operation, no telemetry/account/updater/relay
- [x] Arabic accuracy measured with CIs, unmeasured dialects named
- [x] regression gate for WER in the release checklist
- [x] bilingual release notes and documentation
- [ ] code-signed installer (#18, deferred by owner while open-source-only)
- [ ] clean-machine acceptance rows B–E (#17, needs hardware/VM)
- [ ] managed deployment packaging (MSI/GPO, central config) — not planned
- [ ] external security audit / dependency advisory scan — not scheduled

## How to close the remaining gaps

1. **Signing** (#18): the pipeline is staged; enabling it is a repository variable plus the chosen
   signing service. This removes the SmartScreen warning and is a hard requirement for managed
   deployment.
2. **Rows B–E** (#17): run the four clean-machine scenarios, record evidence in ACCEPTANCE.md. This
   turns "should work" into "measured".
3. **Iraqi/Levantine coverage**: needs a commercial-use corpus with human transcripts; owner
   purchase decision. Until then the app keeps the honest "unmeasured" label.
4. **Managed deployment**, if ever needed: MSI/GPO packaging, silent install switches documentation,
   central configuration/update plan, and a support commitment — none of which exist today.

## Arabic summary

**الخلاصة:** صدى جاهز للاستخدام الشخصي أو لفريق صغير على Windows، ويعمل بلا إنترنت ولا حساب ولا
تتبّع. الإصدار 3.8.0 يضيف مثبّتاً ثانياً لـ WebView2 يعمل دون اتصال، وبوّابة انحدار لدقّة التعرّف،
وتوثيقاً صريحاً لجهوزية التشغيل. المثبّت ما زال غير موقّع رقمياً بقرار المالك، لذلك يظهر تحذير
SmartScreen ويجب التحقق من بصمة SHA-256. لم تُنفَّذ بعد صفوف القبول B–E على أجهزة نظيفة (Windows 10
بلا إنترنت، ومعالج فقط، وSSE4.2 فقط)، ولا توجد قياسات للهجة العراقية أو الشامية، ولا حزمة نشر مركزي
(MSI/GPO) ولا دعم رسمي. لذلك: **جاهز للاستخدام الفردي والفرق الصغيرة، وليس بعد جاهزاً للنشر المُدار
في المؤسسات.** التفاصيل والأدلة في
[VERIFICATION.md](VERIFICATION.md) و[ACCEPTANCE.md](ACCEPTANCE.md) و[SIGNING.md](SIGNING.md).

## Evidence index

| Question | Where the evidence lives |
| --- | --- |
| Does it build and pass tests? | `.github/workflows/ci.yml`, [VERIFICATION.md](VERIFICATION.md) |
| Is the published installer the tested one? | [VERIFICATION.md](VERIFICATION.md) (size, SHA-256, silent install) |
| How accurate is Arabic? | `benchmarks/arabic-asr/results/`, [MODELS-DECISIONS.md](MODELS-DECISIONS.md), [P4-PLAN.md](P4-PLAN.md) |
| What is the security model? | [SECURITY.md](../SECURITY.md), engine guard tests |
| Why is it unsigned? | [SIGNING.md](SIGNING.md) |
| What was tested on real hardware? | [ACCEPTANCE.md](ACCEPTANCE.md) |
| What changed in this release? | [P5-PLAN.md](P5-PLAN.md), `CHANGELOG.md`, `docs/releases/v3.8.0.md` |
