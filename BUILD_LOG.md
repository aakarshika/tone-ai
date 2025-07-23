# 📊 BUILD LOG: Audio Tone AI

> Daily progress tracker - what ran, what didn't, what was learned

---

## Day 0 - Project Setup
**Date**: [Add today's date]

### ✅ What Worked:
- Created project structure
- Set up collaboration rules and gameplan
- Initialized git repository

### ❌ What Didn't Work: ffmpeg binary missing, causing [Errno 2] and conversion failure in main.py.
### 📚 What Was Learned: ffmpeg must be installed via Homebrew (not pip), and should be tracked in a separate setup file for system dependencies.
### 🎯 Tomorrow's Focus: Continue audio ingestion pipeline after verifying ffmpeg install and successful mp3→wav conversion.

### 🔄 What Was Skipped:
- 

### 🧠 Notes & Decisions:
- Starting with file-based pipeline before real-time
- Using local-first approach with API fallbacks

---

## Day 1 - Audio Ingestion & Transcription
**Date**: [Fill when working]

### ✅ What Worked:
- 

### ❌ What Didn't Work:
- 

### 📚 What Was Learned:
- 

### 🔄 What Was Skipped:
- 

### 🎯 Tomorrow's Focus:
- 

### 🧠 Notes & Decisions:
- 

---

## Day 2 - Speaker Diarization
**Date**: [Fill when working]

### ✅ What Worked:
- 

### ❌ What Didn't Work:
- 

### 📚 What Was Learned:
- 

### 🔄 What Was Skipped:
- 

### 🎯 Tomorrow's Focus:
- 

### 🧠 Notes & Decisions:
- 

---

## 📈 Weekly Summary Template

### Week 1 Goals:
- [ ] Audio file → Text transcription working
- [ ] Basic speaker separation implemented
- [ ] Simple UI for file upload/results

### Major Blockers:
- 

### Key Learnings:
- 

### Architecture Decisions:
- 

---

## 🔧 Technical Notes

### Dependencies Installed:
```bash
# Add as you install
pip install faster-whisper
pip install torch torchaudio
# etc.
```

### Hardware/Performance Notes:
- GPU: [Your GPU info]
- RAM usage during processing: [Track this]
- Processing speed benchmarks: [Add as you test]

### Model Download Status:
- [ ] Whisper models downloaded
- [ ] Pyannote models downloaded  
- [ ] SpeechBrain emotion models downloaded

---

## 🐛 Bug Tracker

### Active Issues:
- 

### Resolved Issues:
- 

### Workarounds Applied:
-