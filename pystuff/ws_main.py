"""
Refactored WebSocket Backend
Uses the new modular pipeline system for better maintainability.
"""

import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import PipelineOrchestrator, PipelineConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize pipeline orchestrator
pipeline_orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup."""
    global pipeline_orchestrator
    try:
        # Load configuration if available, otherwise use defaults
        config = PipelineConfig.load_from_file("pipeline_config.json")
        if config is None:
            config = PipelineConfig()
            config.save_to_file("pipeline_config.json")
        
        pipeline_orchestrator = PipelineOrchestrator(config)
        logger.info("Pipeline orchestrator initialized successfully")
        
        # Log pipeline status
        status = pipeline_orchestrator.get_pipeline_status()
        logger.info(f"Pipeline status: {status}")
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        pipeline_orchestrator = None

@app.get("/")
def index():
    """Main page with server information."""
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <title>Tone AI Pipeline Backend</title>
            <style>
                body { font-family: sans-serif; background: #f8f8f8; color: #222; margin: 0; padding: 0; }
                .container { max-width: 800px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 32px; }
                h1 { margin-top: 0; color: #2563eb; }
                pre { background: #222; color: #fff; padding: 12px; border-radius: 6px; font-size: 13px; overflow-x: auto; }
                .status { background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 6px; padding: 16px; margin: 16px 0; }
                .endpoint { background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; padding: 12px; margin: 8px 0; }
            </style>
        </head>
        <body>
            <div class='container'>
                <h1>🎵 Tone AI Pipeline Backend</h1>
                <p>Modular audio processing pipeline with real-time transcription capabilities.</p>
                
                <div class='endpoint'>
                    <strong>WebSocket Endpoint:</strong> <code>ws://127.0.0.1:8000/ws/audio</code>
                </div>
                
                <div class='endpoint'>
                    <strong>Status Endpoint:</strong> <code>GET /status</code>
                </div>
                
                <div class='endpoint'>
                    <strong>Config Endpoint:</strong> <code>GET /config</code>
                </div>
                
                <h3>Pipeline Status</h3>
                <div class='status'>
                    <pre id='status'>Loading...</pre>
                </div>
                
                <h3>Features</h3>
                <ul>
                    <li>✅ Modular pipeline architecture</li>
                    <li>✅ Real-time audio chunk processing</li>
                    <li>✅ Overlapping chunk support</li>
                    <li>✅ Configurable Whisper models</li>
                    <li>✅ Async processing</li>
                    <li>🔄 Speaker diarization (coming soon)</li>
                    <li>🔄 Emotion detection (coming soon)</li>
                </ul>
                
                <script>
                // Fetch and display pipeline status
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').textContent = JSON.stringify(data, null, 2);
                    })
                    .catch(error => {
                        document.getElementById('status').textContent = 'Error loading status: ' + error;
                    });
                </script>
            </div>
        </body>
        </html>
        """
    )

@app.get("/status")
async def get_status():
    """Get pipeline status."""
    if pipeline_orchestrator is None:
        return {"error": "Pipeline not initialized"}
    
    return pipeline_orchestrator.get_pipeline_status()

@app.get("/config")
async def get_config():
    """Get current pipeline configuration."""
    if pipeline_orchestrator is None:
        return {"error": "Pipeline not initialized"}
    
    return pipeline_orchestrator.config.to_dict()

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio processing."""
    await websocket.accept()
    logger.info("[WS] Client connected")
    
    if pipeline_orchestrator is None:
        await websocket.send_json({
            "error": "Pipeline not initialized"
        })
        return
    
    try:
        while True:
            # Receive audio chunk data
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            chunk_idx = msg["chunk_idx"]
            sample_rate = msg["sample_rate"]
            audio_b64 = msg["audio"]
            
            logger.info(f"[WS] Received chunk {chunk_idx + 1}, samples={len(audio_b64)} chars")
            
            # Process the audio chunk through the pipeline
            try:
                result = await pipeline_orchestrator.process_audio_chunk(
                    audio_b64, chunk_idx, sample_rate
                )
                
                # Send result back to client
                await websocket.send_json({
                    "chunk_idx": chunk_idx,
                    "transcript": result["transcript"],
                    "language": result.get("language"),
                    "processing_time": result.get("processing_time"),
                    "status": result["status"]
                })
                
                logger.info(f"[WS] Sent transcript for chunk {chunk_idx + 1}")
                
            except Exception as e:
                logger.error(f"[WS] Error processing chunk {chunk_idx + 1}: {e}")
                await websocket.send_json({
                    "chunk_idx": chunk_idx,
                    "transcript": f"[ERROR] {str(e)}",
                    "status": "error"
                })
                
    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
    except Exception as e:
        logger.error(f"[WS] WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 