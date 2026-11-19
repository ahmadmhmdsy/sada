# Owner decisions — UI/UX questions (19 November 2026)

Status: **decided and implemented for 3.10 in the working tree; release tagging is separate.**
The questions, boards and original recommendation are in [README.md](README.md); the 4.0 direction
is in [../echo-identity-4.0.md](../echo-identity-4.0.md). Evidence screenshots are in
[shots/wave1/](shots/wave1/).

## 1. The four answers

| # | Question | Owner answer (verbatim) | Read as |
| --- | --- | --- | --- |
| Q1 | Which repair family leads? | **“all of the options”** | All four families are P1 in Wave 1 — none is postponed to Wave 2 |
| Q2 | How much do we take on now? | **“الإصدار الأول: أربع إصلاحات فقط”** | Wave 1 only (the four repairs + trust copy), then the five-user gate |
| Q3 | How far do we move from the clone? | **“C · هوية 4.0 — «الصدى»”** | Full Echo identity is the 4.0 direction; **not** built in 3.10 |
| Q4 | Which sentence can survive the truth? | **“قل ما هو صحيح فقط”** | V3 scoped truth-only copy, shipped with the trust/recovery work |

Consequences applied:

- 3.10 = four repairs (A–D below) + V3 trust copy. No identity/token/layout work from Q3, no Wave 2.
- The Echo identity is briefed, not implemented; it starts after the measurement gate on 3.10.
- Any copy that cannot be proven on the first-run download screen is out — including the “absolute
  privacy” lines the boards audited.

## 2. Release map

```text
3.10 (this work)          five-user gate           3.11 Wave 2         4.0
four repairs + V3   →     measure, decide     →    planned repairs  →  Echo identity (brief)
```

| Release | Content | Gate |
| --- | --- | --- |
| 3.10 | A error/recovery, B finish line, C settings door/hierarchy, D Arabic typography, V3 trust copy, `set_theme` fix | five-user test below; no Wave 2 before it passes |
| 3.11 | Wave 2 repairs as planned in [00-overview.html](00-overview.html) | after 3.10 gate + owner go |
| 4.0 | Full Echo identity per [../echo-identity-4.0.md](../echo-identity-4.0.md) | after gate + separate owner approval of the identity preview |

## 3. What was implemented in 3.10

### A · Trust & failure recovery

- `desktop/src/lib/error-kind.ts` (+ `error-kind.test.ts`): classifies a failure log into
  `model | network | audio | file | disk | memory | managed | unknown` with a fixed precedence
  (disk → memory → network → audio → file → model).
- `desktop/src/components/error-modal.tsx`: one dialog, kind-specific title/body/primary action;
  raw log is behind a disclosure with an accessible **Copy details**; **Report issue** is demoted to
  secondary; **Reset** moved under **Advanced**. The primary action is contextual: open model
  settings, retry a network step, or reload.
- `desktop/src/providers/error-modal.tsx`: carries the optional `kind` through the modal state;
  `pages/main/session.tsx` reports recording failures as `audio`.
- `desktop/src/providers/preference.tsx` + `src-tauri/capabilities/main.json`: the window
  `setTheme` call now catches its rejection and has the `core:window:allow-set-theme` capability, so
  a theme change can no longer leave an unhandled promise error (the immediate council fix).

### B · The finish line: copy all + grouped export

- `desktop/src/pages/main/components/transcript-toolbar.tsx`: a filled-primary **Copy all** button
  next to Export, `Ctrl+Shift+C`, full transcript as plain text, toast confirmation, hint in the
  tooltip.
- `desktop/src/pages/main/components/transcript-export-dialog.tsx`: the nine formats are grouped
  under four small headings — **Text** (TXT, Markdown), **Captions & timing** (SRT, WebVTT),
  **Document** (HTML, DOCX, PDF), **Data** (JSON, CSV). In batch mode Export opens a menu (single job
  Export opens the dialog directly, as before).

### C · Settings door and hierarchy

- `desktop/src/components/settings-modal.tsx`: rebuilt on Radix `Dialog` — focus trap, focus
  restore on close, `Escape`, a real X button; content is transparent so the page styling owns the
  surface.
- `desktop/src/pages/settings/page.tsx`: centered modal layout, labelled X button, four navigation
  groups (App, Transcription, Voice & assistant, More options) with group headings instead of one flat list.
- `desktop/src/components/layout.tsx` + `components/ui/dialog.tsx`: Settings gear in the header
  (with a drag-region spacer), `Ctrl+,`, a `vibe:open-settings` event, and `#settings` opens the
  dialog on mount.

