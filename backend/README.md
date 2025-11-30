# Monitor Agent Backend

FastAPI backend for live stream monitoring with local Whisper transcription and Groq AI summarization.

## Features

- **Stream Capture**: FFMPEG-based audio extraction (60-second segments)
- **Playwright URL Fetching**: Automatically captures fresh stream URLs every 15 minutes to handle expiration
- **Local Transcription**: OpenAI Whisper runs completely offline (no API key needed)
- **AI Summaries**: Groq API generates 15-word summaries
- **REST API**: Full CRUD operations for transcripts
- **WebSocket**: Real-time transcript updates pushed to all connected clients
- **Supabase Integration**: Persistent storage with automatic saves

## Tech Stack

- **Python 3.10+**
- **FastAPI** - Async web framework
- **OpenAI Whisper** - Local speech-to-text (base model, ~140MB)
- **Groq API** - Fast LLM inference (llama-3.1-8b-instant)
- **FFMPEG 8.0.1** - Audio processing
- **Playwright** - Headless browser for intercepting stream URLs
- **Supabase** - PostgreSQL database
- **uvicorn** - ASGI server

## Prerequisites

- **Python 3.10+**
- **FFMPEG** - Included in `../tools/ffmpeg-8.0.1-essentials_build/`
- **Groq API Key** - Free tier available at https://console.groq.com
- **Playwright** - For automated stream URL fetching

## Installation

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```
### 3. Install Playwright Browser

Playwright is used to automatically fetch fresh stream URLs from LiveNOW Fox:

```bash
playwright install chromium
```

This installs a headless Chromium browser that intercepts network requests to capture the m3u8 stream URL.ywright install chromium
```

```env
# Groq API (Required - Get free key at https://console.groq.com)
GROQ_API_KEY=gsk_your_api_key_here

# Supabase Database (Optional but recommended)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Stream Settings (Optional - defaults work fine)
SEGMENT_DURATION=60
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
```

**Note**: Supabase is optional. Without it, transcripts are stored in-memory only.tream Settings
SEGMENT_DURATION=60
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
## Running the Server

```bash
python app.py
```

Server starts at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `POST` | `/api/start` | Start stream monitoring | `{"status": "started", "message": "..."}` |
| `POST` | `/api/stop` | Stop monitoring | `{"status": "stopped", "message": "..."}` |
| `GET` | `/api/status` | Get current status | `{"is_running": bool, "processed_count": int}` |
| `GET` | `/api/transcripts?limit=50` | Get recent transcripts | `[{transcript objects}]` |
| `WS` | `/ws` | WebSocket connection | Real-time transcript updates | clients

API Documentation: **http://localhost:8000/docs**

## API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `POST` | `/api/start` | Start stream monitoring | `{"status": "started", "message": "..."}` |
| `POST` | `/api/stop` | Stop monitoring | `{"status": "stopped", "message": "..."}` |
| `GET` | `/api/status` | Get current status | `{"is_running": bool, "processed_count": int}` |
| `GET` | `/api/transcripts?limit=50` | Get recent transcripts | `[{transcript objects}]` |
| `WS` | `/ws` | WebSocket connection | Real-time transcript updates |

### Example Requests

**Start Monitoring:**
```bash
curl -X POST http://localhost:8000/api/start
```

**Get Status:**
```bash
curl http://localhost:8000/api/status
```

**Get Latest Transcripts:**
```bash
curl http://localhost:8000/api/transcripts?limit=10
```

**Response Example:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2025-11-30T12:46:02",
    "video_start": "2025-11-30T12:46:02",
    "video_end": "2025-11-30T12:47:02",
    "filename": "audio_20251130_124602.wav",
    "transcript": "The president announced new measures for climate action today...",
    "summary": "President announces new measures for climate action today."
  }
]
```

### WebSocket Integration

Connect to `ws://localhost:8000/ws` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'new_transcript') {
    console.log('New transcript:', message.data);
  }
};
```

## Project Structure

```
backend/
├── app.py                          # FastAPI application & endpoints
├── config.py                       # Settings & environment variables
├── requirements.txt                # Python dependencies
├── services/
│   ├── stream_service.py          # FFMPEG stream capture
│   └── transcription_service.py   # Whisper + Groq processing
└── utils/
    └── url_fetcher.py             # Playwright URL fetching
```

## File Processing Flow

1. **URL Fetching** (`utils/url_fetcher.py`)
   - Opens LiveNOW Fox in headless Chromium
   - Intercepts network requests
   - Captures m3u8 stream URL
   - Caches URL for 15 minutes

2. **Stream Capture** (`services/stream_service.py`)
   - Uses FFMPEG with captured URL
   - Extracts 60-second audio segments
   - Saves as 16kHz mono WAV files
   - Auto-refreshes URL when expired

3. **Transcription** (`services/transcription_service.py`)
   - Monitors audio directory
   - Loads Whisper model (base, ~140MB)
   - Transcribes audio on CPU
   - Generates 15-word summary via Groq
   - Saves to Supabase database
   - Broadcasts via WebSocket

## Troubleshooting

### "Failed to capture stream URL"
- Check internet connection
- Verify Playwright browser installed: `playwright install chromium`
- LiveNOW Fox might be down - check https://www.livenowfox.com/live

### "Whisper model download failed"
- First run downloads ~140MB model
- Check disk space and internet
- Model cached at `~/.cache/whisper/`

### "Groq API error"
- Verify GROQ_API_KEY in `.env`
- Check API quota at https://console.groq.com
- Free tier: 14,400 requests/day

### "Supabase connection failed"
- Verify SUPABASE_URL and SUPABASE_KEY
- Check project is active (not paused)
- Backend works without Supabase (in-memory only)

### Audio files not being processed
- Check FFMPEG is in PATH
- Verify `output/audio/` directory exists
- Check backend logs for errors
- Files <10KB are skipped (incomplete writes)

## Performance

- **Transcription**: 5-10 seconds per 60-second segment (CPU)
- **Groq API**: <1 second for summary generation
- **WebSocket Broadcast**: <100ms latency
- **Memory Usage**: ~500MB with Whisper model loaded

## Dependencies

Key packages (from `requirements.txt`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai-whisper` - Local transcription
- `groq` - AI summarization
- `playwright` - URL fetching
- `supabase` - Database client
- `python-dotenv` - Environment variables

## Development

### Running Tests
```bash
python test_transcription.py
```

### Viewing Logs
Backend logs show:
- Stream URL captures
- Audio file processing
- Transcription results
- Database saves
- WebSocket connections

### API Documentation
Interactive docs at: `http://localhost:8000/docs`

## Security Notes

- CORS enabled for `localhost:5173` only
- Supabase uses RLS policies
- API keys stored in `.env` (not committed)
- WebSocket connections authenticated via origin

Built with Python 3.10 + FastAPI + Whisper + Groq

1. **Stream Capture**: Uses yt-dlp to fetch the live stream URL from livenowfox.com
2. **Audio Extraction**: FFMPEG extracts audio in 1-minute WAV segments
3. **Segmentation**: Audio files are saved as `audio_YYYYMMDD_HHMMSS.wav`
4. **Processing**: Audio files are monitored and queued for transcription

## Output Structure

```
output/
  audio/
    audio_20231130_120000.wav
    audio_20231130_120100.wav
    ...
```

## Testing FFMPEG

To verify FFMPEG is working:

```powershell
ffmpeg -version
```

## Troubleshooting

- **FFMPEG not found**: Make sure FFMPEG is in your PATH
- **Stream URL fetch fails**: Check internet connection and site availability
- **Permission errors**: Run as administrator or check folder permissions
