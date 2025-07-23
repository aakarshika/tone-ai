# 🎤 AI Tone Detector Pipeline

> Real-time AI that listens to audio, identifies speakers and emotions, and maps tone to narrative scene beats.

**Status**: 🚧 In Development (10-day MVP sprint)

---

## 🎯 What This Does

In short, this takes audio input (live mic or files) and outputs a structured timeline showing:
- **Who spoke when** (speaker diarization)
- **What they said** (speech-to-text) 
- **How they felt** (emotion detection)
- **What kind of scene** it represents (tension, calm, conflict, etc.)

**Example Output**:
```
[00:15] Speaker_1 (angry): "I can't believe you said that!" → Scene: Conflict Rising
[00:18] Speaker_2 (sad): "I'm sorry, I didn't mean it..." → Scene: Tension Peak
[00:22] Speaker_1 (calm): "Let's talk about this." → Scene: Resolution
```

---

## 🏗️ Architecture

```
Audio Input → Transcription → Diarization → Emotion → Scene Classification → Output
     ↓              ↓             ↓          ↓              ↓
   .wav files   faster-whisper  pyannote  speechbrain   rule-based
   live mic     whisper.cpp     fallback  openSMILE     + local LLM
```

**Philosophy**: Local-first, modular blocks, easy to swap components

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- ffmpeg installed
- 8GB+ RAM recommended

### Installation
```bash
git clone [your-repo]
cd audio_ai_tone
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r gameplan.txt
```

### Basic Usage
```bash
# Process audio file
python main.py --input sample.wav

# Live mic input (coming soon)
python main.py --live

# Web UI (coming soon)
streamlit run ui/app.py
```

---

## 📦 Components

### Core Pipeline Modules
- **`audio_processor.py`** - File loading, chunking, format conversion
- **`transcription.py`** - Speech-to-text with WhisperX/faster-whisper
- **`diarization.py`** - Speaker separation with pyannote.audio
- **`emotion_detector.py`** - Emotion classification with SpeechBrain
- **`scene_classifier.py`** - Narrative beat detection (rules + LLM)
- **`pipeline.py`** - Orchestrates all components

### Configuration
- **`config.yaml`** - Model paths, thresholds, API keys
- **`main.py`** - CLI interface and entry point

---

## 🧪 Development Status

**Current Sprint**: 10-day MVP (See `BUILD_LOG.md` for daily progress)

### ✅ Completed
- Project structure and collaboration workflow
- Research phase for model selection

### 🛠️ In Progress  
- Audio file loading and preprocessing
- Basic transcription with faster-whisper

### ⬜ Todo
- Speaker diarization integration
- Emotion detection implementation
- Scene classification rules
- Real-time audio processing
- Basic web UI

---

## 🔧 Technical Details

### Model Choices & Rationale
- **Transcription**: WhisperX (combines Whisper + diarization for word-level timestamps)
- **Diarization**: Pyannote v3.1 (~10% error rate, GPU recommended)
- **Emotion**: SpeechBrain (4 basic emotions: neutral, happy, sad, angry)
- **Scene**: Rule-based initially, Ollama local LLM later

### Performance Targets
- **Real-time latency**: <2s per audio chunk
- **Accuracy**: >85% transcription, >75% emotion detection
- **Resource usage**: <4GB RAM, GPU optional but recommended

### File Structure
```
audio_ai_tone/
├── main.py              # Entry point
├── config.yaml          # Configuration
├── gameplan.txt     # Dependencies
├── /scripts/            # Core modules
├── /models/             # Downloaded models (gitignored)
├── /logs/               # Runtime logs
├── /ui/                 # Streamlit interface
└── /docs/               # Additional documentation
```

---

## 🤝 Development Workflow

This project uses a structured AI-human collaboration approach:

- **`rules.md`** - Collaboration guidelines (human edits only)
- **`gameplan.md`** - Project gameplan (AI can add TODOs)  
- **`brainstorming.md`** - Working memory (both edit frequently)
- **`BUILD_LOG.md`** - Daily progress tracking

### Contributing
1. Read `rules.md` for collaboration guidelines
2. Check `brainstorming.md` for current exploration
3. Update `BUILD_LOG.md` with daily progress
4. Follow "working > optimal" philosophy

---

## 📊 Benchmarks & Validation

### Test Data
- Podcast clips with varied emotions
- Multi-speaker conversations  
- Live mic recordings

### Evaluation Metrics
- Transcription accuracy (WER)
- Speaker identification accuracy
- Emotion classification confidence
- End-to-end processing latency

---

## 🔮 Roadmap

### V1 (10-day MVP)
- File-based audio processing
- Basic web interface
- Core pipeline working end-to-end

### V2 (Future)
- Real-time streaming audio
- Advanced emotion taxonomy
- Visual waveform interface
- Export to video editing tools
