# Production readiness — Sada 3.9.0

An evidence-based answer to "can we use this, and is it production ready?", written 2026-11-19 for
Sada 3.9.0 on Windows 10/11 x64. It is deliberately unflattering where the evidence is thin: every
claim below links to committed evidence, and every gap is named. If a category is not listed, it was
not assessed.

Related: [VERIFICATION.md](VERIFICATION.md) (per-release evidence and hashes),
[ACCEPTANCE.md](ACCEPTANCE.md) (manual acceptance matrix), [SECURITY.md](../SECURITY.md) (security
model), [SECURITY-WHITEPAPER.md](SECURITY-WHITEPAPER.md) (assurance pack), [NETWORK.md](NETWORK.md)
(egress inventory), [DATA-HANDLING.md](DATA-HANDLING.md), [AV-EDR.md](AV-EDR.md),
[ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md), [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md),
[SIGNING.md](SIGNING.md), [P6-PLAN.md](P6-PLAN.md) (what v3.9.0 changed).

## Verdict

| Audience | Verdict | What still blocks a stronger claim |
| --- | --- | --- |
| **Individual / personal use** | **Ready** | Unsigned installer shows a SmartScreen warning; Windows 10 without WebView2 needs the offline installer; some dialects are unmeasured (below). |
| **Small team / office, manual installs** | **Ready with conditions** | Same as above, plus: verify SHA-256 before installing, no automatic updates (by design), no support contract. Retention and DPAPI key storage are available. |
| **Managed / enterprise deployment** | **Pilot-ready** | An MSI, managed policy (offline mode + feature disables), detection/cleanup scripts and a deployment guide now exist, and the assurance pack answers the usual security questionnaire. Still blocking a full "ready": binaries are unsigned (owner decision), clean-machine rows B–E are unexecuted, the policy is enforced inside the app (a local admin can change it), and there is no SLA. |
| **Sensitive / regulated data** | **Ready with controls (pilot)** | Offline design, no telemetry, DPAPI-sealed keys, retention purge, documented egress and a threat model are in place. Accepted residuals remain: unsigned binaries, no at-rest encryption of transcripts (BitLocker required), no external audit/certification, single maintainer. |

In one sentence: **v3.9.0 closes the software-and-documentation gaps that previously blocked a
sensitive or managed pilot — offline policy, key protection, retention, egress inventory, supply-chain
evidence and an MSI — while code signing, independently executed hardware validation and an external
audit remain owner-level gaps and are stated as such.**

## What "production ready" means here

It installs and runs on the target hardware (including offline), Arabic output is predictable and
measured rather than asserted, no data leaves the machine, the release pipeline is repeatable and
verified, upgrade paths keep user data, and limitations are documented before users hit them.

## 1. Build and release pipeline — strong, now with supply-chain evidence

- CI (`.github/workflows/ci.yml`) runs on every push to master and every pull request: frontend
  type-check/build, **204 vitest tests in 33 files**, **120 Rust tests** (app, MCP, Arabic
  normaliser, managed policy, DPAPI, retention), plus the Python benchmark harness suite. The
  release workflow (`.github/workflows/release.yml`) builds the engine from `server/`, runs the
  **8 loopback request-guard tests**, builds NSIS default + offline and a **per-machine MSI**, then
  publishes only if the tag matches the app version and release notes exist.
- **Supply-chain evidence**: every release asset gets a GitHub build provenance attestation
  (Sigstore, keyless), a CycloneDX SBOM is published, `SHA256SUMS.txt` remains the offline path,
  and `scripts/verify-release.ps1` checks hashes and attestations in one step. Details:
  [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md).
- Pinned inputs: lockfiles, `.server-version` engine pin, vendored FFmpeg sidecar, catalogue model
  hashes. A rebuild is not bit-identical (MSVC/NSIS/WiX builds are not reproducible byte-for-byte),
  so the published hash plus attestation is the reference, not a rebuild.