### D · Arabic typography

- `desktop/src/globals.css`: inverse tracking rule — `html[lang^='ar'] * { letter-spacing: 0 }` —
  with explicit exceptions for mono/tabular time and uppercase Latin labels. Arabic letters no longer
  inherit the Latin UI tracking.
- `desktop/src/pages/setup/page.tsx`: download sizes are wrapped in Unicode bidi isolates
  (U+2066/U+2069) so “25 MB من 100 MB” keeps its order in Arabic; verified visually in
  [shots/wave1/04-first-run-ar.png](shots/wave1/04-first-run-ar.png).

### Q4 · V3 scoped truth-only copy

| Where | Arabic | English |
| --- | --- | --- |
| Drop point | التفريغ يتم على هذا الجهاز — لا يُرفع أي صوت أو نص. | Transcription happens on this computer — no audio or text is uploaded. |
| Drop point, second line | التنزيل الأول للنموذج يحتاج إنترنت، وبعدها يعمل صدى دون اتصال. | The first model download needs the internet; after that Sada works offline. |
| First run | هذا التنزيل يحتاج إنترنت مرة واحدة. بعدها يعمل صدى دون اتصال، ولا يُرفع أي صوت أو نص. | This download needs the internet once. After that Sada works offline, and no audio or text is uploaded. |
| Settings · Privacy | بعد تنزيل النموذج مرة واحدة، يعمل صدى على هذا الجهاز بالكامل: لا تحليلات ولا قياس عن بُعد ولا حساب، ولا يُرفع أي صوت أو نص. | After the one-time model download, Sada runs entirely on this computer: no analytics, no telemetry, no account, and no audio or text is uploaded. |

- `idle-hero.tsx` puts the trust block under the panel slot (shield + the two lines above).
- `setup/view-model.ts` captures `{done, total}` bytes and an ETA; `setup/page.tsx` shows
  `role="progressbar"` with aria values, an `aria-live` percent + “x of y” size + ETA, and
  “This happens only once…” for non-URL downloads. The ETA appears only after enough real progress to
  avoid a jumping estimate.
- Settings privacy section keeps the same claim, now with the download exception.
- Banned phrases audit holds in both catalogues: no “never leaves your device”, no “absolute
  privacy”, no “100% safe”, no “offline” without the first-download exception, no ownership absolutes.

### Verification pass · runtime accessibility

The release check is not only “does it build”: the running dev-mock UI was audited with axe-core 4.14.1
(WCAG 2.2 A/AA tags) across **35 states** — idle, every Settings section, and the export dialog, in
English, Arabic and dark mode. It found and this pass fixed:

- Switches and Radix select triggers in Settings had no accessible name (the visible row label was not
  associated). A shared row-label context now gives both controls the label of the row they sit in.
- The selected Settings nav row and the version footer failed AA contrast; they now use
  `bg-primary/10 text-foreground` and solid muted text.
- The selected export-format badge used `bg-primary/20 text-primary` (3.39:1); it is now solid primary
  with primary-foreground text.
- Display-language and transcript-language triggers announced a name that did not contain their visible
  label (`label-content-name-mismatch`); each trigger now carries the label text.

Result: **0 violations in all 35 states.** Focus behaviour of the Radix settings dialog was verified
separately (Tab stays inside, Escape closes). This is automated evidence only — it does not replace the
screen-reader check on Windows or the five-user gate below.

## 4. Evidence (dev mock, headless Chrome 158, 1440×1000)

Captured from the Vite dev server with the mock Tauri layer (`desktop/src/mock-tauri/`), not from the
installed build; timestamps and paths are mock data. Screenshots 05, 06 and 09 were recaptured after
the contrast and accessible-name fixes above, so they show the shipped state, not the pre-fix one.

| Screenshot | Shows |
| --- | --- |
| [01-trust-at-drop-en.png](shots/wave1/01-trust-at-drop-en.png) | Trust block under the drop panel, English |
| [02-trust-at-drop-ar.png](shots/wave1/02-trust-at-drop-ar.png) | Trust block, Arabic RTL, normal tracking |
| [03-first-run-en.png](shots/wave1/03-first-run-en.png) | First-run download: percent, size, “This happens only once…” |
| [04-first-run-ar.png](shots/wave1/04-first-run-ar.png) | Same in Arabic; size order fixed by bidi isolates |
| [05-settings-en.png](shots/wave1/05-settings-en.png) | Settings dialog, grouped navigation |
| [06-settings-ar.png](shots/wave1/06-settings-ar.png) | Same in Arabic |
| [07-copy-all.png](shots/wave1/07-copy-all.png) | Transcript toolbar with primary Copy all |
| [08-copy-toast.png](shots/wave1/08-copy-toast.png) | Copy-all confirmation toast |
| [09-export-groups.png](shots/wave1/09-export-groups.png) | Export dialog with four labelled format groups |
| [10-error-model.png](shots/wave1/10-error-model.png) | Model-kind error: contextual primary action, log behind disclosure |
| [11-error-details.png](shots/wave1/11-error-details.png) | Same dialog with details expanded |

