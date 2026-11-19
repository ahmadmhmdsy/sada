# UI/UX review — Sada desktop app (صدى 3.9.0)

Status: released build reviewed on **2026-11-19** (Asia/Baghdad). The critique findings are open
work for the next two release windows; nothing here changes the shipped 3.9.0 binaries.

| Field | Value |
| --- | --- |
| App version | 3.9.0 |
| Surfaces reviewed | Main window, Settings modal and pages, first-run/setup, dictation indicator, meeting prompt |
| Method | Impeccable critique — dual-agent: assessment A (design review) and B (detector + CDP) isolated, synthesized afterwards |
| Environment | Live Tauri WebView2 app, 800×700 CSS px, DPR 1.25, `lang=ar-IQ`, RTL, light theme |
| Score | **20/40 — Acceptable** (significant improvements needed before users are happy) |
| Snapshot | `.impeccable/critique/2026-11-19T08-51-01Z__desktop-src-pages-main-page-tsx.md` |
| Trend | First run for this target, no trend yet. |
| Council | Qiyas Mode C — 4 core roles + 3 dynamic roles; verdict at the end of this page |

---
Method: dual-agent (A: 5e4e1197-4dab-4fe5-ac43-67cea7eab9bb · B: 6771d271-7493-4b8e-84ec-deae45c1db55)

## Critique — Sada desktop UI (صدى v3.9.0)

*Target: `desktop/src/pages/main/page.tsx` (main window) plus the Settings modal, first-run/setup page, and the two chrome windows. Reviewed live at 800×700 CSS px, lang=ar-IQ, dir=rtl, light theme.*

### Design Health Score

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of System Status | 2 | Single-file transcription shows its only percentage as an 11px sidebar line; the reading pane gets a pulsing bar with no ETA and no live region. Batch runs get "بقي نحو N دقيقة"; the dominant single-file case does not. |
| 2 | Match System / Real World | 3 | Mostly idiomatic Arabic, but الإعدادات / الضبط / الضبط الدقيق name three unrelated things as if related; الوكلاء and المتقدّم assume desktop-tech literacy. |
| 3 | User Control and Freedom | 2 | Settings — the largest modal — has no Escape handler and no focus trap (settings-modal.tsx is a bare fixed inset-0 div). Cancel is otherwise present everywhere. |
| 4 | Consistency and Standards | 2 | Export and Error are Radix dialogs (trap, Escape, aria-modal); Settings is custom. تصدير means "this transcript" or "all finished files" depending on job count. Toaster position is bottom-right while most call sites ask for bottom-center. |
| 5 | Error Prevention | 2 | Disabled primary actions with no adjacent reason (بدء التسجيل needs a model; تفريغ needs a URL). No file-type pre-check before enqueue. Good: destructive actions confirmed natively, managed policy hides forbidden controls. |
| 6 | Recognition Rather Than Recall | 2 | First control a newcomer meets is three icon-only segments (ملف / تسجيل / من رابط) named only by tooltips; Settings is discoverable only at the sidebar footer; the active model is invisible outside Settings. |
| 7 | Flexibility and Efficiency | 2 | Real accelerators exist in the transcript (Space transport, line-to-line editing, playback rate), but no shortcuts for open/record/search/export/settings and no shortcut reference anywhere. |
| 8 | Aesthetic and Minimalist Design | 3 | Disciplined one-column composition, one radius family, aurora only on drag/progress. But minimal has drifted to empty on idle, and the link panel ends in five social logos plus "+1000 مصدر آخر" — marketing inside a tool. |
| 9 | Error Recovery | 1 | Every failure — missing model, unsupported codec, GPU OOM, full disk — gets "خطأ" + "حدث خطأ برمجي." + a raw LTR log + a filled primary "إعادة تعيين صدى" + a GitHub issue link requiring internet and an account. The copy control is an SVG with onMouseDown: not focusable, no name. |
| 10 | Help and Documentation | 1 | No help entry point, onboarding, glossary, or in-app docs. Tooltips and release notes are the entirety of it. |
| **Total** | | **20/40 (50%)** | **Acceptable — floor of the band. Two 1s (error recovery, help) drag down a shell that is otherwise competent and, in the transcript surface, genuinely good.** |

### Design Specificity Verdict

