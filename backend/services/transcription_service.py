"""
Transcription Service using Local OpenAI Whisper
Monitors audio files and generates transcripts + summaries
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime
import os
import whisper
import torch
from groq import Groq
from config import settings

# Ensure FFMPEG is in PATH (required by Whisper)
FFMPEG_PATH = Path(__file__).parent.parent.parent / "tools" / "ffmpeg-8.0.1-essentials_build" / "bin"
if FFMPEG_PATH.exists():
    os.environ["PATH"] = str(FFMPEG_PATH) + os.pathsep + os.environ.get("PATH", "")

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service to monitor audio files and generate transcriptions using local Whisper"""
    
    def __init__(self, model_name: str = "base"):
        self.audio_dir = Path("output/audio")
        self.processed_files = set()
        self.is_monitoring = False
        self.latest_transcripts = []
        
        # Initialize Groq client for AI summaries
        self.groq_client = Groq(api_key=settings.groq_api_key)
        
        # Load local Whisper model
        # Available models: tiny, base, small, medium, large
        # 'base' is a good balance between speed and accuracy (~140MB)
        logger.info(f"Loading Whisper '{model_name}' model locally...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_name, device=device)
        logger.info(f"✓ Whisper model loaded on {device}")
        
    async def start_monitoring(self):
        """Start monitoring for new audio files"""
        self.is_monitoring = True
        logger.info("Started monitoring for audio files and transcription")
        
        while self.is_monitoring:
            try:
                await self._check_new_files()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in transcription monitoring: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_new_files(self):
        """Check for new audio files and process them"""
        if not self.audio_dir.exists():
            return
        
        audio_files = sorted(self.audio_dir.glob("audio_*.wav"))
        
        for audio_file in audio_files:
            if audio_file not in self.processed_files:
                logger.info(f"Found new audio file: {audio_file.name}")
                await self._process_audio_file(audio_file)
                self.processed_files.add(audio_file)
    
    async def _process_audio_file(self, audio_file: Path):
        """Process a single audio file - transcribe and summarize"""
        try:
            file_size = audio_file.stat().st_size
            logger.info(f"Processing: {audio_file.name} ({file_size} bytes)")
            
            # Extract timestamp from filename: audio_YYYYMMDD_HHMMSS.wav
            timestamp = self._extract_timestamp(audio_file.name)
            
            # Transcribe using OpenAI Whisper
            transcript = await self._transcribe_audio(audio_file)
            
            if not transcript:
                logger.warning(f"No transcript generated for {audio_file.name}")
                return
            
            # Generate AI summary (15 words max)
            summary = await self._generate_summary(transcript)
            
            # Store result
            result = {
                "timestamp": timestamp.isoformat(),
                "video_start": timestamp.isoformat(),
                "video_end": (timestamp).isoformat(),  # Will calculate properly later
                "filename": audio_file.name,
                "transcript": transcript,
                "summary": summary
            }
            
            self.latest_transcripts.append(result)
            
            logger.info(f"✓ Processed {audio_file.name}")
            logger.info(f"  Transcript: {transcript[:100]}...")
            logger.info(f"  Summary: {summary}")
            
            # TODO: Save to Supabase
            
        except Exception as e:
            logger.error(f"Error processing {audio_file.name}: {str(e)}", exc_info=True)
    
    def _extract_timestamp(self, filename: str) -> datetime:
        """Extract timestamp from audio filename"""
        try:
            # Format: audio_YYYYMMDD_HHMMSS.wav
            timestamp_str = filename.replace("audio_", "").replace(".wav", "")
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except ValueError:
            logger.warning(f"Could not parse timestamp from {filename}")
            return datetime.now()
    
    async def _transcribe_audio(self, audio_file: Path) -> str:
        """Transcribe audio using local Whisper model"""
        try:
            logger.info(f"Transcribing {audio_file.name} with local Whisper...")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(
                None,
                self._whisper_transcribe,
                audio_file
            )
            
            return transcript
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None
    
    def _whisper_transcribe(self, audio_file: Path) -> str:
        """Synchronous local Whisper transcription"""
        # Ensure we use absolute path
        audio_path = audio_file.resolve()
        logger.info(f"Transcribing: {audio_path}")
        
        result = self.model.transcribe(
            str(audio_path),
            language="en",
            fp16=False  # Use FP32 for CPU compatibility
        )
        return result["text"].strip()
    
    async def _generate_summary(self, transcript: str) -> str:
        """Generate AI summary using Groq LLM (15 words max)"""
        try:
            logger.info("Generating AI summary with Groq...")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(
                None,
                self._groq_summarize,
                transcript
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            # Fallback to first 15 words
            words = transcript.split()
            return " ".join(words[:15]) + "..." if len(words) > 15 else transcript
    
    def _groq_summarize(self, transcript: str) -> str:
        """Synchronous Groq API call for summarization"""
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast and accurate
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise summarizer. Create summaries in EXACTLY 15 words or less. Capture the key point only."
                },
                {
                    "role": "user",
                    "content": f"Summarize this transcript in exactly 15 words or less:\n\n{transcript}"
                }
            ],
            temperature=0.3,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    
    def stop_monitoring(self):
        """Stop monitoring for audio files"""
        self.is_monitoring = False
        logger.info("Stopped transcription monitoring")
    
    def get_processed_count(self):
        """Get count of processed audio files"""
        return len(self.processed_files)
    
    def get_latest_transcripts(self, limit=10):
        """Get the most recent transcripts"""
        return self.latest_transcripts[-limit:]
