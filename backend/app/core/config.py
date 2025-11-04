"""
Configuration Management
Loads settings from environment variables
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    weaviate_api_key: Optional[str] = Field(default=None, alias="WEAVIATE_API_KEY")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")

    # Vector Database
    vector_db_type: str = Field(default="chromadb", alias="VECTOR_DB_TYPE")
    chromadb_path: str = Field(default="./vector_db", alias="CHROMADB_PATH")
    chromadb_persist: bool = Field(default=True, alias="CHROMADB_PERSIST")

    # Pinecone
    pinecone_environment: str = Field(default="us-east-1", alias="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="snapmap-embeddings", alias="PINECONE_INDEX_NAME")

    # Weaviate
    weaviate_url: str = Field(default="http://localhost:8080", alias="WEAVIATE_URL")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")

    # AI Inference
    ai_inference_enabled: bool = Field(default=True, alias="AI_INFERENCE_ENABLED")
    ai_inference_provider: str = Field(default="gemini", alias="AI_INFERENCE_PROVIDER")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")

    # Application
    max_file_size_mb: int = Field(default=100, alias="MAX_FILE_SIZE_MB")
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def update_setting(key: str, value: str) -> bool:
    """
    Update a setting value and persist to .env file

    Args:
        key: Setting key (e.g., 'GEMINI_API_KEY')
        value: New value

    Returns:
        bool: True if successful
    """
    try:
        env_path = Path(__file__).parent.parent.parent / ".env"

        # Read existing .env content
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []

        # Update or add the key
        key_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                key_found = True
                break

        if not key_found:
            lines.append(f"{key}={value}\n")

        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(lines)

        # Reload settings
        global _settings
        _settings = Settings()

        return True
    except Exception as e:
        print(f"Error updating setting: {e}")
        return False


def get_vector_db_options():
    """Get available vector database options"""
    return [
        {
            "id": "chromadb",
            "name": "ChromaDB",
            "description": "Local vector database with persistent storage",
            "requires_api_key": False,
            "recommended": True
        },
        {
            "id": "pinecone",
            "name": "Pinecone",
            "description": "Cloud-based vector database (requires API key)",
            "requires_api_key": True,
            "recommended": False
        },
        {
            "id": "weaviate",
            "name": "Weaviate",
            "description": "Open-source vector search engine",
            "requires_api_key": False,
            "recommended": False
        },
        {
            "id": "qdrant",
            "name": "Qdrant",
            "description": "High-performance vector database",
            "requires_api_key": False,
            "recommended": False
        },
        {
            "id": "local",
            "name": "Local (No Vector DB)",
            "description": "Use only fuzzy matching without semantic search",
            "requires_api_key": False,
            "recommended": False
        }
    ]


def get_ai_provider_options():
    """Get available AI inference providers"""
    return [
        {
            "id": "gemini",
            "name": "Google Gemini",
            "description": "Google's advanced AI model",
            "requires_api_key": True,
            "recommended": True
        },
        {
            "id": "openai",
            "name": "OpenAI GPT",
            "description": "OpenAI's GPT models",
            "requires_api_key": True,
            "recommended": False
        },
        {
            "id": "anthropic",
            "name": "Anthropic Claude",
            "description": "Anthropic's Claude AI",
            "requires_api_key": True,
            "recommended": False
        },
        {
            "id": "local",
            "name": "Local (Disabled)",
            "description": "Disable AI-assisted features",
            "requires_api_key": False,
            "recommended": False
        }
    ]
