# Monitor Agent

AI-powered live stream monitoring system that captures audio from LiveNOW Fox, transcribes using local Whisper, and generates AI summaries with Groq.

## Features

- **Live Stream Capture** - Extracts 60-second audio segments from LiveNOW Fox using FFMPEG
- **Playwright URL Fetching** - Automated browser captures fresh stream URLs every 15 minutes (handles expiration)
- **Local Whisper Transcription** - Speech-to-text runs completely offline (no API key needed, ~140MB model)
- **Groq AI Summaries** - Fast 15-word summaries using llama-3.1-8b-instant
- **FastAPI Backend** - RESTful API with full WebSocket support for real-time updates
- **Supabase Database** - Persistent storage for all transcripts and summaries
- **Professional Frontend** - Clean table-based UI with real-time WebSocket updates
- **Real-time Updates** - WebSocket pushes new transcripts instantly to all connected clients

## Tech Stack

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - Modern async web framework with CORS support
- **OpenAI Whisper** - Local speech recognition (base model, ~140MB, runs on CPU)
- **Groq API** - Fast LLM inference for summarization (llama-3.1-8b-instant)
- **FFMPEG 8.0.1** - Audio/video processing and stream capture
- **Playwright** - Headless Chromium browser for automated URL fetching (intercepts network requests)
- **Supabase** - PostgreSQL database with real-time capabilities and RLS policies
- **uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework with hooks
- **Vite** - Fast build tool and dev server
- **Supabase Client** - Real-time database queries and subscriptions
- **WebSocket** - Real-time transcript updates
- **Modern CSS** - Professional table design, responsive layout

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- Git

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/ChetandeepSingh/MonitorAgent.git
cd MonitorAgent
```

2. **Set up Backend**
```bash
cd backend
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**
```bash
playwright install chromium
```

5. **Configure backend environment**

Create `backend/.env`:
```env
# Groq API (Get free key at: https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

6. **Set up Frontend**
```bash
cd ../frontend
npm install
```

7. **Configure frontend environment**

Create `frontend/.env`:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your_supabase_anon_key_here
```

8. **Set up Supabase Database**

Follow the detailed guide in [SUPABASE_SETUP.md](SUPABASE_SETUP.md) to:
- Create a Supabase project
- Set up the database table with RLS policies
- Get your credentials

## Usage

### How It Works

1. **Playwright URL Fetching**: Opens LiveNOW Fox in headless Chromium, intercepts m3u8 stream URL
2. **Stream Capture**: FFMPEG uses URL to extract 60-second audio segments (16kHz mono WAV)
3. **Auto-Refresh**: Every 15 minutes, Playwright fetches fresh URL (stream URLs expire)
4. **Transcription**: Local Whisper processes each audio file (runs offline on CPU)
5. **Summarization**: Groq generates 15-word AI summary
6. **Storage**: Saves to Supabase database automatically
7. **Broadcasting**: WebSocket pushes new transcripts to all connected clients instantly

### Start the Backend Server

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
python app.py
```

Server will start at: **http://localhost:8000**

**Backend logs will show**:
- Supabase client initialized
- Whisper model loaded on cpu
- Stream URL captured
- Audio segments being processed
- Transcripts saved to database

### Start the Frontend

In a new terminal:
```bash
cd frontend
npm run dev
```

Frontend will start at: **http://localhost:5173**

Open your browser and navigate to `http://localhost:5173`

### Using the Application

1. Click **Start Monitoring** to begin capturing the live stream
2. Wait ~60 seconds for the first transcript
3. View transcripts as they appear in real-time
4. Click on a transcript card to see the full text
5. Click **Stop Monitoring** when done

All transcripts are automatically saved to Supabase and will persist across sessions.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/start` | Start stream monitoring & transcription |
| POST | `/api/stop` | Stop monitoring |
| GET | `/api/status` | Get current status & processed count |
| GET | `/api/transcripts?limit=50` | Get recent transcripts |
| WS | `/ws` | WebSocket for real-time updates |

### Example API Calls

**Start Monitoring:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/start" -Method POST
```

**Check Status:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/status" -Method GET
```

**Get Latest Transcripts:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/transcripts?limit=5" -Method GET
```

### Test Transcription

Test the complete pipeline with existing audio files:
```bash
cd backend
python test_transcription.py
```

## 📁 Project Structure

