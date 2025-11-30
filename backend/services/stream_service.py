import asyncio
import subprocess
import logging
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.url_fetcher import StreamURLFetcher

logger = logging.getLogger(__name__)

class StreamService:
    """Service to handle live stream fetching and management"""
    
    def __init__(self):
        self.is_running = False
        self.process = None
        self.stream_url = None  # Will be fetched automatically
        self.url_fetcher = StreamURLFetcher()
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_data = {}
        self.retry_count = 0
        self.max_retries = 3
        
    async def start_stream(self):
        """Start capturing the live stream"""
        try:
            self.is_running = True
            logger.info(f"Starting stream capture from {self.stream_url}")
            
            # We'll use yt-dlp to get the actual stream URL from the webpage
            # Then use FFMPEG to process it
            await self._fetch_and_process_stream()
            
        except Exception as e:
            logger.error(f"Error in start_stream: {str(e)}")
            self.is_running = False
    async def _fetch_and_process_stream(self):
        """Process the stream with FFMPEG directly - with auto URL refresh"""
        while self.is_running and self.retry_count < self.max_retries:
            try:
                logger.info(f"Fetching fresh stream URL (attempt {self.retry_count + 1}/{self.max_retries})")
                
                # Get fresh URL automatically
                self.stream_url = await self.url_fetcher.get_fresh_url()
                
                if not self.stream_url:
                    logger.error("Failed to get stream URL")
                    self.retry_count += 1
                    await asyncio.sleep(5)
                    continue
                
                logger.info("Starting FFMPEG capture with fresh URL")
                
                # Start FFMPEG to capture and segment audio
                await self._start_ffmpeg_capture(self.stream_url)
                
                # If FFMPEG exits, check if we should retry
                if self.is_running:
                    logger.warning("FFMPEG process ended unexpectedly, retrying...")
                    self.retry_count += 1
                    await asyncio.sleep(5)
                else:
                    # Normal stop
                    break
                
            except Exception as e:
                logger.error(f"Error in stream processing: {str(e)}")
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    logger.info(f"Retrying in 5 seconds... ({self.retry_count}/{self.max_retries})")
                    await asyncio.sleep(5)
                else:
                    logger.error("Max retries reached, stopping stream")
                    raise
    
    async def _start_ffmpeg_capture(self, stream_url):
        """Start FFMPEG to capture and segment audio"""
        try:
            # FFMPEG command to extract audio in 1-minute segments
            # Output format: audio_YYYYMMDD_HHMMSS.wav
            output_pattern = str(self.output_dir / "audio_%Y%m%d_%H%M%S.wav")
            
            ffmpeg_cmd = [
                "ffmpeg",
                # Add headers to mimic browser request
                "-headers", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\nReferer: https://www.livenowfox.com/\r\n",
                "-i", stream_url,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # WAV format
                "-ar", "16000",  # 16kHz sample rate (good for speech recognition)
                "-ac", "1",  # Mono audio
                "-f", "segment",  # Segment the output
                "-segment_time", "60",  # 60 seconds per segment
                "-segment_format", "wav",
                "-strftime", "1",  # Enable strftime in output filename
                "-reset_timestamps", "1",
                output_pattern,
                "-y"  # Overwrite output files
            ]
            
            logger.info(f"Starting FFMPEG capture: {' '.join(ffmpeg_cmd)}")
            
            # Start FFMPEG process
            self.process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor FFMPEG output in background
            asyncio.create_task(self._monitor_ffmpeg_output())
            
            # Wait for process to complete (or be stopped)
            await self.process.wait()
            
        except Exception as e:
            logger.error(f"Error in FFMPEG capture: {str(e)}")
            raise
    
    async def _monitor_ffmpeg_output(self):
        """Monitor FFMPEG stderr output for progress"""
        try:
            while self.is_running and self.process:
                line = await self.process.stderr.readline()
                if not line:
                    break
                
                line_str = line.decode().strip()
                if line_str:
                    # Log important FFMPEG messages
                    if "time=" in line_str or "error" in line_str.lower():
                        logger.info(f"FFMPEG: {line_str}")
        
        except Exception as e:
            logger.error(f"Error monitoring FFMPEG: {str(e)}")
    
    async def stop_stream(self):
        """Stop the stream capture"""
        try:
            self.is_running = False
            
            if self.process:
                logger.info("Stopping FFMPEG process...")
                self.process.terminate()
                
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    logger.warning("FFMPEG didn't stop gracefully, killing...")
                    self.process.kill()
                    await self.process.wait()
                
                self.process = None
                logger.info("Stream capture stopped")
        
        except Exception as e:
            logger.error(f"Error stopping stream: {str(e)}")
            raise
    
    def get_audio_files(self):
        """Get list of generated audio files"""
        return sorted(self.output_dir.glob("audio_*.wav"))
