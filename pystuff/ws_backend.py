import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import numpy as np
import base64
import json
import io

# SPEECH-TO-TEXT DEPENDENCIES
try:
    import soundfile as sf
except ImportError:
    print("[ERROR] soundfile not installed.")
    sf = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("[ERROR] faster-whisper not installed.")
    WhisperModel = None

app = FastAPI()

# Load Whisper model once if available
whisper_model = None
if WhisperModel is not None:
    try:
        # Use "tiny" model for faster processing
        whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("[INFO] Whisper tiny model loaded successfully for fast processing.")
    except Exception as e:
        print(f"[ERROR] Failed to load Whisper model: {e}")
        whisper_model = None

@app.get("/")
def index():
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <title>Tone AI WebSocket Backend</title>
            <style>
                body { font-family: sans-serif; background: #f8f8f8; color: #222; margin: 0; padding: 0; }
                .container { max-width: 600px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 32px; }
                h1 { margin-top: 0; }
                pre { background: #222; color: #fff; padding: 12px; border-radius: 6px; font-size: 13px; }
            </style>
        </head>
        <body>
            <div class='container'>
                <h1>Tone AI WebSocket Backend</h1>
                <p>This is the backend server for Tone AI.<br>
                WebSocket endpoint: <code>ws://127.0.0.1:8000/ws/audio</code></p>
                <p>Use your frontend or a WebSocket client to connect and stream audio chunks for real-time speech-to-text.</p>
                <h3>Server Status</h3>
                <pre id='log'>Waiting for WebSocket connections...</pre>
                <script>
                // Optionally, you could add a live log here by connecting to the WebSocket and displaying messages
                </script>
            </div>
        </body>
        </html>
        """
    )

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected.")
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            chunk_idx = msg["chunk_idx"]
            sample_rate = msg["sample_rate"]
            audio_b64 = msg["audio"]
            audio_bytes = base64.b64decode(audio_b64)
            audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
            print(f"[WS] Received chunk {chunk_idx+1}, samples={len(audio_np)}, sample_rate={sample_rate}")
            
            # Check if dependencies are available
            if sf is None or whisper_model is None:
                error_msg = "Missing dependencies: "
                if sf is None:
                    error_msg += "soundfile "
                if whisper_model is None:
                    error_msg += "faster-whisper "
                print(f"[WS] {error_msg}")
                await websocket.send_json({
                    "chunk_idx": chunk_idx,
                    "transcript": f"[ERROR] {error_msg}"
                })
                continue
            
            # Convert PCM float32 to WAV in memory
            try:
                with io.BytesIO() as wav_io:
                    sf.write(wav_io, audio_np, sample_rate, format='WAV')
                    wav_io.seek(0)
                    # Transcribe with Whisper
                    segments, info = whisper_model.transcribe(wav_io)
                    text = " ".join([seg.text for seg in segments])
                print(f"[WS] Transcript for chunk {chunk_idx+1}: {text.strip()}")
                await websocket.send_json({
                    "chunk_idx": chunk_idx,
                    "transcript": text.strip()
                })
                print(f"[WS] Sent transcript for chunk {chunk_idx+1}")
            except Exception as e:
                print(f"[WS] Error processing chunk {chunk_idx+1}: {e}")
                await websocket.send_json({
                    "chunk_idx": chunk_idx,
                    "transcript": f"[ERROR] {e}"
                })
    except WebSocketDisconnect:
        print("[WS] Client disconnected.") 