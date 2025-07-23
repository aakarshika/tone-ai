import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import numpy as np
import base64
import json

app = FastAPI()

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
            # Expecting JSON: {"chunk_idx": int, "sample_rate": int, "audio": base64-encoded PCM}
            msg = json.loads(data)
            chunk_idx = msg["chunk_idx"]
            sample_rate = msg["sample_rate"]
            audio_b64 = msg["audio"]
            audio_bytes = base64.b64decode(audio_b64)
            audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
            print(f"[WS] Received chunk {chunk_idx+1}, samples={len(audio_np)}, sample_rate={sample_rate}")
            # Simulate processing
            await asyncio.sleep(0.2)
            transcript = f"Transcript for chunk {chunk_idx+1} ({len(audio_np)/sample_rate:.1f}s)"
            print(f"[WS] Transcript for chunk {chunk_idx+1}: {transcript}")
            # Send result back
            await websocket.send_json({
                "chunk_idx": chunk_idx,
                "transcript": transcript
            })
            print(f"[WS] Sent transcript for chunk {chunk_idx+1}")
    except WebSocketDisconnect:
        print("[WS] Client disconnected.") 