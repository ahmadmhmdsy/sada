# Step Zero B — Arabic subtitle burn-in falsification

**Status:** **PASS — 5/5 clips correctly shaped and readable at 720p** (with one caveat for native typography review)
**Date of test:** 2026-11-19 (Asia/Baghdad)
**Authorisation:** OWNER-ACTIONS A15 — owner instruction "then A14 then A15" (2026-11-19)
**Workstream:** FC-2 Step Zero A (separate report) and FC-3 Step Zero B (this report), GitHub issue [#60](https://github.com/alshahia/sada/issues/60)
**Release under test:** tag `v3.10.0` tree (commit `be27bd5`); no product code, dependency or version changed by this test.

## Question

Can the **bundled** FFmpeg burn correctly shaped, right-to-left Arabic subtitles onto a
720p H.264 video — offline, with the fonts that already ship in the app, and without
Python or a network call — well enough to be a real feature candidate?

## Verdict

**Yes for the falsification test.** Five out of five clips rendered with joined Arabic
letterforms, correct right-to-left order, correct diacritic positioning, correct mixed
Latin/Arabic runs and correct digit/date/time placement. Arabic punctuation
(`؟`, `،`), guillemets (`«»`), parentheses, brackets and an em dash all rendered as
real glyphs — no tofu, no disconnected letters, no reversed words.

One caveat to carry into any future feature work: neutral bidi characters around
numbers (the percent sign in `87%`) and mirrored brackets are placed acceptably but
were judged by an agent, not by a native Arabic typographer. A native pass is required
before shipping UI copy that depends on their exact placement. That does not change the
pass verdict for *shaping* and *readability*, which is what this test measured.

## Environment (recorded, not inferred)

| Item | Value |
| --- | --- |
| Host | Windows x64, NVIDIA Quadro RTX 4000 (8,192 MiB), Intel UHD 630 |
| FFmpeg | Bundled `desktop/src-tauri/binaries/ffmpeg-x86_64-pc-windows-msvc.exe` — "ffmpeg version 9.0.2-essentials_build-www.gyan.dev", `--enable-libass --enable-libfribidi --enable-libharfbuzz`, filters `ass` and `subtitles` present |
| Fonts | Bundled `desktop/src/assets/fonts/IBMPlexSansArabic-Regular.ttf` (236,708 B) and `-Bold.ttf` (247,896 B); both used |
| Script | UTF-8 SRT, no BOM; one cue per line (a font/language exercise, not a wrapping test) |
| Video under test | 1280×720, 25 fps, 10 s, H.264 yuv420p, silent AAC; synthetic dark background with a 160×90 grid so scaling is visible |
| Burn command | `ffmpeg -i clipN.mp4 -vf "subtitles=clipN.srt:fontsdir=.:force_style='FontName=IBM Plex Sans Arabic,FontSize=30,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=48'" -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a copy outN.mp4` |
| Review frames | One frame per cue at t = 2 s, 5 s and 8 s; subtitle region cropped and stacked per clip, then inspected at full 1280-px width |
| Network / Python | None — burn-in ran from the local binary with local fonts and local files |

## Test set and results

Five clips × three cues = fifteen Arabic lines covering the failure modes that font
shaping and bidi engines usually get wrong.

| Clip | Content type | Sample line | Result |
| --- | --- | --- | --- |
| 1 | MSA / formal, full diacritics (`اختبارٌ`, `متّصلة`, `التأكّد`) | هذا اختبارٌ لترجمة النصوص العربية داخل الفيديو. | **Pass** — every diacritic placed over its letter; medial/initial/final forms joined |
| 2 | Iraqi dialect, colloquial | هذا تجربة حتى نشوف الخط يطلع زين لو لا. / شنو رايك؟ واضح لو يحتاج تكبير؟ | **Pass** — dialect words shaped correctly; `؟` mirrored to the left end as RTL expects |
| 3 | Arabic + Latin/acronyms code-switching | نستخدم Wi-Fi و VPN و OCR في التطبيق. / ملف PDF فيه نصّ عربي وإنجليزي. | **Pass** — Latin runs keep LTR order inside the RTL line; no spacing collapse at the joins |
| 4 | Numbers, dates, times, percentages | الاجتماع يوم 2026/11/19 الساعة 14:30. / نسبة الإنجاز 87% خلال 3 أسابيع. | **Pass** — date and colon-time are unreversed and readable; digits keep Western order; percent sign legible (placement note below) |
| 5 | Punctuation and bidi neutrals | قال المدير: «الاجتماع انتهى»، ثم غادر. / هل وصلت الرسالة (رقم 12) أم لا؟ / نسخة 3.10.0 — ملاحظات الإصدار [مهمّة]. | **Pass** — `«»`, parentheses, `[ ]`, em dash and trailing periods all render; no tofu |

### What was looked for

1. **Shaping** — connected letterforms with correct initial/medial/final/isolated forms.
2. **Direction** — words and sentences read right-to-left; mdash and punctuation at the correct end.
3. **Diacritics** — fatha/kasra/shadda/sukun attached to the correct letter.
4. **Mixed runs** — Latin tokens and digits not reversed or reordered inside Arabic.
5. **Coverage** — no `.notdef`/tofu boxes (the bundled font covers Arabic + Latin + punctuation).
6. **Readability at 720p** — white fill, black outline, 30 px font, 48 px bottom margin, legible at 100 % video size on the review frame.

### Caveats and limits (honest scope)

- **Native typography review pending.** The agent inspected the frames. Placement of the
  percent sign in `87%` and the mirroring of `[]` around `[مهمّة]` are conventionally
  acceptable but should be signed off by a native reader before any shipped copy relies
  on them.
- **Single-line cues only.** Line wrapping and multi-line safe areas were not exercised;
  a feature implementation must test 2-line cues and a smaller font size.
- **Synthetic background.** The clips use a quiet dark grid, not busy footage. Contrast
  and outline settings must be re-verified against real video before release.
- **Font subsetting not tested.** The app ships TTF; the test used the TTF directly, which
  is what a bundled post-production path would do.
- **This test authorises nothing.** It records that FC-3 is technically viable with the
  bundled FFmpeg; it adds no UI, no CLI command and no release claim.

## Evidence artefacts (scratch, not committed)

Location: `E:/rea/vibe_app/.dsh/tmp/step-zero-b/` (kept on the build host; reproducible
from the commands above and the SRTs below).

| File | Bytes | SHA-256 |
| --- | --- | --- |
| clip1.srt | 346 | `0b7d4fa6…` |
| clip2.srt | 287 | `dd8f7c92…` |
| clip3.srt | 261 | `6148d3ca…` |
| clip4.srt | 262 | `7a509754…` |
| clip5.srt | 285 | `d5108170…` |
| out1.mp4 | 73,844 | `31877d07fbb5e99ba626873351f69d71538a9375294a7e14ef124a7fe0244c40` |
| out2.mp4 | 66,810 | `3a3f5ba445a1e1a69177d6ee87c0508c73b61f8d0bc3520c1a8e3bd7a5f3a0df` |
| out3.mp4 | 67,532 | `0bd033b6714659f27a1292d57989062af95edecabd2e90843e1e26bfae46a44b` |
| out4.mp4 | 66,709 | `e27a511ed9db56a909d320369ff836ebf4b00770307b7b1a7ab83353f7d22971` |
| out5.mp4 | 61,478 | `a5d9f3cf5545cb9f1760a90d48589635620fe65c022d6f8c339f9b309c3fcd53` |
| sheet1.png | 152,375 | `6227fb30705c01ba725a1924d7624dd4e4d394fedc8930c5e0f9b7370596375c` |
| sheet2.png | 131,053 | `9a79d5c9d5cfc021883333cfa8e78882efa173ea0e1435fd6e6ffe45e90a9b62` |
| sheet3.png | 132,944 | `44e20ca05dd714214bed53b47d4281a744ad75a97696d348749fef9da6293a1c` |
| sheet4.png | 130,920 | `b1c0d88af1faa8338b93609fb342eb24f8575ea636f582d3e6e5ad39e0308582` |
| sheet5.png | 127,910 | `b18fc3447bd745f56e4f444c3f1d4dd36a211441d50e1119b294c3edbdd2727b` |

Each `sheetN.png` stacks the three cue frames of clip N at full width; those are the
images the visual verdict is based on.

## Next step if this becomes a feature (not authorised by this report)

FC-3 is a **passer** in falsification terms, so it may be considered for the next feature
release **only** if the owner and the five-user gate approve it (P7-PLAN M2). The
implementation would be a post-production action that invokes the already-bundled FFmpeg
with a sidecar SRT, no new dependency, plus UI for style settings and the native
typography review above.
