from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import List, Optional
import os
import traceback

from .base_extractor import BaseExtractor

class BurnDepth(str, Enum):
    FIRST_DEGREE = "1st degree"
    SECOND_DEGREE_SUPERFICIAL = "2nd degree superficial"
    SECOND_DEGREE_DEEP = "2nd degree deep"
    THIRD_DEGREE = "3rd degree"
    FOURTH_DEGREE = "4th degree"

class BurnLocation(BaseModel):
    location: str = Field(description="Body part affected")
    degree: BurnDepth = Field(description="Burn depth for this location")
    laterality: Optional[str] = Field(description="Left, right, or bilateral if applicable")
    is_circumferential: Optional[bool] = Field(description="Whether the burn is circumferential")

class FluidAdministration(BaseModel):
    type: str = Field(description="Type of fluid administered")
    volume: str = Field(description="Volume of fluid administered")
    
class Intervention(BaseModel):
    date: str = Field(description="Date of intervention (dd-mm-yyyy)")
    procedure: str = Field(description="Type of procedure")
    details: Optional[str] = Field(description="Additional details about the procedure")

class BurnData(BaseModel):
    injury_date: Optional[str] = Field(default=None)  # dd-mm-yyyy
    injury_time: Optional[str] = Field(default=None)  # HH:MM
    injury_cause: Optional[str] = Field(default=None)
    injury_location: List[str] = Field(default_factory=list)
    burn_degree: List[BurnLocation] = Field(default_factory=list)
    tbsa: Optional[float] = Field(default=None)
    inhalation_injury: bool = Field(default=False)
    pre_hospital_intubation: bool = Field(default=False)
    pre_hospital_fluid: List[FluidAdministration] = Field(default_factory=list)
    pre_hospital_other: Optional[str] = Field(default=None)
    mechanical_ventilation: bool = Field(default=False)
    parkland_formula: Optional[dict] = Field(default=None)
    consultations: List[str] = Field(default_factory=list)
    interventions: List[Intervention] = Field(default_factory=list)
    
class BurnDataExtractor(BaseExtractor):
    def __init__(self, project_root: Path):
        super().__init__(project_root, "burn")
        
        try:
            # Load context files
            burn_context_path = project_root / 'instructions' / 'burns-extraction.md'
            if not burn_context_path.exists():
                raise FileNotFoundError(f"Burns context file not found: {burn_context_path}")
            self.burn_context = burn_context_path.read_text()
            print(f"Loaded burns context from {burn_context_path}")

            pt_glossary_path = project_root / 'instructions' / 'dicionario-PT.md'
            if not pt_glossary_path.exists():
                raise FileNotFoundError(f"Portuguese glossary not found: {pt_glossary_path}")
            self.pt_glossary = pt_glossary_path.read_text()
            print(f"Loaded Portuguese glossary from {pt_glossary_path}")

            # Initialize OpenRouter API
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment variables")
            
             # connect to gemini API
            GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            print("Initialized OpenRouter API client")
            
            # Initialize extraction agent
            self.agent = Agent(
                model=self.model,
                result_type=BurnData,
                system_prompt=f"""
                   Using this burn classification context and Portuguese medical glossary:
                
                BURN CLASSIFICATION:
                {self.burn_context}
                
                PORTUGUESE MEDICAL TERMS:
                {self.pt_glossary}
                
                Extract burn injury information from Portuguese medical notes into structured data.
                Use the glossary to interpret medical terms, abbreviations, and expressions.
                
                Important rules:
                1. Burn Locations:
                - the item location must be a body part (e.g., "face", "arm", "leg") in english as in the instructions. Do not state the laterality in the laterality in this item.
                - the item degree must be a burn depth (e.g., "first-degree", "second-degree-superficial") as in the instructions
                - the item laterality must be "left", "right", or "bilateral" if applicable; null otherwise.
                - the item location must be unique within the list
                - the item degree must be unique within the list, use the highest degree if multiple entries for the same location
                - the item laterality must be null if not applicable
                - For arms/legs: create separate entries for left/right if bilateral
                - Circumferential burns only apply to limbs and torso
                - Use exact depth classifications from BurnDepth enum (first-degree, second-degree-superficial, etc.)
                
                2. Total Body Surface Area:
                - Extract the percentage from ASCQ or ASC value
                - Remove any ~ or % symbols and convert to float
                
                3. Burn Mechanism:
                - Use exactly one mechanism from BurnMechanism enum
                - For explosion/gas incidents, use THERMAL_FLAME
                - Include specific agent (e.g., "gas") in etiologic_agent field
                
                Return data according to the BurnData model structure. For missing information:
                - Use empty list for burn_locations if none found
                - Use 0.0 for total_body_surface_area if not specified
                - Use THERMAL_UNSPECIFIED for mechanism if unclear
                - Use None for etiologic_agent if not mentioned
                Return data according to the BurnData model structure.
                """,
            )
            print("Initialized extraction agent with context and glossary")
            
        except Exception as e:
            print(f"Error initializing BurnDataExtractor:")
            print(traceback.format_exc())
            raise

    def extract(self, filename: str | Path) -> Optional[BurnData]:
        """Extract burn data from medical report."""
        try:
            print(f"\nExtracting burn data from {filename}")
            
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
            print("\nExtracted burn data:")
            data = result.data
            print(f"TBSA: {data.tbsa}%")
            print(f"Burn locations ({len(data.burn_degree)}):")
            for burn in data.burn_degree:
                print(f"- {burn.location}: {burn.degree.value}")
            print(f"Interventions ({len(data.interventions)}):")
            for intervention in data.interventions:
                print(f"- {intervention.date}: {intervention.procedure}")
                
            return data
            
        except Exception as e:
            print(f"\nError extracting burn data:")
            print(traceback.format_exc())
            print("\nSuggestion: Check if the markdown content is valid and the extraction agent is properly configured")
            return None
