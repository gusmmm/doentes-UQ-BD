from enum import Enum
from typing import Dict

class ModelProvider(Enum):
    #OPENAI = "openai/gpt-4o-mini"
    OPENAI = "openai/o3-mini-high"
    DEEPSEEK = "deepseek/deepseek-chat"
    ANTHROPIC = "anthropic/claude-3.5-haiku"
    GOOGLE = "google/gemini-2.0-flash-001"

# Model configuration for each extractor
EXTRACTOR_MODELS: Dict[str, ModelProvider] = {
    "patient": ModelProvider.OPENAI,
    "burn": ModelProvider.OPENAI,
    "medical_history": ModelProvider.OPENAI
}

# OpenRouter API settings
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"