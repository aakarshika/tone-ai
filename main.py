import sys
import os

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
    RUN_MIC_TEST = True
    if RUN_MIC_TEST:
        mic_wav = "mic_test.wav"
        if record_mic_to_wav(5, mic_wav):
            load_wav_file(mic_wav) 