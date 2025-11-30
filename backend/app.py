from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging

from services.stream_service import StreamService
from services.transcription_service import TranscriptionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Monitor Agent API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
stream_service = None
transcription_service = None
websocket_connections = []

@app.get("/")
async def root():
    return {"message": "Monitor Agent API is running"}

@app.post("/api/start")
async def start_monitoring():
    """Start the live stream monitoring"""
    global stream_service, transcription_service
    
    try:
        if stream_service and stream_service.is_running:
            return JSONResponse(
                status_code=400,
                content={"error": "Stream is already running"}
            )
        
        stream_service = StreamService()
        transcription_service = TranscriptionService(broadcast_callback=broadcast_new_transcript)
        
        # Start the stream and transcription in background
        asyncio.create_task(stream_service.start_stream())
        asyncio.create_task(transcription_service.start_monitoring())
        
        logger.info("Stream monitoring and transcription started successfully")
        return {"status": "started", "message": "Stream monitoring initiated"}
    
    except Exception as e:
        logger.error(f"Error starting stream: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to start stream: {str(e)}"}
        )
@app.post("/api/stop")
async def stop_monitoring():
    """Stop the live stream monitoring"""
    global stream_service, transcription_service
    
    try:
        if not stream_service or not stream_service.is_running:
            return JSONResponse(
                status_code=400,
                content={"error": "No stream is currently running"}
            )
        
        await stream_service.stop_stream()
        if transcription_service:
            transcription_service.stop_monitoring()
        
        stream_service = None
        transcription_service = None
        
        logger.info("Stream monitoring stopped successfully")
        return {"status": "stopped", "message": "Stream monitoring stopped"}
    
    except Exception as e:
        logger.error(f"Error stopping stream: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to stop stream: {str(e)}"}
        )

@app.get("/api/status")
async def get_status():
    """Get current monitoring status"""
    is_running = stream_service is not None and stream_service.is_running
    processed_count = transcription_service.get_processed_count() if transcription_service else 0
    
    return {
        "is_running": is_running,
        "stream_url": "https://www.livenowfox.com/live" if is_running else None,
        "processed_audio_files": processed_count
    }

@app.get("/api/transcripts")
async def get_transcripts(limit: int = 50):
    """Get recent transcripts"""
    if not transcription_service:
        return []
    
    transcripts = transcription_service.get_latest_transcripts(limit)
    return transcripts

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time transcript updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"WebSocket connection established. Total connections: {len(websocket_connections)}")
    
    try:
        while True:
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Remaining connections: {len(websocket_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

async def broadcast_new_transcript(transcript_data: dict):
    """Broadcast new transcript to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_json({
                "type": "new_transcript",
                "data": transcript_data
            })
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {str(e)}")
            disconnected.append(websocket)
    
    for ws in disconnected:
        websocket_connections.remove(ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
