# Windows code signing

The Windows installer and the app executable are **not signed** as of Sada v3.7.0. This page records
the options, their real costs, what the fork already has in the repository, and the recommendation
for when signing is funded. Nothing is purchased or enabled without the owner's decision.

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
  SIGN_ENABLED=true and SIGN_TUNNEL_URL / SIGN_TUNNEL_SECRET are set, so the release workflow can
  call it today without changing behaviour.
- .github/workflows/release.yml builds the installer and publishes it unsigned; it has no signing
  step or secrets yet.
- desktop/src-tauri/tauri.conf.json has no bundle.windows.signCommand (the Tauri hook the client
  script would occupy).

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

Tauri signs the executable and installer through bundle.windows.signCommand. With the repository
script the wiring is:

    "bundle": {
      "windows": {
        "signCommand": "uv run scripts/sign.py sign %1"
      }
    }

and the release job exports SIGN_ENABLED=true, SIGN_TUNNEL_URL and SIGN_TUNNEL_SECRET. For Azure
Artifact Signing or a cloud HSM the step is a signtool / trusted-signing-action call in
release.yml instead; signCommand is not needed there.

After signing, verify before publishing:

    Get-AuthenticodeSignature .\Sada_<version>x64-setup.exe | Format-List Status, SignerCertificate
    & "$env:ProgramFiles(x86)\Windows Kits\10\bin\*\x64\signtool.exe" verify /pa /v .\Sada_<version>x64-setup.exe

Status must be Valid, and the signer must be the expected publisher. Add the same check to the
release workflow so an unsigned artifact cannot be published by accident.

## Arabic summary

الملف غير موقّع حتى الإصدار 3.7.0، لذلك يظهر تحذير SmartScreen ("ناشر غير معروف"). الحماية الحالية
هي نشر بصمة SHA-256 مع كل إصدار. الخيار الموصى به هو التقدّم إلى **SignPath Foundation** المجاني
للمشاريع مفتوحة المصدر، ثم **Azure Artifact Signing** بحدود 10 دولارات شهرياً إذا كان الكيان مؤهلاً؛
ولا تُشترى شهادة OV/EV قبل قرار المالك. سكربت scripts/sign.py الموجود جاهز للتوصيل عبر signCommand
لكنه يبقى معطلاً حتى تتوفر الشهادة.
