import importlib

REQUIREMENTS = [
    # Audio handling
    'sounddevice', 'ffmpeg', 'pyaudio',
    # Speech-to-text
    'faster_whisper', 'whisperx', 'whisper',
    # Diarization
    'pyannote.audio', 'resemblyzer', 'webrtcvad',
    # Emotion recognition
    'speechbrain', 'opensmile', 'torchaudio', 'transformers',
    # Scene beat classification
    'ollama', 'openai',
    # Utilities
    'numpy', 'scipy', 'pandas', 'pyyaml', 'tqdm', 'matplotlib', 'aiohttp', 'asyncio', 'rich',
    # Deep learning
    'torch', 'torchaudio', 'tensorflow',
    # Optional visualization/debug
    'notebook', 'gradio',
    # Environment
    'dotenv',
]

# Map requirements.txt names to import names if different
IMPORT_ALIASES = {
    'ffmpeg-python': 'ffmpeg',
    'openai-whisper': 'whisper',
    'python-dotenv': 'dotenv',
    'pyyaml': 'yaml',
    'opensmile': 'opensmile',
    'faster-whisper': 'faster_whisper',
}


def try_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"[OK] {module_name}")
        return True
    except ImportError as e:
        print(f"[ERROR] {module_name}: {e}")
        return False


def main():
    print("[INFO] Testing all requirements imports...")
    success = 0
    total = 0
    for req in REQUIREMENTS:
        mod = IMPORT_ALIASES.get(req, req)
        # Handle submodules (e.g., pyannote.audio)
        if '.' in mod:
            mod = mod
        total += 1
        if try_import(mod):
            success += 1
    print(f"\n[SUMMARY] {success}/{total} modules imported successfully.")


if __name__ == "__main__":
    main() 