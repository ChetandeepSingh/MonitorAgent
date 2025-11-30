# Monitor Agent Backend

Python FastAPI backend for monitoring live TV streams and generating transcripts with AI summaries.

## Prerequisites

1. **Python 3.9+**
2. **FFMPEG** - Must be installed and available in PATH
3. **yt-dlp** - For fetching live stream URLs

## Installation

### 1. Install FFMPEG

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```powershell
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase API key

## Running the Backend

```powershell
python app.py
```

The API will be available at: http://localhost:8000

## API Endpoints

- `POST /api/start` - Start monitoring the live stream
- `POST /api/stop` - Stop monitoring
- `GET /api/status` - Get current status
- `WebSocket /ws` - Real-time updates

## How It Works

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
