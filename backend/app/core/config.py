from pydantic_settings import BaseSettings
from typing import List, Optional
from urllib.parse import quote_plus
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "Inventory")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        engine = self.DB_ENGINE.lower()
        password = quote_plus(self.DB_PASSWORD or "")
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if engine == "mysql":
            return f"mysql+pymysql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        if engine in ("postgres", "postgresql"):
            return f"postgresql+psycopg2://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # Fallback to sqlite for local/simple development
        return "sqlite:///inventory.db"

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:4200", "http://localhost:3000"]
    
    # ML/YOLO
    YOLO_MODEL_PATH: str = os.path.join("..", "assets", "models", "yolov8n-seg.pt")
    YOLO_CONFIDENCE_THRESHOLD: float = 0.05
    MAX_IMAGE_SIZE: int = 1920
    
    # OCR
    PYTESSERACT_PATH: str = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

    # AI text suggestion
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # File Upload
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "images")
    MAX_UPLOAD_SIZE: int = 50_000_000  # 50MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