- **Gap:** no code signing (owner decision, see [SIGNING.md](SIGNING.md)); no third-party build audit.

## 2. Automated tests — good, with named holes

| Area | Evidence | What it proves |
| --- | --- | --- |
| Frontend/UI logic | 204 vitest tests / 33 files (`cd desktop && pnpm test`) | Arabic text, PDF layout, settings, transcript state, exports, managed policy, key sealing |
| Rust shell | 120 tests (`cd desktop/src-tauri && cargo test --release`) | MCP server, Arabic normaliser, file/URL handling, policy, DPAPI, retention, app commands |
| Engine guard | 8 tests (`cd server && cargo test --release -p vibe-server guard::`) | loopback Host/Origin rejection |
| Benchmark harness | 62 tests (`cd benchmarks/arabic-asr && python -m unittest discover -s tests`) | WER/CER, normalisation, manifest integrity, regression gate |
| i18n | `python scripts/check_i18n.py` | Arabic locale coverage against en-US (16 new privacy/policy strings) |
| Type-level | `cargo check --tests` and `pnpm exec tsc --noEmit` | test-only code and the UI compile |

**Not covered:** no automated end-to-end UI test on a clean machine, no installer-upgrade
automation beyond the documented silent-install smoke check, no load test for very long audio, no
fuzzing of media/import parsing, and no automated benchmark run (needs model weights; the
`sadabench compare` gate guards a release re-run). Clean-machine rows B–E remain unexecuted — a
runbook and script now make them executable by anyone with the hardware
([VALIDATION-RUNBOOK.md](VALIDATION-RUNBOOK.md)).

## 3. Security and privacy posture — strong design, unsigned binary

Design (see [SECURITY.md](../SECURITY.md), [SECURITY-WHITEPAPER.md](SECURITY-WHITEPAPER.md),
[THREAT-MODEL.md](THREAT-MODEL.md)):

- Local Tauri shell; the engine is a bundled sidecar reachable only through loopback guarded by a
  Host/Origin check (unit-tested). No inbound service is exposed.
- Strict CSP and a minimal capability set; no remote content; no auto-updater, telemetry, account,
  analytics or phone relay. The handoff start command always refuses.
- **Managed policy** (3.9.0): HKLM policy with ProgramData JSON fallback enforces offline mode and
  disables AI, URL import and model downloads; the Rust layer enforces on every guarded action.
- **Egress inventory** (3.9.0): [NETWORK.md](NETWORK.md) lists every outbound path and the policy
  switch that removes it; the offline policy turns them all off, including the connectivity probe.
- **API keys** are DPAPI-sealed (current-user); plaintext config keys migrate once at boot.
- Model downloads verified against catalogue SHA-256; imported files stay local; yt-dlp is
  hash-checked against its release sums.
- MCP mode is stdio-only: no port, no firewall rule, no network surface.

