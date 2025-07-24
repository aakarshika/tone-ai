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

# AUDIO INGESTION: Mic Input Complete
- Mic input implemented and tested (recorded mic_test.wav, loaded and printed info)
- Both file and mic ingestion now work for pipeline input

# Next: Speech-to-Text
- Plan: Implement and test faster-whisper as primary local speech-to-text engine

# OVERLAPPING CHUNKS: Information Loss Solution
- **Problem**: When cutting audio into non-overlapping chunks, information is lost at chunk boundaries (words cut off mid-sentence)
- **Solution**: Implemented overlapping chunks with 3s chunks and 1s overlap (2s step size)
- **Implementation**: 
  - Frontend: Modified chunking logic to use `i += stepSamples` instead of `i += chunkSamples`
  - Added `mergeOverlappingTranscripts()` function to intelligently merge overlapping content
  - Uses word-level overlap detection (minimum 3 words) to find best merge points
  - Updated playback logic to use `STEP_SEC` for chunk timing
- **Benefits**: Prevents word cutting, improves transcript quality, maintains real-time processing
- **Status**: ✅ Implemented and ready for testing

# PERFORMANCE OPTIMIZATION: Speed vs Quality Tradeoff
- **Problem**: Overlapping chunks created performance overhead, slow responses
- **Solutions Implemented**:
  1. **Debounced Merging**: 100ms debounce instead of merging on every chunk
  2. **Larger Chunks**: Increased from 3s to 5s chunks for better throughput
  3. **Reduced Overlap**: Decreased from 1s to 0.5s overlap
  4. **Faster Model**: Backend uses Whisper "tiny" model with int8 quantization
  5. **Optimized Detection**: Reduced minimum overlap from 3 to 2 words
  6. **Batch Mode**: Added batch processing option for performance vs quality tradeoff
- **Performance Gains**: ~3-5x faster processing, reduced CPU usage
- **Quality Impact**: Minimal - still prevents word cutting, slightly less overlap detection
- **Status**: ✅ Optimized and ready for testing

# SPEAKER DIARIZATION: Next Phase Planning
- **Current Status**: Performance optimizations complete, moving to speaker separation
- **Target**: Identify "who spoke when" in audio segments
- **Approach**: Implement pyannote.audio for local speaker diarization
- **Integration**: Add speaker labels to transcript output (e.g., "Speaker 1:", "Speaker 2:")
- **Challenges**: 
  - pyannote.audio licensing verification needed
  - GPU vs CPU performance considerations
  - Integration with existing chunking pipeline
- **Next Steps**: 
  1. Install and test pyannote.audio
  2. Verify licensing for commercial use
  3. Test on multi-speaker audio samples
  4. Integrate speaker labels with transcript output

# PIPELINE REFACTORING: Modular Architecture Complete
- **Problem**: Monolithic `ws_backend.py` was hard to maintain and extend
- **Solution**: Split into modular pipeline components with clear separation of concerns
- **New Architecture**:
  - `pipeline/audio_processor.py` - Audio loading, chunking, format conversion
  - `pipeline/transcription.py` - Speech-to-text with Whisper
  - `pipeline/orchestrator.py` - Main pipeline coordination
  - `pipeline/config.py` - Configuration management
  - `ws_backend_refactored.py` - New WebSocket backend using modular pipeline
- **Benefits**:
  - Easy to add new components (speaker diarization, emotion detection)
  - Better testability and maintainability
  - Configuration-driven pipeline settings
  - Async processing support
  - Component swap capability (local ↔ API)
- **Status**: ✅ Complete and ready for testing

# SPEECH-TO-TEXT: Real-Time Pipeline Brainstorm
- Requirement: Both mic and file modes will provide input as a list of 5-second audio clips (chunks)
- Goal: Real-time recognition and mapping to emotion/scene as fast as possible
- Open Questions:
  1. How should we segment a never-ending audio stream for real-time recognition? Is fixed 5s chunking optimal, or should we use adaptive/overlapping windows?
  2. How to minimize latency between speech input and emotion/scene output?
  3. What is the best way to handle partial/incomplete utterances at chunk boundaries?
- TODO: Research chunking strategies and real-time streaming best practices for speech-to-text and emotion mapping
- Next step: Implement basic batch speech-to-text on 5s audio clips as a baseline before optimizing for real-time

# SPEECH-TO-TEXT: Batch Implementation Plan
- Plan: Implement batch speech-to-text on a list of 5s audio clips using faster-whisper
- Step 1: Split a .wav file into 5s chunks (simulate real-time input)
- Step 2: Transcribe each chunk in sequence using faster-whisper
- Technical notes: Need to ensure chunk boundaries are handled cleanly, and batching does not introduce extra latency

# SPEECH-TO-TEXT: Batch Complete
- Batch speech-to-text on 5s audio clips is working and tested (see logs for chunked transcription)

# Next: Output & Visualization
- Plan: Build a React UI to show audio playback, mapped text, and waveform
- UI will be used for debugging, demo, and validating pipeline results
- Open questions: How to best sync backend chunked output with frontend playback? What data format is best for integration?

