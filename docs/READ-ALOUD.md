# Read-aloud (Arabic text-to-speech) evaluation

Status: **evaluated 2026-11-18, verdict: no-go for v3.5.0** -- Windows does not ship an
Arabic TTS voice with a typical install, and the optional voice could not be quality-tested
on the evaluation machine. Read-aloud stays out of the app; no feature code was written.
This note records the evidence for milestone `v3.5.0`, issue #12, and the models council
card F (`docs/MODELS-COUNCIL.md` section 4).

> **2026-11-19 update.** The features council
> ([FEATURES-COUNCIL.md](FEATURES-COUNCIL.md), card A and Step Zero A) keeps this no-go for OS
> voices and narrows the TTS question to one named test: Habibi-TTS specialized Iraqi and MSA
> models (Apache-2.0 weights) on ten transcripts with a written kill rule. Nothing in this file is
> retracted; it remains the OS-voice evidence.

## Question

Text-to-speech is the cheapest accessibility win left: Windows has local SAPI/OneCore
voices, so a read-aloud action would need no download, no GPU and no model-weight licence.
The open question was whether an acceptable Arabic voice is present on typical Windows
machines, and if not, whether the optional Windows voice is good enough to justify asking
users to install it.

## Method

1. Enumerate every installed SAPI and OneCore voice (registry tokens plus the TTS engine
   directories on disk).
2. Check the installed Windows language features: an Arabic language pack being installed
   does not imply a speech voice is installed.
3. Check which Arabic TTS voices Microsoft documents for Windows and how they are
   installed.
4. Run the quality rubric below on a sample transcript -- blocked when no Arabic voice
   exists on the machine (see Findings).

## Findings on the evaluation machine

Machine: Windows 11 build 26300, 2026-11-18. Arabic (`ar-IQ`) is an installed display
language, English (`en-US`) is the system language.

| Item | Result |
| --- | --- |
| SAPI voices (`System.Speech`) | Microsoft David, Mark, Zira -- all `en-US` |
| OneCore voices (registry + `C:\Windows\Speech_OneCore\Engines\TTS`) | David, Mark, Zira, Eva -- only `en-US` engine data |
| Arabic TTS engine data | none installed |
| Arabic language feature | `ar-IQ` present (display/input), no speech capability |
| Microsoft-documented Arabic voices | Hoda (female, Arabic) and Naayf (male, Arabic Saudi Arabia), available as an **optional voice download** |
| Install path | Narrator settings (Win+Ctrl+N) -> Add more voices -> Settings -> Speech -> Manage voices -> Add voices -> Arabic; download needs network and typically elevation |

Sources: Microsoft Support, "Appendix A: Supported languages and voices"
(<https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-a-supported-languages-and-voices>)
and "Download languages and voices for Immersive Reader, Read Mode, and Read Aloud"
(<https://support.microsoft.com/en-us/education/learning-accelerators/download-languages-and-voices-for-immersive-reader-read-mode-and-read-aloud>).

## Quality rubric

If an Arabic voice is available on a test machine, score a fixed sample transcript
(MSA news paragraph with diacritics, one Iraqi-dialect sentence, and a technical sentence
containing `GPU`, `PDF`, `SRT`, `VTT`) on:

| Dimension | Scale | What counts as acceptable |
| --- | --- | --- |
| Intelligibility | 1-5 | 4+ means a native speaker understands it once without the text |
| MSA vs dialect reading | 1-5 | MSA read correctly; dialect words not mangled into nonsense |
| Punctuation pauses | 1-5 | commas and full stops produce natural pauses, no run-on |
| Technical terms | pass/fail | Latin acronyms are read understandably (spelling out is fine) |
| Latency / offline | pass/fail | starts under ~1 s, works with the network disconnected |
| Availability | pass/fail | present on a fresh Windows install without an optional download |

A voice passes only if intelligibility, MSA and punctuation are all 4+ and every
pass/fail row passes.

## Verdict: no-go

* **Not out of the box.** A normal Windows install (including one with an Arabic display
  language) has English voices only; Arabic TTS is an optional Narrator voice download
  that needs network access and usually elevation. Asking a non-technical Arabic-first
  user to install an OS speech feature before the read-aloud button works is worse than
  not shipping the button.
* **Quality cannot be verified from here.** The evaluation machine is not elevated and
  has no Arabic voice, so the rubric above cannot be run. Shipping a voice we have not
  heard would violate the evidence rule used for every other model decision.
* **Not worth a bundled alternative yet.** Chatterbox Multilingual V3 (MIT, 23 languages
  including Arabic) stays a documented suspended experiment: it is large, needs a GPU for
  acceptable speed, and its watermark requirement conflicts with a clean local read-aloud
  feature. Revisit only with a measured quality win and a licence-compatible watermark
  story.

## Retest path

On a machine with the Arabic voice installed (`Settings -> Time & language -> Speech ->
Voices`, or `Narrator -> Add more voices`), run:

```powershell
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + " | " + $_.VoiceInfo.Culture.Name }
$synth.SetOutputToWaveFile("$env:TEMP\sada-readaloud-ar.wav")
$synth.SelectVoice("<Arabic voice name>")
$synth.Speak("اجتمع الفريق صباح اليوم لمناقشة خطة الإطلاق، ثم رفع تقارير GPU و SRT إلى الإدارة.")
$synth.Dispose()
```

Score the resulting WAV against the rubric; if the verdict flips to go, add a
voice-availability-gated read-aloud action (no cloning, local only) as a separate issue.

