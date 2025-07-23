import sys
import os
import numpy as np

# AUDIO INGESTION DEPENDENCIES
try:
    import soundfile as sf
except ImportError:
    print("[ERROR] soundfile not installed.")
    sf = None

try:
    import ffmpeg
except ImportError:
    print("[ERROR] ffmpeg-python not installed.")
    ffmpeg = None

try:
    import sounddevice as sd
except ImportError:
    print("[ERROR] sounddevice not installed.")
    sd = None

# SPEECH-TO-TEXT DEPENDENCIES
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("[ERROR] faster-whisper not installed.")
    WhisperModel = None


def record_mic_to_wav(duration_sec, output_path, samplerate=44100, channels=1):
    """
    Records audio from the default microphone and saves as a .wav file.
    """
    if sd is None or sf is None:
        print("[ERROR] sounddevice or soundfile not available.")
        return False
    try:
        print(f"[INFO] Recording {duration_sec}s from mic to '{output_path}'...")
        audio = sd.rec(int(duration_sec * samplerate), samplerate=samplerate, channels=channels)
        sd.wait()
        sf.write(output_path, audio, samplerate)
        print(f"[OK] Saved mic recording to '{output_path}'")
        return True
    except Exception as e:
        print(f"[ERROR] Mic recording failed: {e}")
        return False


def capture_mic_audio():
    """
    Stub for capturing audio from the microphone using sounddevice.
    """
    print("[STUB] capture_mic_audio() called. Not yet implemented.")
    # FIXME: Implement real-time mic capture
    return None


def load_wav_file(filepath):
    """
    Loads a .wav file using soundfile, prints shape and duration.
    """
    if sf is None:
        print("[ERROR] soundfile not available.")
        return None
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return None
    try:
        data, samplerate = sf.read(filepath)
        duration = len(data) / samplerate
        print(f"[OK] Loaded '{filepath}': shape={data.shape}, samplerate={samplerate}, duration={duration:.2f}s")
        return data, samplerate
    except Exception as e:
        print(f"[ERROR] Failed to load '{filepath}': {e}")
        return None


def convert_with_ffmpeg(input_path, output_path, format='wav'):
    """
    Converts an audio file to the specified format using ffmpeg-python.
    """
    if ffmpeg is None:
        print("[ERROR] ffmpeg-python not available.")
        return False
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return False
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format=format)
            .overwrite_output()
            .run(quiet=True)
        )
        if os.path.exists(output_path):
            print(f"[OK] Converted '{input_path}' to '{output_path}' (format={format})")
            return True
        else:
            print(f"[ERROR] Output file not created: {output_path}")
            return False
    except Exception as e:
        print(f"[ERROR] ffmpeg conversion failed: {e}")
        return False


def split_wav_to_chunks(wav_path, chunk_sec=5, out_dir="chunks"):
    """
    Splits a .wav file into N-second chunks and saves them to out_dir.
    Returns a list of chunk file paths.
    """
    if sf is None:
        print("[ERROR] soundfile not available.")
        return []
    if not os.path.exists(wav_path):
        print(f"[ERROR] File not found: {wav_path}")
        return []
    os.makedirs(out_dir, exist_ok=True)
    data, samplerate = sf.read(wav_path)
    total_samples = data.shape[0]
    chunk_samples = int(chunk_sec * samplerate)
    chunk_paths = []
    for i, start in enumerate(range(0, total_samples, chunk_samples)):
        end = min(start + chunk_samples, total_samples)
        chunk_data = data[start:end]
        chunk_path = os.path.join(out_dir, f"chunk_{i+1:03d}.wav")
        sf.write(chunk_path, chunk_data, samplerate)
        chunk_paths.append(chunk_path)
        print(f"[OK] Saved chunk {i+1}: {chunk_path} ({(end-start)/samplerate:.2f}s)")
    return chunk_paths


def transcribe_chunks(chunk_paths, model_size="small"):
    """
    Transcribes a list of wav files using faster-whisper.
    Logs the result for each chunk.
    """
    if WhisperModel is None:
        print("[ERROR] faster-whisper not available.")
        return
    print(f"[INFO] Loading faster-whisper model: {model_size}")
    model = WhisperModel(model_size, device="cpu")
    for i, chunk_path in enumerate(chunk_paths):
        print(f"[INFO] Transcribing chunk {i+1}: {chunk_path}")
        try:
            segments, info = model.transcribe(chunk_path)
            text = " ".join([seg.text for seg in segments])
            print(f"[TRANSCRIBE] Chunk {i+1}: {text.strip()}")
        except Exception as e:
            print(f"[ERROR] Transcription failed for {chunk_path}: {e}")


if __name__ == "__main__":
    print("[INFO] main.py started. Running file-based audio ingestion...")
    mp3_file = "input_lori_jo.mp3"
    wav_file = "output.wav"
    # Step 1: Convert mp3 to wav
    if convert_with_ffmpeg(mp3_file, wav_file):
        # Step 2: Load the resulting wav file
        load_wav_file(wav_file)
    else:
        print(f"[ERROR] Could not convert {mp3_file} to {wav_file}. Skipping .wav loading.")

    # Mic test (set to True to enable)
    RUN_MIC_TEST = False
    if RUN_MIC_TEST:
        mic_wav = "mic_test.wav"
        if record_mic_to_wav(5, mic_wav):
            load_wav_file(mic_wav)

    # Speech-to-text batch test
    RUN_STT_BATCH = True
    if RUN_STT_BATCH:
        chunk_paths = split_wav_to_chunks(wav_file, chunk_sec=5, out_dir="chunks")
        transcribe_chunks(chunk_paths, model_size="small") 