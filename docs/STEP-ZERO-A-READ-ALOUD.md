# Step Zero A — Arabic read-aloud falsification

**Status:** **FAIL — no-go on TTS retained** (Python-only runtime is a hard fail; CPU speed is
20× over the limit; GPU speed is borderline; naturalness is unevaluated)
**Date of test:** 2026-11-21 (Asia/Baghdad)
**Authorisation:** OWNER-ACTIONS A15 — owner instruction "then A14 then A15" (2026-11-19)
**Workstream:** FC-2 Step Zero A (this report), GitHub issue [#59](https://github.com/alshahia/sada/issues/59);
companion Step Zero B report: [STEP-ZERO-B-BURN-IN.md](STEP-ZERO-B-BURN-IN.md)
**Release under test:** tag `v3.10.0` tree (commit `be27bd5`). The test ran in a scratch
virtual environment; **no product code, dependency, model or version was changed**.

## Question

Does Habibi-TTS (the specialised Iraqi and MSA checkpoints, Apache-2.0) read Arabic text aloud
well enough, fast enough, under a licence and runtime that could ever ship **offline inside
Sada** — no Python at runtime, optional download ≤ 2 GB, user-owned or licensed reference
voice — or is the read-aloud gap still closed?

## Verdict

**No — the five-criterion gate fails, so TTS stays closed for this cycle.** Two failures are
decisive on their own, and one criterion could not be measured at all:

1. **No Python at runtime — FAIL.** The only working implementation of Habibi-TTS is Python:
   `habibi-tts 0.1.1` + `f5-tts 1.1.22` + `torch 2.8.0+cu126` + `vocos 0.1.0`, a **7,341 MB**
   environment. No shippable non-Python runtime was tested. (A non-Python path exists in
   principle — see [Re-check path](#re-check-path-what-would-change-the-verdict) — but it was
   not evaluated here, and an unproven path cannot pass the criterion.)
2. **CPU real-time factor — FAIL by ~20×.** 67.2 and 58.2 on the i7-9750H against a ≤ 3.0
   limit.
3. **GPU real-time factor — borderline FAIL.** Mean 0.873 (≤ 1.0) but **3 of 10 clips exceeded
   1.0** (max 1.152), and a repeat of the MSA set ranged 0.43–1.06, i.e. run-to-run variance
   crosses the limit. On the reference GPU it is "about real time", not safely real time; a
   slower laptop GPU would be below real time.
4. **Native-listener naturalness — NOT EVALUATED.** No native Arabic listener supplied a
   score, and the agent cannot supply one. A criterion that is not measured cannot be marked
   as passed.
5. **Licence and voice provenance — PASS for the test.** The tested checkpoints are Apache-2.0,
   the MSA reference voice is a CC0-1.0 Common Voice clip, and the Iraqi reference voice is the
   Apache-2.0 Habibi demo sample. Production would still need user-owned voice enrolment,
   which was not exercised.

**What did pass:** re-transcription intelligibility. MSA synthetic speech was transcribed with
**0.0 % CER on all five sentences**, identical to the human recordings (drift 0.0 %, limit
≤ 10 %), and the Iraqi set averaged 3.6 % raw CER (max 10.6 %, caused mainly by the ASR writing
"4" for the spoken word "أربعة"). Voice cloning from the reference clips worked; the samples
are intelligible and correctly accented. Quality was not the blocker — runtime and speed were.

**Kill/continue decision (2026-11-21):** the read-aloud no-go stays. No TTS integration, no
UI, no claim in v3.11. Re-check only when the conditions in
[Re-check path](#re-check-path-what-would-change-the-verdict) are met.

## Environment (recorded, not inferred)

| Item | Value |
| --- | --- |
| Host | Windows 11 Pro 10.0.26300, Intel Core i7-9750H, 31.8 GB RAM |
| GPU | NVIDIA Quadro RTX 4000, 8,192 MiB (the reference machine from the P7 plan) |
| Python | 3.12.9 (uv-managed), isolated venv |
| Packages | `torch 2.8.0+cu126`, `torchaudio 2.8.0+cu126`, `f5-tts 1.1.22`, `habibi-tts 0.1.1`, `vocos 0.1.0`, `x-transformers 2.31.20`, `transformers 5.23.0` |
| ASR engine | `vibe-server v0.6.16-sada.1` (bundled engine), `ggml-large-v3-turbo.bin` (1,549 MB), `--language ar` |
| FFmpeg | bundled 9.0.2 for reference-audio conversion (`VIBE_SERVER_FFMPEG_PATH`) |
| Generation settings | F5-TTS v1 Base config, Vocos mel-24khz vocoder, 32 NFE (default), CFG 2.0, sway −1.0, speed 1.0, dialect id MSA / IRQ, one discarded warm-up run per process, then 5 timed sentences |
| Model load time | MSA 10.3–22.4 s GPU, 12.5 s CPU; IRQ 11.3 s GPU (excluded from RTF) |

## Test set

| Group | Sentences | Checkpoint (Apache-2.0) | Reference voice | Licence of the voice |
| --- | --- | --- | --- | --- |
| MSA | 5 (the reference transcripts of benchmark clips `msa-cv-001`…`msa-cv-005`; each also has its human recording for the human baseline) | `Specialized/MSA/model_200000.safetensors` (1,348,683,569 B) + `vocab.txt` | `benchmarks/arabic-asr/audio/msa-cv-010.wav` (4.78 s), transcript supplied | CC0-1.0 (Common Voice 18 Arabic, Mozilla) |
| Iraqi | 5 composed Iraqi sentences (greetings, questions, meeting, file, offline) | `Specialized/IRQ/model_100000.safetensors` (1,348,775,729 B) + `vocab.txt` | Habibi demo `assets/IRQ.wav` (5.54 s), transcript supplied | Apache-2.0 (Habibi repo sample); production needs a user-owned voice |

Both checkpoints and their vocab files are listed with SHA-256 in the
[artefact table](#evidence-artefacts-scratch-not-committed). The Unified/SAU/UAE checkpoints
(CC-BY-NC-SA-4.0) were not used, as the council requires.

## Method

1. **Environment.** uv venv with Python 3.12, CUDA torch pinned to a version that satisfies
   `habibi-tts`'s `torch<2.9` constraint, then `uv pip install habibi-tts` (pulls `f5-tts`).
   The first attempt installed the CPU torch wheel from PyPI, which silently removes CUDA;
   it was replaced with the cu126 pair before measuring.
2. **Synthesis** (scratch harness, `gen.py`): load the local `.safetensors` checkpoint with the
   local `vocab.txt`, load the Vocos vocoder, preprocess the reference audio + transcript,
   generate one warm-up sentence (discarded), then generate the five test sentences with
   `infer_process` and write 24 kHz mono WAVs. RTF = generation seconds ÷ audio seconds.
3. **Re-transcription** (scratch harness, `asr.py`): call the bundled engine
   (`vibe-server transcribe ggml-large-v3-turbo.bin <wav> --language ar`) on each synthetic WAV;
   compute character CER against the input text with the benchmark's `char_stats`/`rate`
   normalisation (Arabic diacritics, punctuation and tatweel are handled by the benchmark).
   For MSA the same engine transcribes the human recording of each sentence to establish the
   human baseline; CER drift = TTS CER − human CER.
4. **CPU measurement** (`--device cpu`, MSA sentences 1–2): the same pipeline with torch on CPU.
   The Iraqi CPU pair was **not** run: the MSA pair already exceeded the limit by ~20×, both
   checkpoints share the same architecture and size, and the extra ~10 minutes could not change
   the verdict. This is recorded as a limit, not hidden.

## Results

### 1. Re-transcription CER and drift (limit: drift ≤ 10 %)

| Clip | Input sentence | Human CER | TTS CER | Drift |
| --- | --- | --- | --- | --- |
| msa-01 | أعلنت القوات الأمريكية انتهاء مهمتها في العراق. | 0.0 % | 0.0 % | 0.0 % |
| msa-02 | كل ما عليك فعله هو حفظ هذه الجملة عن ظهر قلب. | 0.0 % | 0.0 % | 0.0 % |
| msa-03 | سأكون قد درست الإنجليزية لخمس سنوات مع حلول فبراير المقبل. | 0.0 % | 0.0 % | 0.0 % |
| msa-04 | يحترم عالمنا قانوناً ذهبياً واحداً: من يملك الذهب يضع القانون. | 0.0 % | 0.0 % | 0.0 % |
| msa-05 | بالرغم من أنني أحسست بأن هناك شيئاً غريباً ، لم أعرف بالتحديد ما هو. | 0.0 % | 0.0 % | 0.0 % |
| irq-01 | هذا الصوت جاي من برنامج صدى، يقرأ النص باللهجة العراقية. | — | 2.2 % | n/a |
| irq-02 | شنو رأيك بهذا الاختبار؟ إذا واضح أكدر أستمر بيه. | — | 2.6 % | n/a |
| irq-03 | الاجتماع اليوم الساعة أربعة، لازم نكون جاهزين قبل الموعد. | — | 10.6 % | n/a |
| irq-04 | ملف الترجمة مالت الفيديو خلص، بس يحتاج مراجعة أخيرة. | — | 2.4 % | n/a |
| irq-05 | لا تشيل هم، العملية كلها تصير بدون إنترنت وعلى جهازك. | — | 0.0 % | n/a |

Iraqi has no human recording of the same sentences in the repository, so drift cannot be
computed; only raw CER exists. The irq-03 gap is mostly numeral formatting (the ASR writes
"الساعة 4" for the spoken "الساعة أربعة"), not a mispronunciation. Mean Iraqi CER = 3.6 %,
max = 10.6 %. **Verdict: the one measurable drift criterion passes (MSA 0.0 %); the Iraqi
half is unmeasured by design of the available corpus.**

### 2. GPU real-time factor (limit: ≤ 1.0)

| Clip | Audio (s) | Generation (s) | RTF |
| --- | --- | --- | --- |
| msa-01 | 4.096 | 4.123 | 1.007 |
| msa-02 | 3.712 | 3.938 | 1.061 |
| msa-03 | 4.992 | 3.265 | 0.654 |
| msa-04 | 5.323 | 3.150 | 0.592 |
| msa-05 | 5.749 | 2.462 | 0.428 |
| irq-01 | 4.757 | 4.547 | 0.956 |
| irq-02 | 4.064 | 3.953 | 0.973 |
| irq-03 | 4.907 | 4.767 | 0.972 |
| irq-04 | 4.437 | 5.112 | 1.152 |
| irq-05 | 4.480 | 4.198 | 0.937 |

Mean **0.873**, maximum **1.152**, 3/10 above 1.0. A repeat of the MSA set produced
0.43–1.06, so the per-clip numbers move by up to ~1.8× between runs (laptop GPU clocks, no
fixed seed). **Verdict: marginal fail** — the mean is inside the limit, the guarantee is not.
A feature that sometimes takes longer than the audio it produces is not a real-time feature.

### 3. CPU real-time factor (limit: ≤ 3.0)

| Clip | Audio (s) | Generation (s) | RTF |
| --- | --- | --- | --- |
| msa-01 | 4.043 | 271.745 | **67.22** |
| msa-02 | 3.669 | 213.457 | **58.17** |

**Verdict: fail by ~20×** on a 6-core laptop CPU. A 4-second sentence takes ~4 minutes offline
on a machine with no GPU.

### 4. Model runtime and download size (limit: no Python at runtime; optional download ≤ 2 GB)

| Check | Result |
| --- | --- |
| Non-Python runtime | **None.** `habibi-tts` is a Python package around `f5-tts`; the environment is 7,341 MB and needs Python 3.12 + torch. No GGUF/ONNX/wasm build ships today. |
| Checkpoint size | 1,348,683,569 B (MSA) and 1,348,775,729 B (IRQ) = 1.26 GiB each. **One** optional dialect download is within 2 GB; shipping both would be 2.51 GiB, over the limit. |
| Existing non-Python artefacts | ONNX exports of the IRQ/MSA checkpoints exist (`OpenVoiceOS/phoonnx-f5tts`, Apache-2.0, ~1.39 GB: `model.onnx` 1260.8 MB + preprocess 65.7 MB + decode 59.6 MB) and a community C++/ggml runtime documents Habibi GGUF packages (`audio.cpp`, Apache-2.0, `habibi_msa`/`habibi_irq`). Neither was integrated or tested here. |

**Verdict: fail on the runtime clause** (size clause passes for a single checkpoint).

### 5. Reference voice provenance (limit: user-owned or licensed)

**Pass for the test.** The MSA voice is a CC0-1.0 clip; the Iraqi voice is the Apache-2.0
Habibi demo sample; no third-party voice was cloned without a licence. **Caveat:** the
production requirement — a user recording their own reference voice through the app — was not
exercised and remains unproven.

## Criterion-by-criterion verdict

| # | Criterion (P7 plan copy of record) | Result | Verdict |
| --- | --- | --- | --- |
| 1 | Native-listener mean ≥ 4/5 | Not measured — no native listener supplied | **FAIL (unevaluated cannot pass)** |
| 2 | Re-transcription CER drift ≤ 10 % | MSA 0.0 % drift; Iraqi raw mean 3.6 %, no baseline | **PASS (measurable part)** |
| 3 | RTF ≤ 1.0 GPU / ≤ 3.0 CPU | GPU mean 0.873, max 1.152, 3/10 over 1.0; CPU 58–67 | **FAIL** |
| 4 | No Python at runtime; optional download ≤ 2 GB | Python-only stack, 7.3 GB env; single checkpoint 1.26 GiB | **FAIL** |
| 5 | User-owned or licensed reference voice | CC0 MSA + Apache-2.0 IRQ sample; production enrolment untested | **PASS for the test** |

**Overall: FAIL.** The no-go on read-aloud stands. Nothing in this report authorises TTS code,
UI, model bundling or a public claim.

## Re-check path (what would change the verdict)

The kill rule is "re-check only when a GGUF/ONNX Arabic TTS exists". Since 2026-11-21 one
candidate exists but is unproven:

- **Runtime.** `audio.cpp` (Apache-2.0, C++ on ggml) documents a community F5-TTS/Habibi port
  with GGUF packages for the specialised `habibi_msa`/`habibi_irq` checkpoints; ONNX exports of
  the same checkpoints also exist. A re-check would need: build/embedding in the
  Tauri/Rust sidecar (no Python), licence review of the runtime and of GGUF redistribution,
  then the same quality/CER/RTF/naturalness measurements on this report's test set.
- **Naturalness.** A native Arabic listener scoring the 10 clips (or the 5 MSA + 5 Iraqi set)
  on a 1–5 rubric; without it criterion 1 stays failed.
- **Speed.** Re-measure GPU RTF with a fixed seed and warm clocks, and CPU RTF on the target
  minimum hardware. On this CPU the criterion fails by an order of magnitude, so a CPU-only
  product would need a different model or a much smaller one.

Until those conditions are met, read-aloud is not a candidate for any release.

## Caveats and limits (honest scope)

- **Agent, not native listener.** No human scored naturalness; intelligibility was measured by
  ASR, which is a proxy for "can a listener understand it", not for prosody or naturalness.
- **Small test set.** 10 sentences (5 MSA + 5 Iraqi), one reference voice per dialect, one GPU
  host, one generation seed (unseeded — the samples differ between runs, which is why the RTF
  spread is reported).
- **Iraqi has no human baseline**, so drift is only measured for MSA.
- **CPU pair covers MSA only** (see Method); both checkpoints are the same size/architecture.
- **TTS quality ≠ product decision.** Even a perfect quality score would not have passed the
  runtime criterion; the report does not soften that.
- **No artefacts committed.** Model files (2.5 GB) and WAVs stay in scratch; only sizes,
  SHA-256 values and commands are in this report. The WAVs remain on the test host for the
  owner to listen to.

## Evidence artefacts (scratch, not committed)

Scratch root: `E:/rea/vibe_app/.dsh/tmp/step-zero-a/`. Hash values are computed from the files
used in this run; model URLs are the Hugging Face source.

| File | Bytes | SHA-256 |
| --- | --- | --- |
| `models/MSA/model_200000.safetensors` | 1,348,683,569 | `708a107b05a734523b4e967111dba68f73a7e29f76093f67bb7493204f434cd1` |
| `models/MSA/vocab.txt` | 11,698 | `4de4460ff1ef7cb40c2e564bc1ee2f3198164d10ce71380290986e483ba7e19c` |
| `models/IRQ/model_100000.safetensors` | 1,348,775,729 | `1801bcc5f7baea63bd74bc8424821ad1f0f06200138380a47921113cb1c7f500` |
| `models/IRQ/vocab.txt` | 11,829 | `55484bc3dda8b8e6a7fbf04261b47a8788d4b553a85b93dc46dac6fd39c9fd88` |
| MSA reference voice (`msa-cv-010.wav`) | 152,910 | `ae920026f088a71ef15449644ea8d622aa594365e87dba9bcd46b8268adcbd60` |
| Iraqi reference voice (`assets/IRQ.wav`) | 265,854 | `d6180049f407364cc6667ad6903ba5e55a2b00f002d17ffe16a685199859fca4` |
| `msa_cuda/msa-01.wav` … `msa-05.wav` | 178,220–276,012 | recorded in `out/hashes.json` |
| `iraqi_cuda/irq-01.wav` … `irq-05.wav` | 195,116–235,564 | recorded in `out/hashes.json` |
| `out/cer_msa.json`, `out/cer_iraqi.json`, `out/timings_*.json`, `out/env.json` | small JSON | measurement inputs (not committed) |

## Reproduction (scratch commands, summarised)

```powershell
# 1. Environment (uv)
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe torch==2.8.0 torchaudio==2.8.0 `
  --index-url https://download.pytorch.org/whl/cu126
uv pip install --python .venv/Scripts/python.exe habibi-tts   # pulls f5-tts 1.1.22, vocos, ...

# 2. Checkpoints (Apache-2.0)
curl -L -o models/MSA/model_200000.safetensors `
  https://huggingface.co/SWivid/Habibi-TTS/resolve/main/Specialized/MSA/model_200000.safetensors
curl -L -o models/MSA/vocab.txt `
  https://huggingface.co/SWivid/Habibi-TTS/resolve/main/Specialized/MSA/vocab.txt
curl -L -o models/IRQ/model_100000.safetensors `
  https://huggingface.co/SWivid/Habibi-TTS/resolve/main/Specialized/IRQ/model_100000.safetensors
curl -L -o models/IRQ/vocab.txt `
  https://huggingface.co/SWivid/Habibi-TTS/resolve/main/Specialized/IRQ/vocab.txt

# 3. Generate + re-transcribe (harnesses described in Method; texts in texts.json)
python gen.py --config texts.json --group msa   --device cuda --out out/msa_cuda
python gen.py --config texts.json --group iraqi --device cuda --out out/iraqi_cuda
python gen.py --config texts.json --group msa   --device cpu --limit 2 --out out/msa_cpu
$env:VIBE_SERVER_FFMPEG_PATH = 'app/desktop/src-tauri/binaries/ffmpeg-x86_64-pc-windows-msvc.exe'
python asr.py --config texts.json --group msa   --tts-dir out/msa_cuda --baseline-dir out --out out/cer_msa.json
python asr.py --config texts.json --group iraqi --tts-dir out/iraqi_cuda --out out/cer_iraqi.json
```

The engine call is `vibe-server transcribe <model> <wav> --language ar`; the engine needs
`VIBE_SERVER_FFMPEG_PATH` when the input WAV is not already 16 kHz mono (synthetic audio is
24 kHz). The bundled-FFmpeg dependency is the same binary that ships with the app.
