import re
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import Optional
import os
import traceback

from .base_extractor import BaseExtractor

class PatientData(BaseModel):
    id_patient: int = Field(description="Patient ID from filename")
    gender: Optional[str] = Field(default=None)
    date_of_birth: Optional[str] = Field(default=None)  # dd-mm-yyyy
    process_number: Optional[int] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    admission_date: Optional[str] = Field(default=None)  # dd-mm-yyyy
    admission_time: Optional[str] = Field(default=None)
    origin: Optional[str] = Field(default=None)
    discharge_date: Optional[str] = Field(default=None)  # dd-mm-yyyy
    discharge_time: Optional[str] = Field(default=None)
    destination: Optional[str] = Field(default=None)
    
class PatientDataExtractor(BaseExtractor):
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        
        try:
            # Load context files
            patient_context_path = project_root / 'instructions' / 'patient-extraction.md'
            if not patient_context_path.exists():
                raise FileNotFoundError(f"Patient context file not found: {patient_context_path}")
            self.patient_context = patient_context_path.read_text()
            print(f"Loaded patient context from {patient_context_path}")

            pt_glossary_path = project_root / 'instructions' / 'dicionario-PT.md'
            if not pt_glossary_path.exists():
                raise FileNotFoundError(f"Portuguese glossary not found: {pt_glossary_path}")
            self.pt_glossary = pt_glossary_path.read_text()
            print(f"Loaded Portuguese glossary from {pt_glossary_path}")

            # Initialize OpenRouter API
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment variables")
                
            self.model = OpenAIModel(
                #'deepseek/deepseek-chat',
                'anthropic/claude-3.5-haiku',
                #'openai/gpt-4o-mini',  # Using same model as burn extractor for consistency
                base_url='https://openrouter.ai/api/v1',
                api_key=openrouter_api_key,
            )
            print("Initialized OpenRouter API client")
            
            # Initialize extraction agent
            self.agent = Agent(
                model=self.model,
                result_type=PatientData,
                system_prompt=f"""
                Using these instructions and Portuguese medical glossary:
                
                {self.patient_context}
                {self.pt_glossary}
                
                Extract patient information from Portuguese medical text into structured data.
                
                Pay attention to:
                1. Dates must be in dd-mm-yyyy format
                2. Times must be in HH:MM format (24h)
                3. Address should include full street address when available
                4. For missing information, use None
                
                Return a complete PatientData object.
                """,
            )
            print("Initialized extraction agent with context and glossary")
            
        except Exception as e:
            print(f"Error initializing PatientDataExtractor:")
            print(traceback.format_exc())
            raise

    def extract_patient_id(self, filename: str) -> int:
        """Extract numeric ID from filename."""
        try:
            match = re.search(r'(\d+)', filename)
            if not match:
                raise ValueError(f"No numeric ID found in filename: {filename}")
            return int(match.group(1))
        except Exception as e:
            print(f"Error extracting patient ID from {filename}:")
            print(traceback.format_exc())
            raise

    def extract(self, filename: str | Path) -> Optional[PatientData]:
        """Extract patient data from medical report."""
        try:
            print(f"\nExtracting patient data from {filename}")
            
            # Get patient ID from filename
            patient_id = self.extract_patient_id(str(filename))
            print(f"Extracted patient ID: {patient_id}")
            
            # Read markdown content
            md_content = self.read_md_file(filename)
            if not md_content:
                print("No content read from file")
                return None
            print(f"Read {len(md_content)} characters from markdown file")
                
            print("Sending request to extraction agent...")
            result = self.agent.run_sync(md_content)
            
            if not result:
                print("Error: No result returned from agent")
                return None
                
            if not result.data:
                print("Error: No data in result")
                return None
                
            # Validate the extracted data
            print("\nExtracted data:")
            result.data.id_patient = patient_id
            for field, value in result.data.model_dump().items():
                print(f"{field}: {value}")
                
            return result.data
            
        except Exception as e:
            print(f"\nError extracting patient data:")
            print(traceback.format_exc())
            print("\nSuggestion: Check if the markdown content is valid and the extraction agent is properly configured")
            return None