**Gaps:** released binaries are **unsigned** (owner decision while the project is open-source-only;
pipeline staged, see [SIGNING.md](SIGNING.md)) — SmartScreen warns and tamper evidence relies on
published hashes + attestations. No third-party audit or certification. Dependency advisories are
now scanned in CI (#29), but that is hygiene, not assurance.

## 4. Data handling — local, now with retention and key protection

Settings, logs and sealed keys live in `%APPDATA%\app.sada.desktop\`; transcripts and media in the
chosen transcripts folder (default `Documents\Sada`); models in the app's model directory. Nothing
is synchronised or uploaded. Windows profile ACLs plus BitLocker are the access control; the app does
not encrypt transcripts at rest (stated plainly in [DATA-HANDLING.md](DATA-HANDLING.md)).

New in 3.9.0: optional retention window (0/7/30/90/365 days), automatic purge at launch and a manual
purge action limited to transcript files under the transcripts folder (symlinks skipped, counts and
bytes reported, content never logged); DPAPI sealing of AI keys; logs reviewed to exclude transcript
text and keys.

## 5. Arabic accuracy — measured, not perfect, honestly bounded

The committed 90-clip suite (30 MSA + 10 Latin-mixed + 20 Egyptian + 15 Gulf + 15 technical
code-switch) measures the default engine at **30.27% WER / 18.84% CER** (Whisper large-v3-turbo,
word timestamps 100%, 27.3% of Latin names kept, RTF 0.38). Per-slice: MSA 22.09%, Egyptian
11.03%, Gulf 42.74%, technical 46.18%, Latin-mixed 48.96%. Tables, raw transcripts and method:
`benchmarks/arabic-asr/results/results-2026-11-18-v2.json`/`.md`, decisions in
[MODELS-DECISIONS.md](MODELS-DECISIONS.md).

- Conversation/code-switch Arabic is harder than read MSA/Egyptian; the app says so.
- **Iraqi and Levantine are unmeasured** — no commercial-use-permissive corpus with human
  transcripts was found (matrix in [P4-PLAN.md](P4-PLAN.md)). No claim is made for them.
- 15-clip slices have wide confidence intervals; treat sub-2 pp deltas as unresolved.
- `sadabench compare` fails a release when a re-run regresses more than 1.0 pp WER overall or on
  any slice, so accuracy cannot silently rot.

## 6. Installation and distribution — three packages, managed path added

- Per-user NSIS into `%LOCALAPPDATA%\Sada\`, no admin. Two variants: small (~45 MB, WebView2
  bootstrapper) and offline (~250 MB, embedded WebView2).
- **Per-machine MSI** (3.9.0) for Intune/SCCM/GPO: `msiexec /i ... /qn`, detection rules,
  cleanup scripts and silent switches documented in
  [ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md).
- No auto-update by design: fail-closed update path (user/administrator deploys the next build).
- **Caveats:** VC++ 2015-2022 runtime is installed by an NSIS hook that downloads it when missing —
  offline machines need `vc_redist.x64.exe` pre-installed (or WebView2 setup providing it); the
  installer is unsigned; MSI needs admin rights and a WebView2 runtime present.

## 7. Support and maintenance — the honest weak point

- **Single maintainer** (fork) — bus factor 1. Issue tracker and SECURITY.md are the support
  channels; no SLA, no paid support.
- Upstream drift: the fork is based on upstream Vibe v3.2.2 plus hand-ported changes
  ([UPSTREAM-PATCHES.md](UPSTREAM-PATCHES.md)); an incremental rebase is planned work, not done.
- Licensing: MIT app; MIT/Apache models; **FFmpeg GPLv3** bundled as a separate executable — good
  for commercial use if NOTICE/THIRD-PARTY-NOTICES obligations are kept.

## 8. Field evidence — real, but only from the maintainer

- v3.6.0–v3.8.0 installers were re-downloaded from the release page, hash-matched, silently
  installed and version-checked — see [VERIFICATION.md](VERIFICATION.md). v3.9.0 evidence is added
  there on release.
- The maintainer's machine (Windows 11, GPU) is row A of [ACCEPTANCE.md](ACCEPTANCE.md). Rows B–E
  (offline Windows 10, CPU-only, AVX-only, AVX-less SSE4.2) remain unexecuted — the biggest field
  evidence gap. A script and evidence template now exist ([VALIDATION-RUNBOOK.md](VALIDATION-RUNBOOK.md)).
- No analytics or crash reporting by design, so no real-user field data; feedback comes through the
  issue tracker (privacy-preserving, slow).

## Go/no-go checklist

- [x] repeatable release pipeline with three installers and published hashes
- [x] attested supply chain, SBOM, verification script
- [x] automated suites (frontend, Rust, engine guard, benchmark harness, i18n)
- [x] offline operation, no telemetry/account/updater/relay
- [x] egress inventory and machine-wide offline policy enforced in Rust
- [x] DPAPI key storage and optional transcript retention
- [x] assurance pack for security review (whitepaper, threat model, data handling, AV/EDR)
- [x] managed deployment path (MSI + policy + detection/cleanup scripts + guide)
- [x] Arabic accuracy measured with CIs, unmeasured dialects named
- [ ] code-signed installer (#18, deferred by owner while open-source-only)
- [ ] clean-machine acceptance rows B–E (#17/#34, needs hardware/VM)
- [ ] external security audit / certification — not scheduled

## How to close the remaining gaps

1. **Signing** (#18): pipeline is staged; enabling it is a repository variable plus the chosen
   signing service. Removes SmartScreen warnings; hard requirement for a full managed/regulated sign-off.
2. **Rows B–E** (#17/#34): run the four scenarios with `scripts/acceptance/run-row-b-e.ps1`, record
   the evidence. Turns "should work" into "measured".
3. **Iraqi/Levantine coverage**: needs a commercial-use corpus with human transcripts; owner
   purchase decision. Until then the "unmeasured" label stays.
4. **External audit / pen test**: owner budget decision; the assurance pack is the input.

## Arabic summary

**الخلاصة:** صدى 3.9.0 يغلق الثغرات البرمجية والتوثيقية التي كانت تمنع تجربة استخدام حساسة أو
مُدارة: سياسة جهاز تفرض وضع عدم الاتصال وتُعطّل الذكاء الاصطناعي واستيراد الروابط والتنزيلات،
وتخزين مفاتيح API عبر DPAPI، وسياسة احتفاظ بالنصوص مع حذف آمن، وجرد كامل للاتصالات الشبكية، وحزمة
ضمانات أمنية، وسلسلة توريد موثّقة (بيانات provenance وSBOM)، ومثبّت MSI للنشر المُدار. المثبّت ما زال
غير موقّع رقمياً بقرار المالك، ولم تُنفَّذ بعد صفوف القبول B–E على أجهزة نظيفة، ولا توجد قياسات
للهجة العراقية أو الشامية، ولا دعم رسمي أو تدقيق خارجي. لذلك: **جاهز للاستخدام الفردي والفرق
الصغيرة، وجاهز لتجربة مؤسسية مُدارة بحذر، وليس بعد جاهزاً لاعتماد تنظيمي كامل.** التفاصيل في
[VERIFICATION.md](VERIFICATION.md) و[ACCEPTANCE.md](ACCEPTANCE.md) و[ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md).

## Evidence index

| Question | Where the evidence lives |
| --- | --- |
| Does it build and pass tests? | `.github/workflows/ci.yml` / `release.yml`, [VERIFICATION.md](VERIFICATION.md) |
| Is the published installer the tested one? | [VERIFICATION.md](VERIFICATION.md), [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md), `scripts/verify-release.ps1` |
| How accurate is Arabic? | `benchmarks/arabic-asr/results/`, [MODELS-DECISIONS.md](MODELS-DECISIONS.md), [P4-PLAN.md](P4-PLAN.md) |
| What is the security model? | [SECURITY.md](../SECURITY.md), [SECURITY-WHITEPAPER.md](SECURITY-WHITEPAPER.md), [THREAT-MODEL.md](THREAT-MODEL.md) |
| What data is stored and how do I delete it? | [DATA-HANDLING.md](DATA-HANDLING.md) |
| What does it connect to? | [NETWORK.md](NETWORK.md) |
| Can I deploy it with Intune/SCCM? | [ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md) |
| Why is it unsigned? | [SIGNING.md](SIGNING.md) |
| What was tested on real hardware? | [ACCEPTANCE.md](ACCEPTANCE.md), [VALIDATION-RUNBOOK.md](VALIDATION-RUNBOOK.md) |
| What changed in this release? | [P6-PLAN.md](P6-PLAN.md), `CHANGELOG.md`, `docs/releases/v3.9.0.md` |
