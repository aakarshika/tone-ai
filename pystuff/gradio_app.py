import gradio as gr
import numpy as np
import time

CHUNK_SEC = 1  # Reduced to 1s for easier testing

# Helper to split audio into 5-second chunks
def split_audio_chunks(data, sample_rate, chunk_sec=CHUNK_SEC):
    chunk_samples = int(chunk_sec * sample_rate)
    total_samples = len(data)
    chunks = []
    for start in range(0, total_samples, chunk_samples):
        end = min(start + chunk_samples, total_samples)
        chunk = data[start:end]
        chunks.append(chunk)
    print(f"[DEBUG] split_audio_chunks: {len(chunks)} chunks, sample_rate={sample_rate}, total_samples={total_samples}")
    return chunks

# Simulate transcript for a chunk
def simulate_chunk_transcript(chunk_idx, chunk_sec):
    print(f"[DEBUG] Simulating transcript for chunk {chunk_idx+1}, duration={chunk_sec:.1f}s")
    time.sleep(0.2)  # Shorter delay for debug
    # Simulate actual transcript text
    return f"This is the transcript for chunk {chunk_idx+1} covering {chunk_sec:.1f} seconds."

# Generator for incremental chunk processing (mic)
def process_and_transcribe_stream(audio):
    if audio is None:
        print("[DEBUG] No audio input.")
        yield [], ""
        return
    sample_rate, data = audio
    print(f"[DEBUG] Received audio: sample_rate={sample_rate}, data_shape={data.shape}")
    if data.ndim > 1:
        data = data[:, 0]  # Use first channel if stereo
        print(f"[DEBUG] Converted to mono: new_shape={data.shape}")
    chunks = split_audio_chunks(data, sample_rate)
    table = []
    all_text = []
    for idx, chunk in enumerate(chunks):
        chunk_sec = len(chunk) / sample_rate
        transcript = simulate_chunk_transcript(idx, chunk_sec)
        table.append([f"Chunk {idx+1}", f"{chunk_sec:.1f}s", transcript])
        all_text.append(transcript)
        print(f"[DEBUG] Yielding {len(table)} rows to table.")
        yield table.copy(), "\n".join(all_text)

# Process the full audio file
def process_and_transcribe(audio):
    if audio is None:
        print("[DEBUG] No audio input.")
        return [], ""
    sample_rate, data = audio
    print(f"[DEBUG] Received audio: sample_rate={sample_rate}, data_shape={data.shape}")
    if data.ndim > 1:
        data = data[:, 0]  # Use first channel if stereo
        print(f"[DEBUG] Converted to mono: new_shape={data.shape}")
    chunks = split_audio_chunks(data, sample_rate)
    table = []
    all_text = []
    for idx, chunk in enumerate(chunks):
        chunk_sec = len(chunk) / sample_rate
        transcript = simulate_chunk_transcript(idx, chunk_sec)
        table.append([f"Chunk {idx+1}", f"{chunk_sec:.1f}s", transcript])
        all_text.append(transcript)
    print(f"[DEBUG] Returning {len(table)} rows to table.")
    return table, "\n".join(all_text)

with gr.Blocks() as demo:
    gr.Markdown("# Tone AI - Chunked Transcript Table Demo (with Logs, 1s Chunks)")
    with gr.Tab("Mic Input"):
        mic = gr.Audio(type="numpy", label="Speak now (mic always on)")
        chunk_table = gr.Dataframe(headers=["Chunk", "Duration", "Transcript"], interactive=False)
        transcript_box = gr.Textbox(label="All Transcripts", lines=6, interactive=False)
        def mic_submit(audio):
            yield from process_and_transcribe_stream(audio)
        mic.stream(mic_submit, inputs=mic, outputs=[chunk_table, transcript_box])
    with gr.Tab("File Upload"):
        file_audio = gr.Audio(type="numpy", label="Upload Audio File")
        file_chunk_table = gr.Dataframe(headers=["Chunk", "Duration", "Transcript"], interactive=False)
        file_transcript_box = gr.Textbox(label="All Transcripts", lines=6, interactive=False)
        def file_submit(audio):
            return process_and_transcribe(audio)
        file_audio.change(file_submit, inputs=file_audio, outputs=[file_chunk_table, file_transcript_box])

demo.launch() 