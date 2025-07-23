# System-Level Dependencies (macOS)

This file tracks non-Python dependencies required for the project, to be installed via Homebrew or other package managers.

## ffmpeg
- Install: `brew install ffmpeg`
- Reason: Required for audio file conversion (used by ffmpeg-python). Not available via pip/requirements.txt. 