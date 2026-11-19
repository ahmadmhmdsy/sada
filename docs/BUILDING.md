# Building

### Prerequisites

[pnpm](https://pnpm.io/) | [uv](https://docs.astral.sh/uv/) | [Cargo](https://www.rust-lang.org/tools/install)

Install [chore](https://getchore.github.io/chore/) to use the tasks in the root `chorefile` (run `chore list` to see them; it includes each area's `tasks.chorefile`):

```console
# macOS / Linux
curl -fsSL https://getchore.github.io/chore/install.sh | sh
# Windows
irm https://getchore.github.io/chore/install.ps1 | iex
```

**Linux**:

```console
chore linux-deps
```

That is the apt list from [tauri/prerequisites/#setting-up-linux](https://v2.tauri.app/start/prerequisites/#linux)
plus what Vibe adds — alsa, xdo and the appindicator bindings. The release
workflow runs the same task, so the packages CI has are the packages you get.

**macOS**:

Make sure to install XCode from the AppStore and open it once so it will download essential macOS libraries.

## Build

```console
chore dev      # fetch the sidecars, then run the app
chore build    # fetch the sidecars, then build for production
```

Both start with `chore setup`, which downloads the sidecars from the server
release pinned by `.server-version` into `desktop/src-tauri/binaries/`. The same steps by hand:

```console
chore setup
cd desktop
pnpm install
pnpm exec tauri dev    # or: pnpm exec tauri build
```

`chore setup` takes a target triple for cross-compiles — `chore setup
x86_64-pc-windows-msvc` — which is how the release workflow uses it. Without one
it fetches for this machine.

On macOS, `chore upgrade` builds the app, replaces `/Applications/vibe.app` and
relaunches it.

## Build the Windows installer variants

The default NSIS build keeps Tauri's small `downloadBootstrapper` WebView2 mode: the installer is
about 45 MB and the first install on a Windows 10 machine that never ran a modern app downloads the
WebView2 Runtime. On a fully offline machine, use the second variant: it merges
`desktop/src-tauri/tauri.offline.conf.json`, which embeds the WebView2 Evergreen installer; the
finished asset is about 250 MB (the embedded installer is a full ~200 MB WebView2 standalone
downloadable, not the small bootstrapper).

```console
cd desktop
# default small installer (published as Sada_<version>_x64-setup.exe)
pnpm exec tauri build --bundles nsis
# offline WebView2 variant (published as Sada_<version>_x64-setup-offline.exe)
pnpm exec tauri build --bundles nsis --config src-tauri/tauri.offline.conf.json
```

Both NSIS builds write the same `Sada_<version>_x64-setup.exe` file name, so the release workflow
builds the offline variant first, renames it to `...-offline.exe`, then builds the default;
`SHA256SUMS.txt` gets one line per installer. The NSIS hook (`vc_redist.nsh`) installs the VC++
2015-2022 runtime from the network when it is missing or too old — that applies to both variants.

The third asset is a **per-machine WiX MSI** for managed deployment (Intune/SCCM/GPO). It merges
`desktop/src-tauri/tauri.enterprise.conf.json` (MSI target, en-US installer language) and installs
into `C:\Program Files\Sada` with administrator rights:

```console
cd desktop
# per-machine MSI (published as Sada_<version>_x64_en-US.msi)
pnpm exec tauri build --bundles msi --config src-tauri/tauri.enterprise.conf.json
```

The release workflow builds and verifies all three. Documentation for silent install, detection,
policy and cleanup is in [ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md); the assurance and
supply-chain documents are [SECURITY-WHITEPAPER.md](SECURITY-WHITEPAPER.md) and
[SUPPLY-CHAIN.md](SUPPLY-CHAIN.md).

Code signing is a **dormant overlay**, not part of a normal build:
`desktop/src-tauri/tauri.windows.signing.conf.json` wires `scripts/sign.py` as
`bundle.windows.signCommand` and the release workflow merges it only when the `SIGNING_ENABLED`
repository variable is `true`. See [SIGNING.md](SIGNING.md) for the decision and switch-on procedure.

## Build the server locally (dev)

The engine lives in `server/` and ships as the `vibe-server` sidecar. To run the
app against a build of the tree instead of the pinned release:

```console
chore setup            # ffmpeg and the released server, once
chore server-build     # fetch the ggml libraries, build server/, stage it as the sidecar
```

`server-build` puts `vibe-server-<triple>` where `setup` put the release, so
`tauri dev` and `tauri build` pick it up unchanged. See `server/docs/BUILDING.md`
for the engine on its own.

Since 3.4.0 the release workflow runs the same two steps: the installer ships an engine
built from this tree, because the fork's loopback request guard lives in
`server/crates/vibe-server/src/server/guard.rs` (see [SECURITY.md](../SECURITY.md)).
That build is versioned `<.server-version>-sada.1`; the upstream sidecar fetched by
`setup` is only used for FFmpeg and for local dev before `server-build` runs.
The guard has unit tests (`cargo test -p vibe-server guard::`) that the release workflow runs.

## GPU acceleration (runtime)

The pinned sidecar (`.server-version`) is upstream's prebuilt `vibe-server` release with the ggml
**Vulkan** backend statically linked. There is no CUDA/ROCm build step and no GPU SDK in the build
requirements — the same binary also runs on the CPU.

- Runtime requirement: a GPU driver exposing Vulkan 1.1+, or no GPU at all (the engine falls back to
  CPU). If `vulkan-1.dll` is missing, install the Vulkan Runtime — see [DEBUG.md](DEBUG.md).
- List the devices the engine sees:

  ```console
  desktop/src-tauri/binaries/vibe-server-x86_64-pc-windows-msvc.exe devices
  ```

  It prints JSON per device: `index`, `name` (`Vulkan0`), `description` (the adapter name) and
  `type` (`gpu` / `igpu`). An empty list means Vulkan is not usable and transcription runs on CPU.
- The app selects the device per transcription in **Settings → Models → Hardware → GPU Device
  number**. **Auto** sends no device and the engine picks its default. The **Transcribe on CPU**
  switch sends `no_gpu` when the model is loaded.
- If a model fails to load on the GPU, the shell retries the same file once with `no_gpu`, warns
  the user, and remembers the model so later runs start on the CPU
  (`desktop/src-tauri/src/cmd/server_cmd.rs`).
- Building the engine from source is unchanged: `chore server-build` compiles the same crate with
  whatever ggml backend its release features enable. The shipped Windows sidecar bundles Vulkan,
  not CUDA.

## Test

```console
chore test     # frontend tests (vitest)
```

Rust tests:

```console
export RUST_LOG=trace
cargo test -- --nocapture
```

# Lint

```console
chore ci           # everything below, in one go
chore lint         # eslint, then cargo fmt and clippy with CI's flags
chore format       # prettier and cargo fmt, in place
chore check-types  # tsc over desktop and website
chore check-i18n   # translation coverage against en-US
```

# Create a new release

1. Bump the version in `desktop/src-tauri/tauri.conf.json` and `desktop/src-tauri/Cargo.toml`, and
   update the version strings in `CITATION.cff`, `README*.md`, `llms.txt`, `SECURITY.md` and the
   site pages.
2. Add `docs/releases/v<version>.md` — the release workflow uses it as the release body and fails
   without it — plus a `CHANGELOG.md` entry.
3. Push to `master` and wait for CI to pass. Then create and push the tag:

   ```console
   git tag v<version>
   git push origin v<version>
   ```

   The `Release` workflow checks that the tag matches the app version, builds the offline NSIS
   installer, the per-machine MSI and the default NSIS installer, generates the CycloneDX SBOM,
   creates keyless build provenance attestations, publishes all assets with `SHA256SUMS.txt` and
   the licence files, and verifies the published files with `scripts/verify-release.ps1` (hash +
   attestation) as part of the release checklist.

There is **no auto-updater** and the fork's release workflow publishes **Windows x64 only**; the
upstream Linux/macOS matrix and `latest.json` do not apply.

# Landing

## Compress images

```console
pnpx tinypng-go static/*.png
```

## Convert markdown to PDF

```console
go install github.com/mandolyte/mdtopdf/cmd/md2pdf@latest
md2pdf -i website/public/privacy_policy.md -o website/public/privacy_policy.pdf
```

## Normalize wav file for tests

```console
ffmpeg -i file.wav -ar 16000 -ac 1 -c:a pcm_s16le normal.wav
```

## Edit PR before merge

1. Install [gh cli](https://cli.github.com/)

```console
gh pr checkout <url>
git push <fork url>
```

## Update packages

```console
pnpm install
pnpx ncu -u
cd src-tauri
cargo install cargo-edit
rm -rf ../Cargo.lock
CARGO_NET_GIT_FETCH_WITH_CLI=true cargo upgrade
# OR
cargo +nightly -Zunstable-options update --breaking
```

## Clear Github actions cache

```console
gh cache delete -a
```

## Notes

- Always update crates and lock in specific commit so it will be easy to revert!!
- Don't upgrade important crates such as tauri as long as it stable and works and there's no real need!!

## Windows code signing

Sada releases are unsigned by owner decision (2026-11-18) while the project is open-source-only.
The release workflow already has a dormant signing pipeline (repository variable
`SIGNING_ENABLED`), and the fork does not use the upstream self-signed-certificate recipe. Read
[SIGNING.md](SIGNING.md) before changing anything here.
## Analytics (Optional)

Vibe uses [Aptabase](https://aptabase.com/) for analytics. Not required for development. To enable, set these env vars at build time:

```console
export APTABASE_APP_KEY="A-..."
export APTABASE_BASE_URL="https://..."
```

## Gotchas

## Build faster in dev mode (useful in Windows)

```console
rustup nightly install
rustup component add rustc-codegen-cranelift-preview --toolchain nightly
# Unix
CARGO_PROFILE_DEV_CODEGEN_BACKEND="cranelift" cargo +nightly build -Zcodegen-backend
# Powershell
$env:CARGO_PROFILE_DEV_CODEGEN_BACKEND="cranelift" ; cargo +nightly build -Zcodegen-backend
```

## Sada fork build notes

This fork uses the upstream build unchanged, with three practical additions:

1. `desktop/src-tauri/binaries/` must contain `vibe-server-x86_64-pc-windows-msvc.exe` and
   `ffmpeg-x86_64-pc-windows-msvc.exe` before `tauri build`; they are not committed (see the
   README in that folder).
2. The source tree must be a git repository with at least one commit: `desktop/src-tauri/build.rs`
   calls `git rev-parse` to embed the commit hash, and fails outside a repo. Run
   `git init && git add -A && git commit -m init` in a fresh export.
3. Pin pnpm 10 (the repository uses pnpm 10.4.1; `pnpm install` with pnpm 11 changes the lockfile
   and can break the Tauri CLI invocation).

4. `cargo build --release` in `desktop/src-tauri` produces `target/release/vibe.exe` (the crate
   name is still `vibe`); `pnpm exec tauri build` copies it to the bundled `Sada.exe` and builds the
   NSIS installer. The MCP server is part of that executable, so a plain cargo build is enough to
   test it headlessly:

   ```console
   cargo build --release
   cargo test --release mcp::
   cargo test --release arabic::
   target/release/vibe.exe --mcp --config <scratch-config.json> < requests.jsonl
   ```

   Requests/responses are one JSON line each; stdout carries protocol frames only and stderr carries
   diagnostics. No port is opened, so nothing needs firewall rules.

The Windows build was verified with Rust 1.100.0, Node.js 24.11.1, pnpm 10.4.1 and the MSVC
2022 Build Tools; it produces `desktop/src-tauri/target/release/bundle/nsis/*-setup.exe`.
`beforeBuildCommand` runs `pnpm build` (paraglide compile → tsc → vite) automatically, so a
single `pnpm exec tauri build` is enough.
