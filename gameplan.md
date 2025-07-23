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

⬜ **TODOs**:
- [x] Implement .wav file loader using `soundfile` (load audio data, print shape/duration)
- [x] Implement ffmpeg conversion function (convert mp3→wav, check output file)
- [x] Add logging and error messages for each function
- [x] Run end-to-end test: load audio file → convert if needed → print info
- [ ] Implement mic input using `sounddevice` (record short audio, stream to pipeline)
- [ ] Test real-time audio stream from mic
- [ ] Ensure fallback to file-based ingestion for testing
- [ ] Add error handling for mic permissions and device issues

**Reasoning:**
- Mic input is required for real-time/production use.
- File-based ingestion is used for testing and reproducibility.

**🛠️ Currently Doing**: Implementing mic input and real-time audio stream

**📦 Libraries**: `sounddevice`, `soundfile`, `ffmpeg-python`

---

## 🧠 SPEECH-TO-TEXT

**📌 Vision**: Convert audio chunks to text with reasonable speed/accuracy balance

**♻️ Tradeoffs**: 
- Local: `faster-whisper` (GPU), `whisper.cpp` (CPU) - Free but slower
- API: OpenAI Whisper API - Fast/accurate but paid

⬜ **TODOs**:
- Implement `faster-whisper` as primary
- Add `whisper.cpp` CPU fallback
- Determine optimal chunk size for real-time

**🛠️ Currently Doing**: -

**📦 Libraries**: `faster-whisper`, `whisper.cpp`

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

## 🎨 OUTPUT & VISUALIZATION

**📌 Vision**: Debug-friendly output and basic UI for results

⬜ **TODOs**:
- Console table output with timestamps
- JSON export for structured data
- Simple Streamlit UI (optional)

**🛠️ Currently Doing**: -

**📦 Libraries**: `rich` (console), `streamlit` (optional UI)

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