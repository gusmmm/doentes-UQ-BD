import os
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import List, Optional
import traceback

from .base_extractor import BaseExtractor

class Surgery(BaseModel):
    """Surgery information."""
    procedure: str = Field(description="Name of surgical procedure")
    date: Optional[str] = Field(default=None)  # yyyy-mm-dd if known
    details: Optional[str] = Field(default=None)

class MedicalHistory(BaseModel):
    """Patient's previous medical history."""
    diseases: List[str] = Field(
        default_factory=list,
        description="Pre-existing conditions before current episode"
    )
    medications: List[str] = Field(
        default_factory=list,
        description="Medications taken before current episode"
    )
    previous_surgeries: List[Surgery] = Field(
        default_factory=list,
        description="Surgical procedures performed BEFORE current burn episode"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="Known allergies before admission"
    )

   
class MedicalHistoryExtractor(BaseExtractor):
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        
        try:
            # Load context files
            history_context_path = project_root / 'instructions' / 'medical-history-extraction.md'
            if not history_context_path.exists():
                raise FileNotFoundError(f"Medical history context file not found: {history_context_path}")
            self.history_context = history_context_path.read_text()
            
            pt_glossary_path = project_root / 'instructions' / 'dicionario-PT.md'
            if not pt_glossary_path.exists():
                raise FileNotFoundError(f"Portuguese glossary not found: {pt_glossary_path}")
            self.pt_glossary = pt_glossary_path.read_text()

            # Initialize OpenRouter API
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY not found")
            
             # connect to gemini API
            GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")

            self.model = OpenAIModel(
                #'deepseek/deepseek-chat',
                'openai/gpt-4o-mini',
                #'anthropic/claude-3.5-haiku',
                #'google/gemini-2.0-flash-001',
                base_url='https://openrouter.ai/api/v1',
                api_key=openrouter_api_key,
            )
            print("Initialized OpenRouter API client")

            self.agent = Agent(
                model=self.model,
                #'gemini-2.0-flash-001',
                result_type=MedicalHistory,
                system_prompt=f"""
                Using these instructions and Portuguese medical glossary:
                
                {self.history_context}
                {self.pt_glossary}
                
                Extract patient's previous medical history from Portuguese text.
                Focus on information before the current injury:
                1. Pre-existing diseases and conditions
                2. Regular medications taken before injury
                3. Previous surgeries with dates if available
                4. Known allergies
                
                Return MedicalHistory object with all fields.
                Use empty lists for missing information.
                """
            )

        except Exception as e:
            print(f"Error initializing MedicalHistoryExtractor:")
            print(traceback.format_exc())
            raise

    def extract(self, filename: str | Path) -> Optional[MedicalHistory]:
        """Extract medical history from report."""
        try:
            print(f"\nExtracting medical history from {filename}")
            
            md_content = self.read_md_file(filename)
            if not md_content:
                return None
                
            print("Processing medical history...")
            result = self.agent.run_sync(md_content)
            
            if not result or not result.data:
                return None
                
            # Log extracted data
            data = result.data
            print("\nExtracted medical history:")
            print(f"Diseases: {len(data.diseases)}")
            print(f"Medications: {len(data.medications)}")
            print(f"Surgeries: {len(data.previous_surgeries)}")
            print(f"Allergies: {len(data.allergies)}")
            
            return data

        except Exception as e:
            print(f"\nError extracting medical history:")
            print(traceback.format_exc())
            return None