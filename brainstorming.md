# 🧠 BRAINSTORMING: Audio Tone AI MVP

## 📅 10-Day Development Plan

| Day | Goal | Key Libraries | Success Test |
|-----|------|---------------|--------------|
| 1-2 | Audio → Text Pipeline | `faster-whisper`, `ffmpeg` | Upload file → accurate transcript with timestamps |
| 3-4 | Speaker Separation | `pyannote.audio`, `whisperx` | Same audio → "Speaker 1:", "Speaker 2:" labels |
| 5-6 | Emotion Detection | `speechbrain`, `torchaudio` | Each speaker line shows emotion + confidence |
| 7-8 | Scene Classification | Rule-based + `ollama` (local LLM) | Detect "tension", "calm", "conflict" from tone shifts |
| 9-10 | Real-time Pipeline | `sounddevice`, `asyncio` | Speak live → get tone + scene in <2s |

## 🔧 Current Model Research Status

### ✅ Confirmed Choices:
- **Transcription**: WhisperX for word-level timestamps with diarization - combines Whisper + pyannote
- **Diarization**: Pyannote v3.1 achieves ~10% error rate vs Nemo's higher rates
- **Emotion**: SpeechBrain classifies "neutral", "happy", "sad", "angry"

### 🔄 Still Exploring:
- **Real-time latency**: FastAPI + Whisper for real-time processing but need benchmarks
- **Scene classification**: Manual rules vs local LLM (ollama) 
- **Audio chunking**: Optimal size for streaming without over-segmentation

## 🎯 Implementation Decisions Made

**Week 1 Focus**: File-based pipeline (not real-time yet)
- Start with `.wav` files → structured output
- Get transcription + diarization working reliably
- Add basic emotion detection

**Architecture**: Modular pipeline blocks that can be swapped
- `audio_processor.py` - handles file loading/chunking
- `transcription.py` - WhisperX integration  
- `emotion_detector.py` - SpeechBrain models
- `scene_classifier.py` - rule-based initially

## 📊 Data Strategy

**Test Audio Sources**:
1. 2-3 minute podcast clips (varied emotions)
2. Phone call recordings (if available)
3. Live mic recording (own voice with different tones)

**Labeling Approach**:
- Manual emotion tags for validation
- Simple scene labels: `calm`, `tension`, `conflict`, `resolution`

## ⚠️ Current Blockers & Questions

**Technical**:
- pyannote.audio licensing - need to verify for commercial use
- GPU vs CPU performance on local machine
- Whisper language detection errors with short segments - may need longer chunks

**Design**:
- Emotion taxonomy: Stick with SpeechBrain's 4 emotions or expand?
- Scene beats: How granular should the classification be?
- Real-time buffer size: Balance latency vs accuracy

## 🧪 Next Tests to Run

1. **Benchmark faster-whisper vs WhisperX** on 5-min audio sample
2. **Test pyannote.audio** speaker separation accuracy on multi-speaker sample  
3. **SpeechBrain emotion model** confidence thresholds
4. **Measure end-to-end latency** for 30-second audio chunk

## 💡 Ideas for V2 (Post-MVP)

- Visual waveform with emotion overlay
- Export to video editing tools (Premiere, DaVinci)
- Custom emotion model training
- Multi-language support
- Kubernetes deployment

# Setup Troubleshooting Log
- Encountered PyAudio install error due to missing PortAudio on macOS. Fixed by running `brew install portaudio` before `pip install -r requirements.txt`.
- All requirements now install successfully. This is a common macOS gotcha for audio projects.

# AUDIO INGESTION: Fast Path Decision
- Decision: To finish audio ingestion quickly, will focus on file-based ingestion (.wav/.mp3) and defer mic capture (TODO).
- .wav chosen as the working format for the pipeline (uncompressed, compatible with all modules).
- Plan: implement .wav loader and ffmpeg conversion in main.py, then run end-to-end test with a sample file.

# AUDIO INGESTION: Planning & Research
- Next steps: Confirm all audio dependencies are importable in Python, then scaffold main.py with empty functions for mic capture, .wav loading, and ffmpeg conversion.
- Research: `sounddevice` is the standard for cross-platform mic capture in Python; on macOS, permissions may require user approval. For .wav loading, `soundfile` or `scipy.io.wavfile` are common. `ffmpeg-python` can be used for format conversion if needed.
- Will implement placeholder (stub) functions first, then test imports and permissions.

# AUDIO INGESTION: ffmpeg Binary Issue
- Issue: ffmpeg-python failed because the ffmpeg binary was not installed or not in PATH ([Errno 2] No such file or directory: 'ffmpeg').
- Fix: Installed ffmpeg using Homebrew: `brew install ffmpeg`.
- Reasoning: ffmpeg is a system-level tool, not a Python package, so it cannot be added to requirements.txt. It must be installed via Homebrew (macOS) or another package manager, and tracked in a separate setup file for reproducibility.