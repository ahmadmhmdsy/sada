# Five-user gate kit — runs on 3.11.0

Runnable moderator kit for the gate that must pass before the next UI wave (3.12 Wave 2) and before
any 4.0 work. The rules and pass thresholds live in [DECISIONS.md](DECISIONS.md) §6 — this file is the
operating manual for running them, and the two must not disagree.

**Status 2026-11-23:** ready to run. The installer below is the published, verified 3.11.0 build, and
[GATE-RUN-3.11.md](GATE-RUN-3.11.md) is the pre-flight and session pack. 3.11.0 shipped no UI change
(maintenance only), so the 3.10-era tasks and thresholds still apply.

**Why run it:** the four Wave 1 repairs were chosen from a critique, not from behaviour. This gate is
the only evidence that they actually work for Iraqi-Arabic speakers before the project spends another
release on them.

## 1. What you need

| Item | Notes |
| --- | --- |
| 5 participants | Iraqi-Arabic speakers, none of whom has seen the boards or these tasks; at least 3 installing Sada for the first time on their own Windows 10/11 device |
| 1 moderator + 1 note-taker | Same two people for all five sessions (consistency beats convenience) |
| 3.11.0 installer | The verified published asset (not the dev server): `Sada_3.11.0_x64-setup.exe`, 44,013,711 bytes, SHA-256 `57742cf25cc73bbf62e2775035658b1d5194fb2f5de8252b04676e5d083d2929`, from the [v3.11.0 release](https://github.com/alshahia/sada/releases/tag/v3.11.0). It can also be built from the tagged commit `c7acdc8`. Record its SHA-256 on every sheet. |
| Sample audio for task 3 | One Arabic clip, 30–60 s (`sample-ar-30s.m4a`); a second copy on a USB stick in case the participant's device blocks the file |
| Deliberately broken model for task 4 | A folder containing a fake `ggml-medium.bin` of a few KB (any text file renamed). Used to produce a real model-kind error without touching the participant's files. |
| Wi-Fi | Task 1 covers the only online step: the first model download |
| Printed observation sheets | One per participant (§4) + task cards (§3); keep results anonymous (P1…P5) |
| Timer | Every task has a time budget; record actual seconds where the pass rule uses time |

Sessions are ~30 minutes each; allow 45 in the calendar. Notes only — **no telemetry, no audio or video
recording of the participant**, no data leaves the room. If the participant agrees to a screen recording
for internal review only, keep it local and delete it after the results are written.

## 2. Rules for the moderator

1. Read the task card **verbatim**, then stop talking. Do not name a button, a menu or a feature.
2. Think-aloud is required: “گلي شنو راح تسوي هسه، وشنو تتوقع يصير”.
3. Let them struggle. Only rescue after 60 seconds of visible dead-end, and write down that you rescued
   (rescued attempts still count as failures for the pass rule).
4. If they ask a direct question, answer it with a question: “شنو تتوقع؟” / “جرب وشوف”.
5. Record verbatim quotes for the trust and error tasks; paraphrase everything else.
6. Never explain the four repairs, never mention boards, axes or copy variants.
7. Run the tasks in this order for every participant. Do not change the order, the wording, or the
   pass rules after the first participant starts.
8. At the end, thank them and give the agreed gift/support without tying it to the answers.

## 3. Task cards

Print each card separately, in Arabic; the English line is for the note-taker only.

### Task 1 — Install, first run, and the trust question (12 min)

> **البطاقة ١ · التنصيب وأول تشغيل**
> ركّب صدى من هذا الملف، وكمّل الإعداد الأول حتى توصل لشاشة التنزيل. بعدها گلي: **شنو راح يصير
> للتسجيل مالتك بعد ما تخلص؟** وشنو تحتاج حتى يشتغل التطبيق أول مرة؟

English: install the 3.11.0 installer, complete first-run setup, and reach the model download. Then ask
what happens to their audio, and what the app needs for the first run.

Record: did they reach the download screen unaided (Y/N)? What do they say happens to the audio —
“stays on this computer / not uploaded” (Y/N/something else, quote it)? Do they understand the one-time
internet need (Y/N)? Did they click anything that implies an account, cloud or upload?

### Task 2 — Find Settings (2 min)

> **البطاقة ٢ · الإعدادات**
> من الشاشة الرئيسية، بدّل لغة العرض إلى الإنجليزية.

English: from the main screen, change the display language to English.

Record: seconds from task start to the settings dialog being visible (stop the clock when the dialog
opens, not when the language changes). Note how they found it (gear / keyboard / menu) and whether the
grouped sidebar helped (“وين ألگى …؟” quotes).

### Task 3 — Finish a transcript and get the whole text out (8 min)

> **البطاقة ٣ · استخراج النص**
> سوِّ تفريغ لهذا الملف الصوتي، وبعدين طلّع النص كامل حتى تكدر تلصقه بمكان ثاني.

English: transcribe the sample audio, then get the full text out so it can be pasted elsewhere.

Record: which control they use first (Copy all / Export / select-and-copy / something else). If they
open Export, note which format they choose and whether the four groups helped or distracted. Paste the
result into the note-taker's Notepad to confirm the text is complete and ordered.

### Task 4 — A model error and the next step (6 min)

> **البطاقة ٤ · خطأ**
> (المُيسِّر يفتح الإعدادات ← الموديلات ويختار موديل مكسور بالغلط، بعدين يطلب تفريغ.)
> صار خطأ. شنو راح تسوي هسه؟ جرّب تكمّل.

English: the facilitator (not the participant) points the model setting at the deliberately broken
model, then asks for a transcription. The participant has to recover.

Record: first action (open model settings / retry / reset / report issue / ask for help / close).
Was the offered recovery the one they chose (Y/N)? Did they reach Reset first (Y/N — a Reset-first
path fails the pass rule)? Quote what they say the dialog is telling them.

### Task 5 — Read the Arabic UI (5 min)

> **البطاقة ٥ · نظرة على الواجهة**
> شوف هذي الشاشات (البداية، الإعدادات ← الخصوصية، أول تشغيل) وگلي إذا شي مكسور، مو مفهوم، أو
> يبدو غلط.

English: look at the idle screen, Settings → Privacy, and the first-run screen, and report anything that
looks broken, unclear or wrong.

Record every finding, one per line, with the screen and a severity: **critical** (text unreadable,
letters disconnected or reversed, bidi order wrong in a number/unit, a control that cannot be used) or
**minor** (cosmetic spacing, a wording preference). Attach a screenshot only if the participant points
at something visible, and only with consent.

## 4. Observation sheet (copy one per participant)

```text
Participant: P___        Date: ____-__-__        Facilitator: ______________
Installer SHA-256: ______________________________  Device/Windows: ____________
Consent: notes only [ ]   screen recording local-only [ ]   declined [ ]
First Sada install?  yes [ ]  no [ ]

TASK 1 — install / trust                                           time ___ min
  reached download screen unaided ............ Y / N / rescued
  audio “stays here, not uploaded” ............ Y / N / other: ______________________
  quote: ______________________________________________________________________
  understands one-time internet need ......... Y / N
  account/cloud/upload implication ........... Y / N  what: _______________________

TASK 2 — settings discovery                                        time ___ s
  opened settings ............................. Y / N / rescued
  path: gear [ ] keyboard [ ] other: ________
  quote: ______________________________________________________________________

TASK 3 — full text out                                             time ___ min
  first control: Copy all [ ] Export [ ] select+copy [ ] other: ______________
  if Export: format ______   groups helped / distracted / unnoticed
  pasted text complete and ordered ............ Y / N
  quote: ______________________________________________________________________

TASK 4 — model error recovery                                      time ___ min
  first action: model settings [ ] retry [ ] reset [ ] report [ ] ask [ ]
  chose the offered recovery .................. Y / N
  Reset first (fails rule) .................... Y / N
  quote: ______________________________________________________________________

TASK 5 — Arabic read-through
  critical findings: __   minor findings: __
  1. screen __________ severity ______ description ____________________________
  2. screen __________ severity ______ description ____________________________
  3. screen __________ severity ______ description ____________________________

Notes / facilitator remarks:
______________________________________________________________________________
```

## 5. Scoring the gate

Fill the five rows below from the sheets. A row passes only if every cell in its “pass rule” column is
met; rescued attempts count as failures.

| Task | Pass rule | P1 | P2 | P3 | P4 | P5 | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 4/5 “stays on this computer / not uploaded”; 5/5 understand one-time internet |  |  |  |  |  |  |
| 2 | 4/5 in under 10 s; median ≤ 8 s |  |  |  |  |  |  |
| 3 | 4/5 use Copy all; nobody opens Export first by mistake |  |  |  |  |  |  |
| 4 | 3/5 choose the offered recovery; nobody chooses Reset first |  |  |  |  |  |  |
| 5 | 0 critical bidi/tracking defects; ≤ 2 minor findings |  |  |  |  |  |  |

Decision (from [DECISIONS.md](DECISIONS.md) §6):

- **Pass** (all five rows pass) → start the 3.12 Wave 2 scope (see [v3.12.0-plan.md](../../releases/v3.12.0-plan.md));
  review the [4.0 identity brief](../echo-identity-4.0.md) preview for a separate owner go.
- **Partial** (one or two rows fail) → fix only the failing task, retest with the next five participants;
  Wave 2 waits.
- **Fail** (three or more rows fail, or any critical safety/trust failure such as an unexpected upload
  prompt) → stop the sequence and re-open the relevant Q1 family with the council.

Write the anonymised appendix into [DECISIONS.md](DECISIONS.md) §6 before changing any UI again:

```text
### Gate results — 3.11.0 (dates)
Participants: P1…P5, Iraqi Arabic, n first-time installs = __
Outcome: pass / partial / fail
Row results: 1 __/5 · 2 __/5 (median __ s) · 3 __/5 · 4 __/5 · 5 __ critical, __ minor
Quotes worth keeping: ...
Failures and the single fix chosen: ...
Decision applied: ...
```

## 6. After the gate

- **Pass** → the DECISIONS.md release map moves the next UI wave (3.12) to ready; record the exact build
  tested: 3.11.0, tag `c7acdc8`, installer SHA-256 `57742cf2…d2929`.
- **Partial/fail** → do not start 3.12 and do not start the Echo identity. The failing task becomes the
  only repair; everything else waits.
- Keep the filled sheets and photos of the room state for six months; they are the evidence behind the
  decision. Do not publish participant names or faces anywhere.
