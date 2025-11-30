"""
Test transcription service with existing audio files
"""

import asyncio
import logging
from pathlib import Path
from services.transcription_service import TranscriptionService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_transcription():
    """Test transcription on existing audio files"""
    
    print("=" * 80)
    print("🎙️  Testing Transcription Service (OpenAI Whisper + GPT-4)")
    print("=" * 80)
    
    audio_dir = Path("output/audio")
    audio_files = sorted(audio_dir.glob("audio_*.wav"))
    
    if not audio_files:
        print("\n❌ No audio files found in output/audio/")
        print("Run the stream capture first to generate audio files.\n")
        return
    
    print(f"\nFound {len(audio_files)} audio file(s):")
    for f in audio_files:
        size_kb = f.stat().st_size / 1024
        print(f"  📁 {f.name} ({size_kb:.2f} KB)")
    
    print("\n" + "=" * 80)
    print("Starting transcription (this may take a few minutes)...")
    print("=" * 80 + "\n")
    
    service = TranscriptionService()
    
    # Process first file as test
    test_file = audio_files[0]
    await service._process_audio_file(test_file)
    
    print("\n" + "=" * 80)
    print("✓ Transcription Test Complete!")
    print("=" * 80)
    
    # Show results
    if service.latest_transcripts:
        result = service.latest_transcripts[0]
        print(f"\n📄 File: {result['filename']}")
        print(f"⏰ Timestamp: {result['timestamp']}")
        print(f"\n📝 Transcript:")
        print(f"   {result['transcript']}")
        print(f"\n✨ Summary (15 words):")
        print(f"   {result['summary']}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_transcription())