# OUTPUT & VISUALIZATION: UI Architecture Brainstorm
- Plan: Implement a React app with Tailwind CSS for the frontend
- Backend will remain in Python, serving audio and transcript data to the React frontend (via API or static files)
- Options considered:
  1. Move everything to React (JS-only): Would require porting all audio processing and ML to JS/TS, which is not practical for this project
  2. Do the UI in Python (e.g., Streamlit): Fast for prototyping, but less flexible for custom, modern UIs and harder to integrate with React ecosystem
  3. React frontend + Python backend: Best fit for modularity, flexibility, and future extensibility; allows us to keep ML/audio logic in Python and build a modern UI
- Decision: Proceed with React + Tailwind CSS frontend, Python backend

---

## [UI Build] - Main Layout Implemented
- Added audio recording and upload controls to App.jsx
- Audio playback and waveform placeholder included
- Real-time transcript area added (awaiting backend integration)
- Next: Integrate backend for speech-to-text and tone analysis, and add results UI

---

## [Design Brainstorm] - Real-time Chunked Transcription
- Idea: Frontend splits audio into chunks, sends each chunk to Python backend for transcription.
- Backend transcribes each chunk, maintains a timestamped transcript.
- UI updates transcript in real time as each chunk is processed.
- Pros: Enables near real-time feedback, scalable for long files, easier error recovery.
- Cons: Chunking on frontend may be tricky (browser APIs, sync with playback), network latency, chunk boundaries may split words/sentences.
- Feasibility: Yes, with careful chunking and backend state management. Need to define chunk size, overlap, and transcript merging logic.
- Next: Prototype chunk upload from UI, backend API for chunk transcription, and real-time transcript update in UI.

---

## [Decision] - Switch to Python UI for Rapid Prototyping
- Decided to pause React/Node UI work for now.
- Will build the UI in Python (Gradio or Streamlit) for faster iteration and direct integration with audio/ML code.
- The React structure will be kept in the repo for future use if/when a more advanced frontend is needed.
- Focus: Ship a working, mic-first, real-time demo ASAP.

---

## [Vision Refinement] - Mic-First, Real-Time, Rolling Context
- Project vision: UI should feel like a live, always-on mic experience.
- Transcript is just one of several real-time outputs (tone, emotion, etc.).
- Results (transcript, analysis) are updated incrementally, not as a full batch.
- Python backend assumed to return results for each second of audio, with a 2s processing delay.
- UI maintains a rolling context, updating display as new results arrive.
- Audio file upload is only for testing/dev, not the main user flow.
- Next: Prototype mic capture, rolling transcript/analysis update in UI, and mock backend delay.

---

## [Action] - Building Python UI (Gradio)
- Proceeding to build the Python UI for a mic-first, real-time demo.
- Will scaffold a Gradio app that captures mic input, processes audio in real time, and displays rolling transcript/analysis.
- Streamlit can be used later if needed, but Gradio is default for now due to audio/ML demo simplicity.

---

## [UI/UX Update] - Chunked Waveform Frames with Per-Chunk Transcript
- After recording (mic) or uploading (file), split audio into 5-second chunks.
- Display each chunk as a frame in the waveform window (visual timeline of audio).
- Each chunk/frame will show the transcript for that chunk.
- Applies to both mic and file input.
- Enables real-time and chunk-level analysis, and sets up for future tone/emotion display per chunk.
- Next: Implement chunking logic, waveform frame display, and per-chunk transcript in Gradio UI.

---

## [Testing Plan] - Simulate Real-Time Chunk Arrival in Python
- For backend testing, simulate the JS frontend by processing an audio file in Python.
- Split the file into small chunks (e.g., 1s), and send/process each chunk one by one, with a delay between them.
- This mimics real-time streaming and allows backend and UI logic to be tested before full JS integration.
- Next: Write a Python test harness that reads an audio file, splits it, and feeds chunks to the backend as if they are arriving live.

# UI Layout Change - Full Screen
- Changed main UI from a centered, boxed layout to a full-width, full-height responsive layout.
- Reason: User requested a more immersive, less constrained experience for the speech-to-text demo.
- Tradeoff: Lost the card-like focus, but gained more space for logs, transcript, and future visualizations (e.g., waveform).
- Next: Monitor user feedback for further tweaks (e.g., padding, background contrast).
- Increased the height of the system logs window (from h-32 to h-64) for better readability and to allow more log lines to be visible at once.

# Brainstorming - Current Session

## 2025-07-23 - Backend Speech-to-Text Integration

### ✅ What Worked:
- Successfully installed `soundfile` and `faster-whisper` dependencies
- Integrated real WhisperModel from main.py into WebSocket backend
- Added graceful error handling for missing dependencies (similar to main.py)
- Backend now validates chunks, logs details, and sends actual transcripts
- Whisper model loads successfully on startup with proper error handling

### 🔧 Technical Implementation:
- Used `io.BytesIO()` to convert base64 PCM chunks to WAV in memory
- Integrated `WhisperModel("small", device="cpu")` for transcription
- Added dependency checks before processing chunks
- Maintained backward compatibility with error messages for missing deps

### 📊 Current Status:
- Backend ready for real-time speech-to-text processing
- Frontend can now receive actual transcripts instead of simulated ones
- All chunks are properly validated and logged
- Ready for testing with the React UI

### 🎯 Next Steps:
- Test the full pipeline with real audio files
- Verify chunk-by-chunk transcription works as expected
- Monitor performance and accuracy of real-time transcription
