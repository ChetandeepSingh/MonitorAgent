# Monitor Agent - Live TV Stream Monitor

A real-time system that monitors live TV feeds, extracts audio, generates transcripts using OpenAI Whisper, and creates AI-powered summaries.

## Project Structure

```
Monitor Agent/
├── backend/          # Python FastAPI backend
│   ├── app.py
│   ├── services/
│   └── output/      # Generated audio files
└── frontend/        # React frontend (coming soon)
```

## Features

- 🎥 Live stream capture from livenowfox.com
- 🔊 Audio extraction in 1-minute segments using FFMPEG
- 📝 Speech-to-text transcription (OpenAI Whisper)
- 🤖 AI-generated summaries (15 words max)
- 💾 Data persistence with Supabase
- ⚡ Real-time WebSocket updates
- 🎮 Start/Stop controls

## Quick Start

### Backend Setup

1. Navigate to backend folder:
```powershell
cd backend
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure environment:
```powershell
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```powershell
python app.py
```

## Prerequisites

- Python 3.9+
- FFMPEG (must be in PATH)
- OpenAI API key
- Supabase account

## Current Status

✅ Backend structure created
✅ Stream capture with FFMPEG
✅ Audio extraction (1-minute segments)
⏳ Transcription pipeline (next)
⏳ AI summarization (next)
⏳ Frontend UI (next)
⏳ Supabase integration (next)

## Next Steps

1. Implement OpenAI Whisper transcription
2. Add GPT-4 summarization
3. Build React frontend
4. Set up Supabase database
5. Add error handling and retry logic
