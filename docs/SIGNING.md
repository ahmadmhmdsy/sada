# Windows code signing

The Windows installer and the app executable are **not signed** as of Sada v3.8.0. This page records
the options, their real costs, what the fork already has in the repository, and the recommendation
for when signing is funded. Nothing is purchased or enabled without the owner's decision.

**Status (2026-11-18): the owner decided to keep releases unsigned while the project is
open-source-only; the SignPath Foundation application comes later (issue #18). P5 staged the
pipeline so enabling it is configuration, not a redesign — see *When signing is enabled* below.
The released assets stay unsigned, and the release notes say so.

## What users see today

An unsigned NSIS installer triggers Microsoft Defender SmartScreen's "Windows protected your PC"
dialog ("unknown publisher") on machines where it has not been seen before. The bytes are still
guarded:

- every release publishes SHA256SUMS.txt and the installer hash in the release notes;
- docs/VERIFICATION.md records the published size and SHA-256 of each installer;
- the app has no updater, so a download cannot be swapped between versions silently.

Users are told to verify the hash before choosing *More info -> Run anyway*. That is honest but not
a good first-run experience, and it does not protect users who click through.

## What signing buys

| Property | Unsigned (today) | Signed |
| --- | --- | --- |
| SmartScreen first-run warning | yes | no after reputation exists (OV / Artifact Signing); usually no for EV |
| Publisher name in the dialog | unknown | certificate subject (person or registered business) |
| Tamper evidence | hash published separately | Authenticode signature verifies offline |
| Enterprise / school deployment | often blocked by policy | allowed with a trusted publisher |
| Cost | 0 | see below |

## Options (list prices as of November 2026; confirm with the CA before buying)

| Option | Approx. cost | Identity requirement | CI fit | Notes |
| --- | --- | --- | --- | --- |
| **SignPath Foundation** | **free for open source** | public OSS project; SignPath verifies the binary came from the repository | HSM-based cloud signing, GitHub Action | Best fit for this fork: MIT, public repository, no hardware token, no purchase. Requires an application and review, so not instant. Used by Stellarium, Flameshot and others. |
| **Azure Artifact Signing** (formerly Trusted Signing) | ~US$9.99/month | organisation validation; individual accounts need 3 years of verifiable business history and are not available in every country | native GitHub Action, short-lived certificates, no token | Cheapest paid option and the cleanest CI path if the owner's entity qualifies. |
| **OV code signing certificate** | ~US$200-500/year | legal identity verification (individual or company) | certificate must live on a FIPS token or HSM since June 2023; the repository's scripts/sign.py drives a YubiKey from a signing machine over a tunnel | Works with a personal identity, but the token must be present for every release (or pay for the CA's cloud HSM). |
| **EV code signing certificate** | ~US$400-900/year | strict legal + business verification | same hardware/HSM constraint | Strongest reputation signal; SmartScreen may still build reputation. Overkill while the app is a small OSS fork. |

## What the repository already has

- scripts/sign.py (inherited from upstream Vibe) has two halves: a YubiKey signing server that
  shells out to jsign, and a client that a Tauri signCommand can call. It is a **dry run** unless
  SIGN_ENABLED=true and SIGN_TUNNEL_URL / SIGN_TUNNEL_SECRET are set.
- desktop/src-tauri/tauri.windows.signing.conf.json is a Tauri config **overlay** that wires
  `bundle.windows.signCommand` to `uv run ../../scripts/sign.py sign %1`. It is not merged into a
  normal build, so the base config and the default installer stay unsigned.
- .github/workflows/release.yml (P5, v3.8.0) has the dormant pipeline: a *Resolve signing
  configuration* step plus build steps that merge the signing overlay only when the repository
  variable `SIGNING_ENABLED` is `true`, and a *Verify Authenticode signatures* step that fails the
  release if any asset is not validly signed. With the variable unset — today — those steps are
  skipped, `uv` is not installed, no signer is spawned and no secret is needed.
- The release still publishes SHA-256 lines for **both** installers (small and offline WebView2),
  so users can verify what they downloaded without any signing infrastructure.

## Recommendation

1. **Apply to SignPath Foundation first.** It is free, designed for public OSS, signs from an HSM
   (no token in CI), and is enough to remove the unknown-publisher warning while keeping the
   project's licence and independence. Filling the application is a decision for the owner.
2. If SignPath does not accept the project and the owner has a qualifying entity, **Azure Artifact
   Signing** at about US$120/year is the next cheapest option.
3. Buy an OV/EV certificate only if a partner or store requires a specific publisher legal name.
4. Until one of those is funded: keep publishing hashes, keep the verification steps in the release
   notes, and keep the installer small (bundling a full WebView2 offline installer is a separate
   size decision, see docs/ACCEPTANCE.md).

## When signing is enabled

The switch is the repository variable `SIGNING_ENABLED=true` (Settings → Secrets and variables →
Actions → Variables). The workflow then:

1. installs `uv` (needed by the existing Tauri signCommand overlay);
2. merges `desktop/src-tauri/tauri.windows.signing.conf.json` into both installer builds;
3. exports `SIGN_ENABLED=true` (from the variable) and the `SIGN_TUNNEL_URL` /
   `SIGN_TUNNEL_SECRET` repository secrets to `scripts/sign.py`;
4. runs the Authenticode verification step before the release is created, so an unsigned asset
   cannot be published by accident.

The YubiKey tunnel signer is the path the inherited script implements. If the SignPath Foundation
application is approved instead, replace step 2 with the SignPath GitHub Action (its project/policy
IDs come from the accepted application) and drop the signing overlay: SignPath signs in its own
pipeline and `signCommand` is not needed there. Keep the variable and the verification step.

Manual verification (same check the workflow runs):
    Get-AuthenticodeSignature .\Sada_<version>_x64-setup.exe | Format-List Status, SignerCertificate
    & "$env:ProgramFiles(x86)\Windows Kits\10\bin\*\x64\signtool.exe" verify /pa /v .\Sada_<version>_x64-setup.exe

Repeat for `Sada_<version>_x64-setup-offline.exe`. Status must be **Valid**, and the signer must be
the expected publisher. SmartScreen reputation still needs to build after the first signed release;
signing removes the unknown-publisher warning, it does not create instant trust for a new file.

## Arabic summary

الملف غير موقّع حتى الإصدار 3.8.0، لذلك يظهر تحذير SmartScreen ("ناشر غير معروف"). قرار المالك في
2026-11-18 هو البقاء على إصدارات غير موقّعة ما دام المشروع مفتوح المصدر فقط، مع تجهيز المسار
لكي يُفعَّل لاحقاً بمتغير واحد. الحماية الحالية هي نشر بصمة SHA-256 للمثبّتَين (الصغير ومثبّت
WebView2 دون اتصال) مع كل إصدار. الخيار الموصى به عند التقديم هو **SignPath Foundation** المجاني
للمشاريع مفتوحة المصدر، ثم **Azure Artifact Signing** بحدود 10 دولارات شهرياً إذا كان الكيان
مؤهلاً؛ ولا تُشترى شهادة OV/EV قبل قرار المالك. في v3.8.0 أصبح سير الإصدار يدمج ملف
tauri.windows.signing.conf.json ويشغّل scripts/sign.py فقط عندما يكون المتغير SIGNING_ENABLED
مساوياً true، ثم يتحقق من التوقيع قبل النشر؛ وبدون المتغير يبقى كل شيء كما هو اليوم: غير موقّع
وبدون أسرار.