**LLM assessment: authored for the act of transcription; borrowed for everything around it.** The shell is an explicit clone, and the code says so: globals.css:115 "ChatGPT-style neutrals", layout.tsx:86 "Claude-desktop style" sidebar, recents-sidebar.tsx:425 "Codex-style: the wordmark gets its own row", page.tsx:107 "ElevenLabs style" player. Blur the text on the idle window and it is indistinguishable from any AI chat client: wordmark top-right, "new" row beneath, recents list, settings pinned to a collapsible footer, one centered column with a dashed target. Nothing in the composition refers to sound, Arabic, or Iraq; the primary accent is stock SaaS blue (#2563eb) and the only chroma is the inherited aurora.

What *is* authored: the transcript instrument (timestamp-as-play-button, gradient listening wash instead of a selection block, Space transport, Arrow/Tab line-to-line editing), the Arabic/bidi foundation (bundled IBM Plex Sans Arabic, html[lang^=ar] corrections, unicode-bidi isolation for timestamps and numbers), and the copy voice ("تظهر هنا ملفات التفريغ التي تنشئها"، "يحدث هذا مرة واحدة فقط."، "ليس الآن") — idiomatic, not translated English.

The specificity failure is that the product's whole differentiator — *this never leaves your device* — appears in one sentence three clicks deep, behind a gear in a footer that disappears with the sidebar. The most distinctive true thing about Sada is the least visible thing in its interface.

**Deterministic scan.** 62 detector rules available; source scan of `desktop/src` (1,725 files, 1,499 of them generated paraglide modules) returned 1 finding: `overused-font` at `desktop/src/lib/transcript-export.ts:128` (Roboto inside the generated standalone HTML transcript export — a downloaded document, not the app shell). It is a false positive as a UI-slop signal, with a real nuance: Windows has no Roboto, so the exported HTML falls back to Arial and its Arabic runs lose IBM Plex Sans Arabic. CDP scan of the running main window (800×700, DPR 1.25) returned 1 finding: `script-error` — an uncaught promise rejection, "Command plugin:window|set_theme not allowed by ACL". That is a real bug, not a visual-design blocker: providers/preference.tsx:404 calls void getCurrentWebviewWindow().setTheme(theme) in a synchronous try/catch that cannot catch the rejection, and src-tauri/capabilities/main.json grants core:window:default but not core:window:allow-set-theme. The sibling meeting-prompt-window handles the same call with .catch(() => undefined).

**Visual overlays.** No reliable user-visible overlay: this is a Tauri WebView2 desktop app with no [Human] browser tab. The CDP scan attached to the live page, did not navigate, resize, or inject, and left it as found. The fallback signal is the detector's CDP finding plus direct DOM/computed-style probes (contrast, font sizes, focus indicators, letter-spacing).

### Overall Impression

The engineering craft is real; the product's confidence is not. Sada gives away its most valuable truth (offline, private, Arabic-first) and asks a first-timer to decode icons, wait through an opaque download, and face nine file formats at the finish line. The transcript reading surface is the work of someone who edits speech for a living; the shell around it is the work of someone who kept a chat app's clothes. The single biggest opportunity is not a redesign: it is to make trust (privacy, local processing, honest progress) and the dominant end action (copy/share) first-class on the existing composition.

### What's Working

1. **The transcript reading surface is a real instrument.** Timestamp gutter doubles as a play button (aria-label="تشغيل من هنا", title = the time); the spoken line gets a gradient wash that reads as lighting rather than selection; Space toggles playback; click-to-place-caret editing carries drag-selection into the line editor; Enter/Tab/Arrow move line to line. Most competitors ship a textarea; this ships an editor for dictation.
2. **The idle composition is disciplined.** One 640px optical column, pb-[30vh] to lift it above true centre, a fixed 220px slot so the source pills never move, and an aurora that ignites only while dragging. It survives 800×700 without clipping.
3. **The Arabic/bidi foundation is above category norm.** Bundled Plex Arabic instead of a webfont (matching the no-phone-home contract), Arabic line-height/tracking corrections, and unicode-bidi isolation so 12:04 and 3.20 do not scramble inside RTL lines — a fix most Arabic apps never make.

### Priority Issues

#### [P1] Every failure tells the user the same lie, and offers a factory reset as the cure
`error-modal.tsx:40-51`. Missing model, unsupported m4a, GPU OOM, full disk: title "خطأ", body "حدث خطأ برمجي." (modalErrorBody), a read-only dir="ltr" textarea of the raw error, then a filled primary "إعادة تعيين صدى" (resetApp) and an outline "الإبلاغ عن مشكلة" that opens GitHub — requiring internet and an account on an offline-first app. This audience is offline, Arabic, and not going to file a GitHub issue.
**Why it matters:** being told "a programming error occurred" after a failed 47-minute meeting, with factory reset as the fix, reads as data loss — and resetting does not fix a missing model either.
**Fix:** map failure classes to three sentences that each name cause and next step (missing model → "تنزيل النموذج"; unsupported format → "تحويل الملف" + accepted list; disk full → path to free space). Demote reset to a text link under "لا يمكن حل المشكلة؟". Replace the SVG copy control with a real button labelled "نسخ التفاصيل". Use the same strings in the dictation HUD, which currently truncates errors into a 224px pill. **Suggested command:** $impeccable clarify + $impeccable harden.

#### [P1] The finish line is a 16-control dialog, and copying is locked inside it
`transcript-export-dialog.tsx`: nine formats (TXT MD SRT VTT HTML JSON CSV DOCX PDF), five option rows (المحتوى، المظهر، اتجاه النص، الطوابع، المتحدثون), plus نسخ and حفظ. نسخ is a secondary outline button that disappears entirely for PDF, DOCX and HTML (footer condition format !== html/docx/pdf at :407). There is no copy-all anywhere else in the app.
**Why it matters:** most meeting-notes users finish in WhatsApp or Word, not a file. The dominant end action is three clicks deep and invisible for three formats; nine options exceed the ≤4 decision rule before the user has chosen anything.
**Fix:** put "نسخ الكل" next to تصدير in the transcript toolbar (Ctrl+Shift+C). Keep all nine formats — power users and batch export rely on them — but default to "نص عادي" and tuck PDF/DOCX/HTML/JSON/CSV behind "صيغ أخرى". Move المظهر/اتجاه النص into a collapsed "خيارات متقدمة" row: the user is finishing, not configuring. **Suggested command:** $impeccable distill.

#### [P1] الإعدادات: one door, and it disappears; then the modal is not a modal
`recents-sidebar.tsx:485-493` is the only in-window path to Settings; the header strip in layout.tsx:135 is empty and components/app-menu.tsx (the only settings-gear design) is dead code. Collapse the sidebar and Settings is unreachable — no Ctrl+, no menu bar. When it opens it is a fixed inset-0 div: no role="dialog", no aria-modal, no focus trap, no Escape, no return focus; Tab leaks behind the overlay. Ten destinations, no search, four unlabeled runs ("split into visually separated runs — no group headings", settings/page.tsx:57). Verified by a live Tab/Escape pass.
**Why it matters:** a destination that disappears when you tidy the layout is a navigation bug; a modal that leaks keyboard focus while painted at z-50 is a reverse keyboard trap.
**Fix:** move الإعدادات into the empty header (or bind Ctrl+,), keeping the footer row as a second door; port the modal onto the same Radix Dialog the export and error surfaces already use (Escape, trap, aria-modal, return focus); add real group headings (عام · التفريغ · الصوت · متقدم) now, a search field later; give the settings switch — the app's main control — a visible label association and an outline instead of a 1.25:1 track. **Suggested command:** $impeccable harden + $impeccable document.

#### [P1] Arabic is being set with Latin typography, because the RTL fix list names classes instead of rules
`globals.css:629-649` correctly zeroes tracking for Arabic — but only for the named utilities .tracking-tight/-tighter/-wide/-wider/-widest and h1–h3. Every arbitrary value bypasses it: 22 tracking-[…] occurrences in the desktop source. Measured live: the eyebrow "الأخيرة" computes letter-spacing 0.88px (0.08em at 11px) and the wordmark "صدى" computes -0.51px (-0.03em), compressing the joins of the product's own name. Affected: الأخيرة، قيد التنفيذ، خيارات النموذج، يعمل مع، الملفات · 2 من 3، سلوك التطبيق، المساعدة والمجتمع، recording device labels, and the tracking-[0.12em] version row.
**Why it matters:** this is the flaw an Arabic-first app cannot have. At 11px, added tracking on a connected script costs legibility on the labels users scan most — and contradicts the file's own comment that Arabic joins must stay untouched.
**Fix:** invert the rule: set letter-spacing: 0 for all Arabic text via html[lang^=ar] *, then opt tracking back in only for Latin runs (.font-mono). Remove uppercase from .eyebrow: it is a no-op in Arabic and signals a Latin class ported wholesale. **Suggested command:** $impeccable typeset.

#### [P2] First run and the wait are opaque; configuration dead-ends are silent
`sada-first-run.png`: eyebrow "الإعداد", 28–36px "جارٍ تنزيل النموذج…", a 1.5px bar, "2%", "يحدث هذا مرة واحدة فقط.", "إلغاء". No model name, size, speed, remaining time, what happens next, or that this is the only network step; the manual-download escape hatch exists only as a tooltip. During transcription, a single file gets no ETA even though batchTimeLeft exists, and the pane offers "سيظهر النص هنا قريباً…" over a pulsing pill while the CPU pins — the most likely reading is "it is uploading my meeting". Record and link panels then end in disabled primary buttons ("بدء التسجيل", "تفريغ") with no adjacent reason.
**Why it matters:** the highest-stakes screens are the thinnest. Trust is decided before the first transcript exists.
**Fix:** give first-run the model name, download size, estimated time, and a sentence on what happens next; reuse the batch ETA for single files; show progress in the reading pane, not only the sidebar, with role="status" and a polite aria-live; put the missing-model explanation in the model prompt adjacent to the disabled action, or replace the disabled button with an enabled "تنزيل النموذج". **Suggested command:** $impeccable onboard.

### Persona Red Flags

**Alex (impatient power user).** Nine focusable controls on idle and zero global shortcuts: no Ctrl+O, no Ctrl+F, no Ctrl+,, no shortcut sheet. He collapses the sidebar for reading width and loses Settings entirely. He wants to compare two models on one file; the active model is invisible on the main screen, so every comparison is a 10-item-settings round trip. He will like: drop-to-append into a running session, auto-export, the batch card with "بقي نحو N دقيقة".

**Sam (screen reader / keyboard, 200% zoom).** Settings opens with no role="dialog", no aria-modal, no focus trap; Tab walks out behind the overlay and Escape does nothing. In the transcript, every line is a role="textbox" span that does nothing until Enter mounts a real textarea, and every line gutter is a button named "تشغيل من هنا" — a 400-line meeting yields 400 identically named buttons. No aria-live for progress, completion, or per-file errors. The language pill's focusable button carries outline-none with no ring, verified by a real Tab pass; the main settings switch track is #e6e6e6 on white (1.25:1), 32×18px, with a non-clickable div label row. At 200% zoom an 800px window becomes 400 CSS px: the 288px sidebar plus padding leaves under 100px for the drop zone and nothing collapses.

**Huda (Arabic-speaking Windows user, 34, Baghdad; laptop, Arabic keyboard, records meetings on her phone; not a power user).** She opens Sada, sees "صدى" and three icon pills she must hover to decode; she ignores them and clicks the dashed box, which works. She drops a 47-minute m4a: no confirmation of what was accepted, no duration, no "we will not upload it"; the only progress is an 11px sidebar line at 8%. She waits, unsure whether closing the window is safe. The transcript is good. To send it on WhatsApp she finds تصدير and meets nine formats; the default نص عادي and حفظ work, but نسخ — the one-click path she wanted — is an outline button inside a dialog she was afraid of. If anything fails she gets "حدث خطأ برمجي" and a reset button, and she will not open a GitHub issue in English. Nothing ever tells her the one thing that would make her trust the app with a client meeting: that the transcript never leaves her device.

### Minor Observations

- **Real bug from the detector:** uncaught rejection "Command plugin:window|set_theme not allowed by ACL" (providers/preference.tsx:404; src-tauri/capabilities/main.json lacks core:window:allow-set-theme). One-line fix: add the permission or .catch(() => undefined) as meeting-prompt-window.tsx already does.
- docs/media/sada-settings.png still stamps SADA 3.2.2; the live build shows 3.9.0 (bookkeeping; regenerate during the next asset pass).
- Version row that opens release notes: 10px mono at text-muted-foreground/60 ≈ 2.4:1 contrast with a hover-only arrow — the least legible text in Settings is a navigation affordance.
- components/app-menu.tsx and components/advanced-options-button.tsx are unused; the latter still hard-codes "Advanced Options", a tripwire for the repo's no-hard-coded-strings invariant if revived.
- `file-queue.tsx`: a role="button" span with its own key handler nested inside a button — invalid nesting, doubled activation on Enter, no Space handling.
- `meeting-prompt-window.tsx` auto-dismisses after 10s with no visible countdown; its two source chips are 28px tall with 11px text.
- `dictation-indicator-window.tsx` is the only surface outside the token system (bg-zinc-950, red-500, emerald-400, blue-400); errors truncate into a 224px pill with no way to expand. aria-live absent.
- `app.tsx:70` Toaster is bottom-right under the player bar and can stack with the model-download card; several call sites request bottom-center.
- `idle-hero.tsx` ends the link panel with five social logos and "+1000 مصدر آخر" — the most landing-page moment in the product, inside a tool.
- No `.impeccable/critique/ignore.md` existed for this run, so no findings were suppressed.

### Questions to Consider

1. If offline-and-private is the product, why is the one sentence that says so hidden behind الإعدادات → الخصوصية — and what would you delete from the idle window to put an accurate version of it under the drop zone?
2. The sidebar is pinned to the physical left in every locale (layout.tsx:132, direction: ltr) while its content is RTL. Defend that to an Arabic user arriving from Word or Explorer — or admit it is upstream's layout that was never re-decided.
3. Is تصدير the end of the product or a power tool? If most transcripts end in WhatsApp, why is نسخ inside a nine-format dialog — and absent for PDF, DOCX and HTML?
4. What is الضبط to someone who has never met a Whisper model — and why do الإعدادات / الضبط / الضبط الدقيق mean three unrelated things inside one app?

### Run Notes

- **Target slug:** desktop-src-pages-main-page-tsx (resolved by critique-storage slug).
- **Ignore list:** none — no `.impeccable/critique/ignore.md` existed before this run.
- **Assessment independence:** two isolated workflow agents. A (design review) received source, live DOM, and screenshots and was told not to run the detector; B (detector) was told not to see A. Both returned before synthesis; detector findings entered the parent context only after A completed.
- **CLI detector:** source scan 1,725 files (regex-only: .ts/.js/.tsx/.css), 1 finding (overused-font, export template) — undercount stated by the tool; rendered-element rules did not run. CDP scan on the live main window: 1 finding (script-error, theme ACL).
- **Browser visibility:** CDP attached to the running Tauri WebView2 app; main window 800×700 CSS px, DPR 1.25; secondary windows (dictation indicator 280×64, meeting prompt 304×152) measured but not scanned. Settings panel skipped by B to preserve state; it was inspected earlier by the parent and Assessment A.
- **Overlay injection:** not applicable/not attempted — desktop WebView2 has no browser tab; no [Human] overlay exists for this run.
- **Live server:** none started, none to stop.
- **State preservation:** window returned to the idle main screen, light theme, no dialog, active element BODY; verified after the CDP scan.
- **Temp files:** agent probe scripts and screenshots were written under %LOCALAPPDATA%\Temp\sada-ui\; left in place as evidence, not part of the repo.

---

## What remains an owner decision

These are not agent tasks; they change scope, wording or product direction and need the maintainer:

1. **Scope of the first fix window.** The council caps Wave 1 at one release window; confirm that
   no feature work outranks the trust, copy-first, settings and Arabic fixes.
2. **The two trust sentences.** The exact Arabic wording is a product voice decision. The required
   meaning: the model downloads once; after that transcription runs on this PC and no audio or text
   is uploaded. Anything stronger than that is false.
3. **Visual identity.** The council refused a re-theme for 3.10. Decide whether an authored identity
   (beyond the cloned shell) is a later goal worth a real design brief, or out of scope for the fork.
4. **RTL sidebar.** Approve or reject the 5-user test as the deciding evidence before the sidebar is
   mirrored; the change touches layout utilities and screenshots, not just CSS direction.
5. **Screenshot regeneration.** Regenerating docs/media images requires a live 3.9.0+ build and
   replacing committed assets; owner sign-off avoids accidental drift during the fix waves.

Visual prototypes for all four decisions — with impact, effort, risk, long-run notes and a recommended
bundle — are in [docs/design/ui-decisions/](design/ui-decisions/). Open its `index.html` to compare
the options side by side.

## Council review — Qiyas (Mode C, merged)

**Question put to the council:** Sada v3.9.0 scores 20/40 on the Impeccable critique. Which findings must be fixed, in what order, and what should be refused — for a solo maintainer shipping an offline, Arabic-first Windows app with no telemetry and release capacity measured in days, not sprints?

### Seated roles

| Role | Qiyas duty | Signature question |
|---|---|---|
| **The Expert** — composite Arabic-first desktop product and localization specialist | *Takhrij al-Manat*: extract why a precedent worked, forecast second-order effects | Why did it work, and what breaks in 6–24 months? |
| **The Engineer** | *Al-Far'*: every proposal must carry a precedent and a stated cause | What is the precedent, and what is the cause? |
| **Devil's Advocate** | *Al-Qawadih*: attack the cause, not the wording | Where does the cause break? |
| **The Naive User** — Arabic-speaking Windows user who hates complexity and reads everything in the worst possible way | *Tahqiq al-Manat*: does the cause exist in the real user? | What is in it for me, and why would I bother? |
| **The Maestro** | Silent until the stop condition; rules only on what survived | — |

Dynamic roles seated for this hearing (role cards):

```
Role: Accessibility Auditor
Mandate: keyboard, screen reader, zoom and focus correctness in every surface.
Signature question: Can Sam finish this without a mouse, at 200% zoom, with a screen reader?
Qiyas tool: reality check + material difference. Red line: any control reachable only by hover or mouse.

Role: Trust & Privacy Officer
Mandate: truth of every offline/privacy sentence, and the no-telemetry, no-account posture.
Signature question: Is the claim true at first run, not only after setup?
Qiyas tool: invalid premise. Red line: an absolute "never leaves your device" while the first run downloads a model.

Role: Release Maintainer
Mandate: capacity, regression surface, release risk and documentation debt.
Signature question: What does this cost, what does it break, and who updates the screenshots?
Qiyas tool: second-order effect. Red line: a redesign or new dependency that buys no verified user outcome.
```

### Global invariants (Expert)

1. **Trust is the product.** Sada's only defensible differentiator is local, offline, Arabic-first processing. Any interface that hides that fact, or states it inaccurately, fails the product, not just the heuristic table.
2. **The finish line dominates.** Transcription ends when the text is somewhere useful — clipboard, WhatsApp, Word. A file-format taxonomy is a power tool, not the primary ending.
3. **Arabic script integrity is non-negotiable.** No letter-spacing, no uppercase, no Latin typography ported wholesale. This is the one visual class of defect an Arabic-first app cannot ship.
4. **Global destinations must survive layout changes.** Settings cannot depend on a sidebar being open; a modal must behave like a modal.
5. **No telemetry means no instrumented test.** Evidence has to come from moderated, consented hallway tests and observable behavior — not analytics.
6. **Capacity is the binding constraint.** Three small release windows exist before the next feature cycle; anything that consumes them without moving a metric is refused.

### The hearing

**Round 1 — the first draft.**

**The Engineer:** Proposal: a 3.10 "design refresh". Re-theme the idle window away from the chat-shell look, mirror the sidebar to the right in RTL, move Settings into a proper modal, and cut export to three formats. Precedent: the 2024 Sonos app redesign — a cleaner shell that shipped without the capabilities users relied on. Cause: removing complexity raises perceived quality. Four changes, one release.

**The Naive User:** Fatal flaw — I do not care that it is prettier. Last week I dropped a meeting, could not tell whether it was uploading, and when I found the transcript I could not find a copy button. You are debating a sidebar while I am trying to send text to my boss. (Reality check: the cause "a cleaner shell raises quality" does not exist in this user.)

**Devil's Advocate (counter-case + non-causation):** Sonos is a negative precedent, not a positive one — their redesign was rejected precisely because it replaced a stable, feature-complete app with a prettier but less capable one. You have inverted the cause: a visual refresh *does not* create trust. Meanwhile the critique says the shell is a clone, which is a taste judgment, not the conversion problem. Drop the refresh.

**The Expert (second-order effect):** Two things will get worse, not better, on the current path. Model downloads will keep growing (multi-GB is already normal), so an opaque first run becomes a bigger abandonment risk each release. And Windows RTL conventions are becoming more visible to Arabic users through Office and Explorer; the longer the app keeps a physical-left dock, the more it reads as a ported app. The clone aesthetic is not the emergency; the invisible trust and the finish line are.

**The Engineer — I revise:** Drop the re-theme. Keep the shell. Spend the three windows on: (a) truthful trust surfaces, (b) the copy-first finish line, (c) a settings modal that behaves like one, (d) the Arabic tracking leak. Sidebar mirroring moves to a decided test, not this release. Cutting formats is withdrawn — batch and office users depend on them.

**Round 2 — the trust claim.**

**The Engineer:** Add one line under the drop zone: "لا يغادر أي شيء جهازك" (nothing leaves your device). Precedent: Signal prints the end-to-end-encryption notice inside the conversation, at the point of the sensitive act. Cause: a trust statement placed at the moment of risk lowers hesitation.

**Trust & Privacy Officer (invalid premise):** The sentence is false at first run. The app downloads a multi-GB model before it can transcribe; on a clean install the user is on the network. An absolute claim invites exactly the distrust it is meant to prevent, and on an MIT project the correction will be public. Also: "nothing leaves" cannot be printed while the app offers "open a link" sources without an explicit scope.

**Devil's Advocate (material difference):** Signal encrypts every message; it does not need to download a model. The precedent's cause assumes the sensitive act is online. Here the network step is one-time and visible; the invariant has to be scoped, not hidden.

**The Engineer — I revise:** Two sentences, both true: on first run, "يُنزَّل النموذج مرة واحدة ثم يعمل صدى دون إنترنت"; in the idle state, "التفريغ يتم على هذا الجهاز — لا يُرفع أي صوت أو نص". Place the second under the drop zone, not behind الإعدادات. Precedent retargeted to on-device labels: the cause is "honest local-processing statement at the point of use", not "absolute privacy slogan". The absolute sentence is removed.

**The Naive User:** Better. Now I know the big download is expected and that my meeting is not uploaded. But do not put a paragraph there; one line under the box, small, before I drop.

**Round 3 — the finish line.**

**The Engineer:** Add "نسخ الكل" in the transcript toolbar, keyboard shortcut Ctrl+Shift+C. Precedent: Otter puts copy in the transcript toolbar; Google Docs and Notion treat copy as a first-class action. Cause: the dominant end action gets a first-class affordance. Then reduce the export dialog to TXT/MD/SRT.

**Devil's Advocate (counter-case):** The dialog is not the problem you think. Users who already use batch export and DOCX for reports will read removal as regression, and the fork inherited those formats. The critique itself says "16 controls"; its fix is progressive disclosure, not deletion.

**Accessibility Auditor (reality check):** And the dialog's copy button is secondary, disappears for PDF/DOCX/HTML, and announces nothing to a screen reader when it succeeds. A toolbar copy button must not inherit that: it needs a live confirmation ("تم النسخ") and must copy the whole transcript, not the page selection, without ambiguity.

**The Engineer — I revise:** Keep all nine formats; group them: primary row for نص عادي / Markdown / SRT, everything else behind "صيغ أخرى". Add copy-all to the toolbar for every format; add an explicit "نسخ المحدد" only when a selection exists; announce success through a polite live region. The "cut to three formats" branch is dropped.

**Round 4 — the settings door and the Arabic leak.**

**The Engineer:** Port Settings onto the Radix dialog already used by export and errors. Precedent: the WAI-ARIA Authoring Practices dialog pattern — Esc, focus trap, aria-modal, return focus. Cause: modal semantics are the API contract of a modal. Add a header gear or Ctrl+, so the door survives a collapsed sidebar. And fix Arabic tracking by inverting the CSS rule.

**Accessibility Auditor (fatal flaw in the first draft):** A Radix port alone does not fix the navigation problem — reopening the modal from a footer that stays behind a collapsed sidebar is still a mouse-only dead end. The header door and Ctrl+, are the fix; Radix is the correctness fix. Also: the settings switch's visible label is a non-clickable div and its track is 1.25:1 — port the markup, not just the container.

**The Expert (takhrij):** The Arabic rule is the cleanest case in the whole review: the existing correction lists named utilities, so 22 arbitrary values bypass it. The cause is "Arabic joins must not be tracked", and the correct implementation is the inverse rule (zero by default for Arabic, opt in only for Latin mono), not a longer blacklist. Precedent: Windows and Office Arabic UI never track Arabic; Arabic body text is set tight. Strip the incidental Tailwind class list.

**Devil's Advocate (second-order):** Inverting the rule may collide with the transcript's monospace timestamps and the brand wordmark. Test the four surfaces that intentionally use Latin spacing.

**The Engineer — I revise:** Apply zero tracking to Arabic, whitelist the mono font and explicitly Latin runs, and delete `uppercase` from the eyebrow (it does nothing in Arabic and signals a Latin class ported wholesale). Verify the 22 sites and the wordmark at 4× zoom.

**Round 5 — what the council refuses.**

**The Release Maintainer:** The revised package is three release windows. Wave 1 must fit in one day; if it does not, the RTL mirror and help panel move out, not the a11y and trust fixes. Screenshot regeneration is not optional — docs/media/sada-settings.png still says 3.2.2 and is the image a new user sees on GitHub.

**Trust & Privacy Officer:** One more refusal: do not add a badge, a rating, or a third-party trust seal to "prove" privacy. The honest sentence under the drop zone is the trust surface; anything else is theater.

**Devil's Advocate:** I will accept the revised package with one condition: the council must name a falsification test. Otherwise this is a heuristics document, not a product decision.

**The Expert — stop condition met.** The first draft fell, the revisions survived targeted objections, and the remaining disagreement (sidebar mirroring) is a testable difference, not a debate.

### Maestro verdict

| # | Branch | Verdict | Asl → 'Illa (cause) | Constraint imposed by the objections |
|---|---|---|---|---|
| 1 | Truthful trust line under the drop zone + first-run scope sentence | **Survived** | Signal's encryption notice / on-device labels → trust statement at the point of the sensitive act | Must be two accurate sentences; no absolute "never leaves"; model download named with size |
| 2 | "نسخ الكل" in transcript toolbar (Ctrl+Shift+C) with live confirmation | **Survived** | Otter / Google Docs → dominant end action gets a first-class affordance | Whole transcript by default, "copy selected" only when a selection exists; polite aria-live on success |
| 3 | Cut export to three formats | **Dropped** | — | Power and batch users; the fork inherited formats |
| 4 | Export dialog progressive disclosure (keep 9, group primary 3 + "صيغ أخرى", copy everywhere) | **Survived** | GOV.UK / Otter → reduce the first decision to ≤4 without deleting capability | Copy must appear for PDF/DOCX/HTML too |
| 5 | Failure taxonomy: 4 user-action buckets, cause + remedy, copy-details button, reset demoted to text link | **Survived** | VS Code error notifications → remedy adjacent to cause | Unknown errors fall back to retry/details, never to reset; same copy in the HUD |
| 6 | Settings: header door + Ctrl+, + Radix dialog semantics + group headings | **Survived** | WAI-ARIA APG dialog / VS Code & Slack settings shortcuts → global destination independent of layout; modal contract | Switch label must be clickable and contrast fixed; search deferred |
| 7 | Full visual re-theme / new identity | **Dropped** | Sonos 2024 redesign (negative) → shell aesthetics did not create trust; removal of capability did damage | No rebrand before trust, a11y and copy-first finish ship |
| 8 | Mirror sidebar to the right in RTL | **Suspended on test** | Windows Arabic Explorer nav pane / Arabic Wikipedia → start-edge reading gravity | Test with 5 Arabic users first; keep caption-button area clear; stage separately from P1 fixes |
| 9 | Invert Arabic tracking rule + remove uppercase eyebrow | **Survived** | Windows/Office Arabic UI → connected script must not be tracked | Whitelist mono and Latin runs; verify 22 sites and wordmark at 4× zoom |
| 10 | First-run transparency (model name/size/ETA/what next) + single-file ETA + aria-live progress | **Survived** | LM Studio / Ollama model pulls → long one-time download needs scope, progress and a next step | No invented ETA when unknown — show elapsed/pending; reuse batchTimeLeft |
| 11 | Replace disabled primary actions with contextual enabled CTAs | **Downgraded** | GOV.UK disabled-button guidance → hidden prerequisite is a dead end | Blanket enabling is wrong; each panel gets the specific action ("تنزيل النموذج", "الصق رابطاً صالحاً") |
| 12 | In-app help / shortcuts panel / offline FAQ entry | **Downgraded** | macOS Help menu / VS Code shortcut sheet → discoverability without a website | Wave 2 only; keep it one screen, offline, maintained from README docs |
| 13 | Fix set_theme ACL uncaught rejection | **Survived** | Sibling meeting-prompt-window already handles it → catch the promise, or grant the permission | Ship today; it is a real console defect, not a design decision |
| 14 | Privacy badges / trust seals / ratings | **Dropped** | — | Violates the honest, no-third-party posture |

### Step Zero — the falsification test

The cheapest test that could kill the main thesis ("the problem is trust and the finish line, not the visual shell"): **five Arabic-speaking Windows users, 30 minutes each, moderated, consented, no telemetry.** Run it on the installed 3.9.0 build before Wave 1 ships, and again after Wave 2.

| # | Task | Measure |
|---|---|---|
| T1 | Show the idle window for 5 seconds, then hide it: "ما هذا التطبيق؟" | Says transcription/dictation (not chatbot) without prompting |
| T2 | Drop a 10-minute Arabic m4a, then "أرسل النص إلى مديرك على واتساب" | Time and path to clipboard; whether the user finds نسخ inside the export dialog |
| T3 | Collapse the sidebar, then "افتح الإعدادات" | Reaches Settings without help |
| T4 | Trigger the missing-model error, then "ماذا ستفعل؟" | Names a next step or says "أعيد المحاولة / أنزّل النموذج"; does not say "أعيد تعيين التطبيق" |

| Result after Wave 1 | Reading | Action |
|---|---|---|
| ≥4/5 pass T1, ≥4/5 reach copy in ≤30 s, 5/5 reach Settings | Trust thesis confirmed; shell is not the blocker | Continue Wave 2 (taxonomy, progress, RTL test) |
| T1 passes but copy stays buried | Finish-line thesis partially wrong — users find it | Keep the copy CTA but stop further export work; investigate discoverability instead |
| ≥2/5 ask "هل يُرفع هذا؟" before T1/T2 | Trust visibility is the real blocker | Promote the trust line to the first-run screen and idle headline, not just under the box |
| 3+/5 fail T3 | Navigation is the blocker | Wave 1 header door + Ctrl+, before anything else |

### The solution (what the council would ship)

**Wave 0 — today (minutes).** Fix the set_theme rejection: either add `core:window:allow-set-theme` to `src-tauri/capabilities/main.json` or `.catch(() => undefined)` at `providers/preference.tsx:404`, mirroring `meeting-prompt-window.tsx:91-93`. Verify the console is clean on a fresh launch.

**Wave 1 — 3.10, one release window (target 2026-11-22).** Trust, finish line, a11y, Arabic:

- Two accurate trust sentences (first run: once-only download + size; idle: transcription is local; no absolute claim).
- "نسخ الكل" toolbar button + Ctrl+Shift+C + live confirmation; copy available for every export format.
- Settings: Radix dialog semantics; header door and Ctrl+,; four group headings; clickable switch label; contrast fix.
- Arabic tracking inversion with mono/Latin whitelist; delete `uppercase` from the eyebrow.
- Source chooser: visible words (or label + icon) instead of tooltip-only icons; language-pill visible focus ring.
- First-run: model name, download size, what happens next; single-file ETA and aria-live progress in the reading pane; disabled-action explanation adjacent to the control.
- Real copy-details button in the error modal; reset demoted; dead code removed; nested button in `file-queue.tsx` fixed.

**Wave 2 — 3.11 (target 2026-11-29).** Error taxonomy end to end; export grouping (all nine kept); contextual enabled CTAs; help/shortcuts single screen; version row contrast; regenerate docs screenshots (3.9.0+, including the settings image that still says 3.2.2); RTL sidebar test and, if it passes, the staging decision.

**Wave 3 — measure (target 2026-12-05).** Re-run the five-user test; re-run `$impeccable critique` on the same target and compare the trend. Escalate or stop per the table below.

### Continue / kill metrics

| Metric | Threshold to continue | Decision date |
|---|---|---|
| Hallway task success | ≥4/5 complete T2 without help | 2026-11-22 (Wave 1) |
| Time to clipboard | ≤30 s median | 2026-11-22 |
| Trust comprehension | ≥3/5 can state "it runs on my PC" unprompted after Wave 1 | 2026-11-22 |
| Settings reachability | 5/5 reach Settings with sidebar collapsed | 2026-11-22 |
| Re-critique score | ≥28/40 on the same target | 2026-12-05 |
| Error comprehension | ≥4/5 name a remedy at T4 | 2026-12-05 |

**Kill rule:** if T1 already passes ≥4/5 and the privacy question never appears, the visual-clone finding is cosmetic — deprioritize the RTL mirror and help panel, and stop spending release windows on shell work. If any P1 fix does not move its metric by 2026-12-05, it reverts to a design decision rather than more polish.

### Risks and mitigations

- **Privacy overclaim (Trust & Privacy Officer).** Any absolute sentence will be false on first run. Use the scoped two-sentence wording and test it with the five users; no badges.
- **RTL mirror regression (Release Maintainer).** The layout mixes physical left/right utilities and a fixed toggle; stage separately, keep caption-button clearance, test at 800×700 and 200% zoom.
- **Modal port regressions (Accessibility Auditor).** Radix fixes semantics only if focus return and switch labeling are also wired; include the keyboard pass in the same PR.
- **Fake precision on ETA (Engineer).** When speed is unknown, show elapsed time and a pending state, not an invented "دقيقتان".
- **Test bias (Accessibility Auditor).** Five acquaintances over-represent the maintainer's circle; recruit at least two non-technical Arabic speakers and record consent in writing.
- **Docs drift (Release Maintainer).** Screenshot regeneration and version references are release-gating, not follow-up; the 3.2.2 stamp is proof of the failure mode.
- **Scope creep (Maintainer).** Wave 1 is capped at one release window; if it overflows, move the help panel and RTL mirror out — never the a11y and trust fixes.

### First action (today)

1. Clear the console: fix the set_theme ACL rejection and verify a fresh launch logs zero exceptions.
2. Then open the copy-first PR: toolbar "نسخ الكل" with Ctrl+Shift+C and a polite confirmation.
3. Book the five 30-minute hallway sessions for 2026-11-22; the test protocol above is the acceptance script.
