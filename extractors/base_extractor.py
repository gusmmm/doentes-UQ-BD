import os
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import Optional, Type
from pydantic import BaseModel
from settings import EXTRACTOR_MODELS, OPENROUTER_BASE_URL

class BaseExtractor:
    def __init__(self, project_root: Path, extractor_type: str):
        self.project_root = project_root
        
        # Get model from settings
        model_name = EXTRACTOR_MODELS[extractor_type].value
        
        # Initialize OpenRouter API
        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not found")
            
        self.model = OpenAIModel(
            model_name,
            base_url=OPENROUTER_BASE_URL,
            api_key=openrouter_api_key,
        )

    def read_md_file(self, filename: str | Path) -> str | None:
        """Read content from a markdown file."""
        try:
            file_path = Path(filename)
            if not file_path.is_absolute():
                file_path = self.project_root / file_path
                
            print(f"Reading file {file_path}")
            return file_path.read_text(encoding='utf-8')
            
        except FileNotFoundError:
            print(f"File {file_path} not found")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return None
