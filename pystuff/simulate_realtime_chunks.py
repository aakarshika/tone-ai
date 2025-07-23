import soundfile as sf
import time
import numpy as np
import os
import subprocess

CHUNK_SEC = 1  # 1 second per chunk
AUDIO_FILE = "/Users/aakarshika/Dev/audio_ai_tone/pystuff/input_lori_jo.mp3"  # Change as needed
WAV_FILE = AUDIO_FILE.replace('.mp3', '.wav')

# Convert MP3 to WAV using ffmpeg if needed
def convert_mp3_to_wav(mp3_path, wav_path):
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"[SIM] MP3 file not found: {mp3_path}")
    print(f"[SIM] Converting {mp3_path} to {wav_path} using ffmpeg...")
    result = subprocess.run([
        "ffmpeg", "-y", "-i", mp3_path, wav_path
    ], capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode())
        raise RuntimeError(f"[SIM] ffmpeg conversion failed!")
    print(f"[SIM] Conversion complete.")

# Placeholder for backend processing (replace with real API call)
def process_chunk(chunk_data, sample_rate, chunk_idx):
    print(f"[SIM] Processing chunk {chunk_idx+1}, samples={len(chunk_data)}")
    # Simulate backend processing delay
    time.sleep(0.2)
    # Simulate transcript result
    return f"Transcript for chunk {chunk_idx+1} ({len(chunk_data)/sample_rate:.1f}s)"

def split_audio_chunks(data, sample_rate, chunk_sec=CHUNK_SEC):
    chunk_samples = int(chunk_sec * sample_rate)
    total_samples = len(data)
    chunks = []
    for start in range(0, total_samples, chunk_samples):
        end = min(start + chunk_samples, total_samples)
        chunk = data[start:end]
        chunks.append(chunk)
    return chunks

def main():
    # Convert MP3 to WAV if needed
    if AUDIO_FILE.endswith('.mp3'):
        if not os.path.exists(WAV_FILE):
            convert_mp3_to_wav(AUDIO_FILE, WAV_FILE)
        audio_path = WAV_FILE
    else:
        audio_path = AUDIO_FILE
    print(f"[SIM] Loading audio file: {audio_path}")
    data, sample_rate = sf.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]  # Use first channel if stereo
    chunks = split_audio_chunks(data, sample_rate)
    print(f"[SIM] Split into {len(chunks)} chunks of {CHUNK_SEC}s each.")
    for idx, chunk in enumerate(chunks):
        result = process_chunk(chunk, sample_rate, idx)
        print(f"[SIM] Result: {result}")
        time.sleep(0.5)  # Simulate real-time delay between chunks

if __name__ == "__main__":
    main() 