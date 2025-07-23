# 📦 AI TONE DETECTOR PIPELINE

> Real-time AI that listens to audio, identifies speakers/emotions, and maps tone to narrative scene beats.

**Input**: Live mic or `.wav` files  
**Output**: Structured speaker timeline with text + emotion + beat labels  
**Platform**: macOS dev, Python backend, local-first preferred

---

## 🚨 SETUP CHECKLIST

✅ Install Python 3.11, `ffmpeg`, `portaudio`  
✅ Create `venv`, install core libs: `whisperx`, `pyannote`, `torch`, `sounddevice`  
⬜ Setup repo structure: `main.py`, `config.yaml`, `logs/`, `BUILD_LOG.md`  
⬜ Test with placeholder audio file

**Status:**
- All Python dependencies and system libraries are now installed and working (including PyAudio/PortAudio fix on macOS).
- Remaining: Set up repo structure files, and run a test with a placeholder audio file to validate the environment.

---

## 🚩 Today's Focus

- Confirm all dependencies and system libraries are installed and working (including audio libraries).
- Scaffold `main.py` with empty functions for AUDIO INGESTION (mic capture, .wav loader, ffmpeg conversion).
- Research and implement the AUDIO INGESTION section of the pipeline.

---

## 🔊 AUDIO INGESTION

**📌 Vision**: Capture real-time mic or load `.wav` files with minimal latency

**♻️ Tradeoffs**: Real-time streaming complexity vs batch processing simplicity

✅ All audio dependencies (`sounddevice`, `ffmpeg`, `portaudio`, etc.) are importable and working (see test_installs.py summary: 30/30 modules OK).

✅ File-based ingestion (.mp3→.wav) is working and tested end-to-end.

✅ Mic input implemented and tested (recorded mic_test.wav, loaded and printed info).

⬜ **TODOs**:
- [ ] Implement stream input instead of single file

**Reasoning:**
- Mic input is required for real-time/production use.
- File-based ingestion is used for testing and reproducibility.

**🛠️ Currently Doing**: Moving to speech-to-text pipeline

**📦 Libraries**: `sounddevice`, `soundfile`, `ffmpeg-python`

---

## 🧠 SPEECH-TO-TEXT

**📌 Vision**: Convert audio chunks to text with reasonable speed/accuracy balance

**♻️ Tradeoffs**:
- Local: `faster-whisper` (GPU), `whisper.cpp` (CPU) - Free but slower
- API: OpenAI Whisper API - Fast/accurate but paid

✅ Batch speech-to-text on 5s audio clips is working and tested (see logs for chunked transcription results).

⬜ **TODOs**:
- [ ] Prepare for real-time streaming after batch baseline is working
- [ ] Add logging and error handling for transcription failures

**For later (after batch baseline):**
- [ ] Implement `faster-whisper` as primary speech-to-text engine (real-time/streaming mode)
- [ ] Add `whisper.cpp` CPU fallback for non-GPU systems
- [ ] Test transcription on both mic and file-based audio (real-time and batch)
- [ ] Determine optimal chunk size for real-time streaming

**Reasoning:**
- Batch mode on 5s chunks simulates real-time input and is easier to debug
- Once batch works, can optimize for true streaming/low-latency

**🛠️ Currently Doing**: Moving to UI development for output/visualization

**📦 Libraries**: `faster-whisper`, `whisper.cpp`

---

## 🎨 OUTPUT & VISUALIZATION

**📌 Vision**: Show audio playback with mapped text and waveform in a modern UI

⬜ **TODOs**:
- [ ] Scaffold a React UI to display:
    - Audio file playback
    - Synchronized text transcript mapped to audio
    - Audio waveform visualization
- [ ] Integrate backend output (chunked text, timestamps) with frontend
- [ ] Add basic styling and controls (play/pause, seek)
- [ ] Enable debugging and demo for pipeline results

**Reasoning:**
- UI is needed for debugging, demo, and user feedback
- Visualizing text alignment with audio helps validate pipeline accuracy

**🛠️ Currently Doing**: Planning and scaffolding React UI

**📦 Libraries**: React, wavesurfer.js (for waveform), any modern React toolchain

---

## 🗣️ SPEAKER DIARIZATION  

**📌 Vision**: Identify "who spoke when" in audio segments

**♻️ Tradeoffs**:
- Local: `pyannote.audio` (SOTA, needs GPU) vs `resemblyzer` (lighter, CPU)
- API: Google/AssemblyAI (accurate, paid)

⬜ **TODOs**:
- Implement `pyannote.audio` for speaker separation
- Test on partial audio segments
- Verify open-source licensing

**🛠️ Currently Doing**: -

⬜ **DISCOVERY NEEDED**: Speaker segmentation on streaming audio

**📦 Libraries**: `pyannote.audio`

---

## 😠 EMOTION DETECTION

**📌 Vision**: Classify emotional tone from speech audio

**♻️ Tradeoffs**:
- Local: `speechbrain` models, `openSMILE` features - Private but setup-heavy
- API: Affectiva, Azure Emotion - Easy but paid

⬜ **TODOs**:
- Choose emotion taxonomy (Ekman basic emotions as start)
- Implement `speechbrain` pretrained model
- Create validation test set

**🛠️ Currently Doing**: -

⬜ **DISCOVERY NEEDED**: Define emotion taxonomy and validation approach

**📦 Libraries**: `speechbrain`, `openSMILE`

---

## 🎭 SCENE BEAT CLASSIFICATION

**📌 Vision**: Map emotions + text to narrative scene types (tension, resolution, etc.)

**♻️ Tradeoffs**:
- Local: Small LLMs via `ollama`, rule-based heuristics - Free but limited
- API: ChatGPT/Claude - High quality but costly

⬜ **TODOs**:
- Start with simple rule-based emotion→beat mapping
- Define beat taxonomy (tension, calm, conflict, resolution)
- Test local LLM integration

**🛠️ Currently Doing**: -

⬜ **DISCOVERY NEEDED**: Scene beat taxonomy and labeling examples

**📦 Libraries**: `ollama` (local LLM), rule-based fallback

---

## 🔁 PIPELINE ORCHESTRATION

**📌 Vision**: Compose all modules into replaceable, testable pipeline

**♻️ Tradeoffs**: Async streaming vs synchronous batch processing

⬜ **TODOs**:
- Create `pipeline.py` with modular components
- Implement basic async audio processing
- Add component swap capability (local ↔ API)

**🛠️ Currently Doing**: -

⬜ **DISCOVERY NEEDED**: Best async pattern for audio pipeline

**📦 Libraries**: `asyncio`, `threading`

---

## 🧪 TESTING & VALIDATION  

**📌 Vision**: Real-world robustness with sample audio

⬜ **TODOs**:
- Collect 3-5 test audio samples (different speakers, emotions)
- Create accuracy benchmarks for each component
- End-to-end pipeline test

**🛠️ Currently Doing**: -

---

## 🚀 DEPLOYMENT

**📌 Vision**: Easy local usage, optional cloud deployment

⬜ **TODOs**:
- Package as runnable script with `main.py`
- Add Docker container (optional)
- AWS deployment guide (optional)

**🛠️ Currently Doing**: -

---

## ⬜ DONE WHEN:
- Pipeline processes live mic input → structured output
- All components tested with sample audio  
- Basic UI shows real-time results
- Documentation allows others to run locally