# صدى (Sada) — Arabic-first transcription, on your own computer

Sada is an Arabic-first fork of [Vibe](https://github.com/thewh1teagle/vibe) (MIT), built on
upstream tag **v3.2.2**. It transcribes audio and video fully offline using Whisper models, and
it opens in Arabic, right-to-left, with Arabic defaults out of the box. English and the other
upstream languages are still available from Settings.

- Arabic README (main): [README.ar.md](./README.ar.md)
- What changed compared with upstream v3.2.2: [docs/UPSTREAM-PATCHES.md](./docs/UPSTREAM-PATCHES.md)
- Privacy: [PRIVACY.md](./PRIVACY.md)
- Licences and attribution: [NOTICE](./NOTICE), [THIRD-PARTY-NOTICES.md](./THIRD-PARTY-NOTICES.md)
- Upstream README snapshot: [docs/upstream-README.md](./docs/upstream-README.md)

Sada is an independent fork. It is not affiliated with, endorsed by or published by the
original Vibe author. "Vibe" remains the property of its author; the Sada name and artwork are
this fork's own.

## Build

See [docs/BUILDING.md](./docs/BUILDING.md). On Windows, the first build needs Rust, Node.js
with pnpm 10, and the two sidecar binaries in `desktop/src-tauri/binaries/` (see
`desktop/src-tauri/binaries/README.md`). Then:

```powershell
cd desktop
pnpm install
pnpm build
pnpm exec tauri build
```

The NSIS installer is written to `desktop/src-tauri/target/release/bundle/nsis/`.

## Licence

MIT, see [LICENSE](./LICENSE). This fork ships the same bundled FFmpeg build as upstream,
which is GPLv3; read [THIRD-PARTY-NOTICES.md](./THIRD-PARTY-NOTICES.md) before distributing a
build to anyone else.
