# Echo identity — 4.0 direction brief

Status: **direction brief — not implemented in 3.10 or 3.11.** The token layer from this brief landed on master as a non-shipping preview behind the build flag `VITE_ECHO_PREVIEW=true` ([#83](https://github.com/alshahia/sada/pull/83), merged 2026-11-23 as `83e464a`); default builds are unchanged and nothing from this brief is in a release. The rest of the direction (shell, rail, wordmark, in-app motif, dark theme) has not been implemented.
Owner decision (19 Nov 2026): Q3 → **C · هوية 4.0 — «الصدى»**. The full Echo identity is the 4.0
release direction, starting only after the five-user measurement gate on 3.10 (see
[DECISIONS.md](ui-decisions/DECISIONS.md)). No token, layout or logo change from this brief ships in
3.10; 3.10 keeps the borrowed Vibe shell and adds only truth-only copy and the four Wave-1 repairs.

The visual reference is the third window of [03-q3-identity.html](ui-decisions/03-q3-identity.html);
this document turns that prototype into an implementable direction without pretending it is a spec.

## 1. Positioning sentence

> صدى يحتفظ بما قيل. Arabic speech-to-text that runs on this computer, with no account and no upload.

The name is the idea: the voice ends, the echo remains. Every identity decision should serve one
feeling — *the recording is gone, the writing stays here* — and nothing in the shell should suggest a
chat app, a cloud service, or a subscription.

What the identity is **not** (from the board): no logo-only rebrand, no new icon pipeline, no font
licensing. It is the decisions a user feels on every screen — direction, accent, density, and one
recognisable motif.

## 2. Motif system

The echo is drawn as **concentric arcs that decay from a solid centre**. Three uses, no more:

| Use | Asset | Rule |
| --- | --- | --- |
| Wordmark | echo glyph + «صدى» | glyph sits at the reading start of the wordmark, stroke weight of the arc matches the wordmark's stem |
| Empty state | three/four concentric rings behind the drop target, clipped at one edge | static, low contrast, never animated on load |
| Continuity | a 10-bar waveform footline on the transcript footer / idle hero | only the centre bar uses the signal colour; bars are flat, 2px |

Do not reuse the rings as a loading spinner, background pattern behind text, or decorative border.
If an element cannot be explained by "the voice leaves an echo", it does not carry the motif.

## 3. Tokens

Replace borrowed cloud-grey/blue values with a paper-and-ink ramp. Values are proposed, not final;
every pair below is checked and the failing pair is called out.

| Token | Value | Use | Contrast note |
| --- | --- | --- | --- |
| `--paper-0` | `#FBF8F2` | main window surface | base |
| `--paper-1` | `#F6F1E6` | canvas behind panels | base |
| `--sand-1` | `#EFE8DA` | window chrome, toolbars | decorative |
| `--sand-2` | `#E2D8C5` | hairline borders | decorative |
| `--sand-3` | `#CFC2AC` | strong borders, drop-target edge | 1.6:1 vs paper — border only, never text |
| `--ink-900` | `#17140F` | rail background, primary text | 17.1:1 on `--paper-0` ✓ |
| `--ink-500` | `#7A7164` | secondary text, captions | 4.6:1 on `--paper-0` ✓ (≥14px only) |
| `--signal-500` | `#C2603F` | rings, selection underline, waveform centre | 3.9:1 on paper — **decorative and ≥24px text only** |
| `--signal-600` | `#A94E2F` | links, primary CTA, focus ring | 5.2:1 on paper ✓; white on it 5.5:1 ✓ |
| `--verify-700` | `#3F7D5F` | trust check icon and its short line | 4.6:1 on paper ✓ |

Rules:

- Terracotta is a **signal**, not a theme. It appears on at most one primary action per screen plus
  the motif; everything else is ink, paper, sand.
- Small text on terracotta (or terracotta small text on paper) uses `--signal-600`, never 500.
- The ink rail (`--ink-900`) replaces the light sidebar. Rail text is `--paper-0`; inactive items use
  sand-3 at 60% and are never below 4.5:1 for their label.
- Keep the existing semantic colours for success/warning/error; do not repaint the error modal.
- Dark theme is out of scope for the first pass. Do not ship a half-migrated dark mode; if the OS is
  dark, keep the light paper theme until a full dark ramp is designed.

## 4. Typography

The app already bundles IBM Plex Sans Arabic (OFL) and uses Inter for Latin: keep both, no licensing
work. The change is a scale and rhythm, not a new family.

| Role | Arabic | Latin | Size / line-height |
| --- | --- | --- | --- |
| Display (idle headline) | Plex AR SemiBold | Inter SemiBold | 25–28 / 1.3 |
| Section title | Plex AR SemiBold | Inter SemiBold | 16–18 / 1.4 |
| Body | Plex AR Regular | Inter Variable | 14–15 / 1.7 Arabic, 1.6 Latin |
| UI label / button | Plex AR Medium | Inter Medium | 12–13 / 1.5 |
| Timestamp / technical | Plex AR Regular tabular | Inter tabular | 11–12 / 1.4 |

- Arabic letter-spacing stays **0** (already enforced in 3.10 by the inverse-tracking rule); never
  apply uppercase or positive tracking to Arabic.
- Arabic commas `،`, question marks `؟`, and Arabic quotation marks in Arabic copy; Latin punctuation
  only in Latin strings.
- Western digits (`0–9`) for time, size and percent everywhere, tabular in transcript timestamps.
  Arabic-Indic digits are a future user preference, not a default.
- Line length: cap Arabic body text at ~70 characters per line; the transcript pane sets its own
  measure.
- Bidi: any mixed value (size, percent, path, model name) is wrapped in Unicode isolates in code, not
  fixed by CSS `direction` on the container. 3.10 fixed the first instance (download size); the 4.0
  pass audits the rest with the same helper.

## 5. Layout and shell

1. **Direction follows the language, once.** Arabic is the default and the rail sits on the right
   (reading start). English mirrors it to the left. No screen keeps the Vibe left-rail-in-RTL
   mismatch.
2. **No chat vocabulary.** No "new chat", no message bubbles, no assistant avatar. A session is a
   transcript: one record, its segments, its export.
3. **The empty screen is one composition:** headline, one drop target, trust line, language/options,
   done. The rail holds recents and nothing promotional.
4. **Settings is a door, not a page.** Keep the 3.10 header gear + `Ctrl+,`; in 4.0 it opens the same
   grouped dialog over the paper canvas.
5. **Trust lives at the decision point.** The privacy line stays under the drop target and on first
   run, in the 3.10 wording (V3 scoped truth). The 4.0 shell may restyle it; it may not strengthen
   the claim.
6. **Density is calm, not sparse.** 24px screen padding, 12–16px block rhythm, one accent per screen.

## 6. Motion

- Echo rings: one 1.8s opacity pulse on drop-target hover/focus only; static otherwise.
- New transcript segment: 120ms fade/slide at the end of the list, never reorder animation.
- Progress: keep the native progress semantics from 3.10; do not animate a fake indeterminate state
  during real download progress.
- Honor `prefers-reduced-motion`: rings static, segment insert instant.

## 7. Copy rules (inherited from V3, non-negotiable)

Say only what is true:

- Allowed: "التفريغ يتم على هذا الجهاز — لا يُرفع أي صوت أو نص." / "The first model download needs the
  internet; after that Sada works offline."
- Allowed: "بعد تنزيل النموذج مرة واحدة، يعمل صدى على هذا الجهاز بالكامل: لا تحليلات ولا قياس عن بُعد
  ولا حساب، ولا يُرفع أي صوت أو نص."
- Banned in every language: "لا يغادر جهازك أبداً", "خصوصية مطلقة", "آمن 100%", "بدون إنترنت" without the
  first-download exception, "بياناتك ملكك للأبد".
- The same rule applies to the 4.0 taglines: the display headline may be poetic, the trust line must
  stay literal.

## 8. Migration plan (after the gate, inside 4.0)

1. **Tokens + fonts first** (one PR): add the paper/ink/signal variables, map existing components to
   them, no layout change. Verify with the 3.10 screenshots as the baseline.
2. **Shell next:** rail to the reading start, ink rail, window chrome in sand. Keep every 3.10
   feature working; screenshots before/after.
3. **Empty state and motif:** wordmark, rings, waveform footline, headline.
4. **Settings and secondary surfaces:** grouped dialog restyle, export dialog, error modal typography
   (function and copy unchanged).
5. **Icons and installer artwork:** only after the in-app direction is accepted — this is where the
   release pipeline (OG cards, installer, tray) is touched.
6. Each step ships behind a build flag or a branch preview until the owner approves the whole set;
   the token layer alone is reversible in one commit.

## 9. Acceptance checklist for 4.0

- [ ] Rail sits at the reading start in both languages; no LTR/RTL mismatch on any screen.
- [ ] Every terracotta text/CTA pair meets 4.5:1 (or 3:1 for ≥24px only); checked pair list committed.
- [ ] Arabic letter-spacing is 0 everywhere; no uppercase Latin transforms on Arabic strings.
- [ ] Mixed numeric values (size, percent, time) render in the correct order in both languages.
- [ ] The trust line still passes the claim audit and appears at the drop point and on first run.
- [ ] No new network path, account, telemetry or cloud dependency was introduced.
- [ ] The wordmark, icon and installer artwork share one motif; upstream attribution is intact.
- [ ] A five-user review of the 4.0 build shows no regression in the 3.10 gate tasks.

## 10. Risks and open questions

- **Risk: identity over trust.** A poetic shell can read as marketing and weaken the literal trust
  line. Mitigation: trust copy keeps its own typographic slot and is never restyled into a badge.
- **Risk: scope explosion.** The motif invites illustration, icon and site work. Keep 4.0 to the app;
  release artwork is a separate, owner-approved step.
- **Open:** whether the display headline ships in Arabic only (with a shorter English line) or is
  translated fully. Decide with the measurement participants.
- **Open:** dark theme timing — design after light is accepted, not in the same release.
- **Open:** whether the echo glyph replaces the current app icon or lives only in-app; decide with
  the installer/OG-card pass.
- **Observation carried from 3.10:** several English catalogue strings still say "Vibe" (upstream base
  locale); the Arabic says صدى. The 4.0 naming pass is the natural place for one consistent brand
  rename in `en-US.json`, together with the wordmark and installer artwork.
