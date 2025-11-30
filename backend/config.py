from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Stream Settings
    stream_url: str = "https://www.livenowfox.com/live"
    segment_duration: int = 60
    
    # Audio Settings
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    
    # Paths
    output_dir: Path = Path("output")
    audio_dir: Path = Path("output/audio")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