```
MonitorAgent/
├── backend/
│   ├── app.py                      # FastAPI application entry point
│   ├── config.py                   # Settings & environment variables
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (not in git)
│   ├── services/
│   │   ├── stream_service.py       # Stream capture & FFMPEG management
│   │   └── transcription_service.py # Whisper + Groq integration
│   ├── utils/
│   │   └── url_fetcher.py          # Playwright URL auto-fetcher
│   ├── output/
│   │   └── audio/                  # Generated 60s audio segments
│   └── venv/                       # Python virtual environment
├── tools/
│   └── ffmpeg-8.0.1-essentials_build/ # FFMPEG binaries
├── frontend/                       # React app (coming soon)
├── .gitignore
├── .vscode/
│   └── settings.json              # VS Code Python config
└── README.md
```

## 🔄 How It Works

1. **Stream Capture**: FFMPEG connects to LiveNOW Fox HLS stream and captures 60-second audio segments in WAV format
2. **URL Management**: Playwright automatically fetches fresh m3u8 URLs every 15 minutes (URLs expire quickly)
3. **Transcription**: Local Whisper base model transcribes audio completely offline (~8-10 seconds per minute)
4. **Summarization**: Groq API generates concise 15-word summaries using llama-3.1-8b-instant (~0.5 seconds)
5. **Storage**: Transcripts and summaries stored in memory (Supabase integration coming soon)

## ⚡ Performance

- **Audio Capture**: Real-time (60-second segments)
- **Transcription**: ~8-10 seconds per minute of audio (CPU, base model)
- **Summarization**: ~0.5 seconds (Groq API)
- **Total Latency**: ~10-15 seconds from speech to summary

## 🎛️ Whisper Models

Available models (trade-off between speed and accuracy):

| Model | Parameters | RAM Usage | Speed (Relative) |
|-------|-----------|-----------|------------------|
| `tiny` | 39M | ~1GB | Fastest |
| `base` | 74M | ~1GB | **Default** ⭐ |
| `small` | 244M | ~2GB | Slower |
| `medium` | 769M | ~5GB | Slow |
| `large` | 1550M | ~10GB | Slowest |

Change model in `services/transcription_service.py`:
```python
# In TranscriptionService.__init__()
self.model = whisper.load_model("base")  # Change to "small", "medium", etc.
```

## 🔑 API Keys

### Groq API (Required)
1. Sign up at: https://console.groq.com
2. Create an API key (free tier: 30 requests/min)
3. Add to `.env`: `GROQ_API_KEY=gsk_...`

### Supabase (Optional - Future Use)
1. Sign up at: https://supabase.com
2. Create a project
3. Add credentials to `.env`

## ✅ Current Status

- [x] Audio extraction with FFMPEG (60s segments)
- [x] Auto URL refresh with Playwright (15-min cache)
- [x] Local Whisper transcription (base model)
- [x] Groq AI summarization (15 words)
- [x] FastAPI backend with REST endpoints
- [x] WebSocket support for real-time updates
- [x] Error handling & retry logic (3 attempts)
- [ ] Supabase database integration
- [ ] React frontend UI
- [ ] User authentication
- [ ] Multi-stream support
- [ ] Export transcripts (CSV, JSON)

## 🗺️ Roadmap

### Phase 1: Backend (Completed ✅)
- Audio capture pipeline
- Whisper transcription
- AI summarization
- REST API

### Phase 2: Frontend (In Progress 🚧)
- React UI with Start/Stop controls
- Real-time transcript display
- Summary visualization

### Phase 3: Database (Planned 📋)
- Supabase integration
- Persistent storage
- Query interface

### Phase 4: Enhancements (Future 🔮)
- Multiple stream sources
- User authentication
- Export functionality
- Performance metrics dashboard

## 🐛 Troubleshooting

**Issue: Whisper transcription fails**
- Ensure FFMPEG is accessible (check `tools/ffmpeg-8.0.1-essentials_build/bin/`)
- Verify audio files exist in `backend/output/audio/`

**Issue: "Invalid API Key" for Groq**
- Get a fresh API key from https://console.groq.com/keys
- Update `.env` file with correct key
- Restart the backend server

**Issue: Stream URL expired (403 Forbidden)**
- URL auto-refresh happens every 15 minutes
- Manually restart monitoring if needed: `POST /api/stop` then `POST /api/start`

**Issue: Pylance import warnings in VS Code**
- These are IDE warnings, not runtime errors
- Code runs correctly in virtual environment
- Reload VS Code window to refresh: `Ctrl+Shift+P` → "Reload Window"

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Groq](https://groq.com) - Fast LLM inference
- [LiveNOW Fox](https://www.livenowfox.com) - Live stream source
- [FastAPI](https://fastapi.tiangolo.com) - Web framework

## 📞 Support

For issues or questions:
- Open a [GitHub Issue](https://github.com/ChetandeepSingh/MonitorAgent/issues)
- Check existing issues for solutions

---

**Built with ❤️ for real-time media monitoring**
