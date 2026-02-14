"""
Centralized Configuration
ყველა კონფიგურაცია ერთ ადგილას
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """მთავარი კონფიგურაცია"""
    
    # === Project Info ===
    PROJECT_NAME = "საგადასახადო RAG ასისტენტი"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # === Paths ===
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    VECTOR_DB_DIR = DATA_DIR / "vector_db"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = DATA_DIR / "logs"
    CONFIG_DIR = BASE_DIR / "config"
    PROMPTS_DIR = CONFIG_DIR / "prompts"
    
    # === API Keys ===
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # === Claude Settings ===
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    CLAUDE_TEMPERATURE = 0.0
    CLAUDE_MAX_TOKENS = 2000
    
    # === RAG Settings ===
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # === Embeddings ===
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE = "cpu"
    
    # === Vector Database ===
    COLLECTION_NAME = "tax_documents"
    
    # === Cache ===
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1 hour in seconds
    
    # === Logging ===
    LOG_LEVEL = "INFO"
    LOG_FILE = LOGS_DIR / "app.log"
    
    # === UI ===
    UI_TITLE = "საგადასახადო RAG ასისტენტი"
    UI_ICON = "🤖"
    
    @classmethod
    def validate(cls):
        """შეამოწმე და შექმენი საქაღალდეები"""
        # Check API Key
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("❌ ANTHROPIC_API_KEY არ არის დაყენებული .env ფაილში!")
        
        # Create directories
        for directory in [cls.DATA_DIR, cls.DOCUMENTS_DIR, cls.VECTOR_DB_DIR,
                          cls.CACHE_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        print("✅ კონფიგურაცია ვალიდურია")
        return True


# Global settings instance
settings = Settings()