## 5. Verification

Run from `app/desktop` on 19 Nov 2026:

| Check | Command | Result |
| --- | --- | --- |
| Build (paraglide → tsc → vite) | `pnpm build` | pass, exit 0; Vite built in 1m 19s |
| Test suite | `pnpm test` | **34 files / 207 tests passed**, exit 0 |
| i18n parity | key count in `i18n/desktop/en-US.json` and `ar-IQ.json` | 786 keys each, no missing Arabic keys |
| Docs/metadata guard | `node scripts/seo/check-seo.mjs` | pass after this document landed (see repo CI) |
| Runtime axe audit (WCAG 2.2 A/AA) | workspace headless harness (axe-core 4.14.1, headless Chrome 158) over the dev mock; not shipped in the repo | **35 states / 0 violations**: idle, all 10 Settings sections, export dialog; EN + AR + dark |
| Dialog focus behaviour | same script | focus trap holds (5/5 Tab stays inside); `Escape` closes the settings dialog; focus **restoration** not confirmed in the headless harness |

Not covered by automation: the installed (Tauri) build, real model-download timing, screen-reader
behaviour on Windows (axe cannot see it), and the five-user test below. Those are explicitly the next
evidence to gather.

## 6. Five-user gate (required before Wave 2 and before 4.0)

Operating manual for running it — materials, task cards, printable observation sheet, scoring table and
the appendix template — is [GATE-KIT.md](GATE-KIT.md). The rules below are the source of truth.

Participants: five Iraqi-Arabic speakers who did not see the boards, at least three installing for
the first time. Moderated, think-aloud, ~30 minutes, recorded notes only (no telemetry).

| # | Task | Pass rule |
| --- | --- | --- |
| 1 | Install, reach the model download, then explain what happens to their audio | 4/5 say “stays on this computer / not uploaded”; 5/5 understand the one-time internet need |
| 2 | From an idle screen, open Settings without being told where it is | 4/5 in under 10 seconds; median ≤8s |
| 3 | Finish a transcript and get the full text out | 4/5 use Copy all; none opens Export first by mistake |
| 4 | Reproduce a model error and choose the next step | 3/5 choose the offered recovery; none chooses Reset first |
| 5 | Read the Arabic UI and report anything that looks broken | 0 critical bidi/tracking defects; ≤2 minor findings |

Decision rules:

- **Pass** → start 3.11 Wave 2 and review the 4.0 identity brief for a separate go.
- **Partial** → fix only the failing task, retest with the next five participants; Wave 2 waits.
- **Fail** → stop the sequence and re-open the relevant Q1 family with the council.
- Write the results (anonymised) as an appendix to this file; do not edit the pass rules afterwards.

## 7. Explicitly not in 3.10

| Deferred | Why |
| --- | --- |
| Echo identity (Q3 C): tokens, ink rail, rings, wordmark, artwork | Owner chose it as 4.0; starting it now would mix identity with measurement and break the gate |
| Wave 2 repairs | Q2 answer is “four repairs only” before the gate |
| RTL sidebar mirror / full re-theme | Part of the identity direction, token-level, moves with 4.0 |
| Progress-fill direction in Arabic (fill still grows left→right) | Cosmetic; keep the diff small, measure it in task 5, fix with the 4.0 typography pass |
| English catalogue still says “Vibe” in several strings (Arabic says صدى) | Upstream base-locale debt, not a 3.10 repair; belongs to the 4.0 naming/wordmark pass and one consistent `en-US.json` rename |
| Real-download ETA calibration | Needs the installed build and real model sizes; the UI is ready |

## 8. References

- Boards and recommendation: [README.md](README.md), `00-overview.html` … `04-q4-trust.html`
- 4.0 Echo brief: [../echo-identity-4.0.md](../echo-identity-4.0.md)
- Critique that opened the questions: [../../../docs/UI-UX-REVIEW.md](../../UI-UX-REVIEW.md)
- Copy audit source: [04-q4-trust.html](04-q4-trust.html)
