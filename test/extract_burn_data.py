from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import Optional, List
from enum import Enum
import os
from dotenv import load_dotenv
from pathlib import Path

# Get project root directory (1 level up from test folder)
project_root = Path(__file__).parent.parent

# Load environment variables and context
load_dotenv()
with open(project_root / 'instructions' / 'burns-extraction.md', 'r') as f:
    BURN_CONTEXT = f.read()

""" # connect to openrouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")


model = OpenAIModel(
    'meta-llama/llama-3.3-70b-instruct',
    #'google/gemini-flash-1.5-8b',   # or any other OpenRouter model
    base_url='https://openrouter.ai/api/v1',
    api_key=OPENROUTER_API_KEY,
) """

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

class BurnDepth(str, Enum):
    FIRST_DEGREE = "first-degree"
    SECOND_DEGREE_SUPERFICIAL = "second-degree-superficial"
    SECOND_DEGREE_DEEP = "second-degree-deep"
    THIRD_DEGREE = "third-degree"
    FOURTH_DEGREE = "fourth-degree"

class BurnMechanism(str, Enum):
    THERMAL_FLAME = "thermal-flame"
    THERMAL_SCALD = "thermal-scald"
    THERMAL_CONTACT = "thermal-contact"
    THERMAL_UNSPECIFIED = "thermal-unspecified"
    ELECTRICAL_HIGH = "electrical-high"
    ELECTRICAL_LOW = "electrical-low"
    ELECTRICAL_UNSPECIFIED = "electrical-unspecified"
    CHEMICAL = "chemical"
    RADIATION = "radiation"
    INHALATION = "inhalation"

class BurnLocation(BaseModel):
    location: str = Field(description="Body part affected")
    depth: BurnDepth = Field(description="Burn depth for this location")
    laterality: Optional[str] = Field(description="Laterality of the burn")
    is_circumferential: bool = Field(description="Whether the burn is circumferential")

class BurnData(BaseModel):
    burn_locations: List[BurnLocation] = Field(
        description="List of burn locations with their depths",
        default_factory=list
    ) 
    total_body_surface_area: float = Field(description="Total body surface area affected (%)")
    mechanism: BurnMechanism = Field(description="Mechanism of injury")
    etiologic_agent: Optional[str] = Field(
        description="Specific agent causing the burn",
        default=None
    )
   

def read_md_file(filename):
    """Read content from a markdown file in the clean folder"""
    #file_path = os.path.join('markdown_clean', filename)
    file_path = filename
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            print(f"Reading file {file_path}")
            return file.read()
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None

agent = Agent(
    #model=model,
    'gemini-2.0-flash-exp',
    result_type=BurnData,
    system_prompt=f"""
    Using this burn classification context:
    
    {BURN_CONTEXT}
    
    Extract burn injury information from Portuguese medical notes into structured data.
    Each burn location should include both the body part,its burn depth and whether it is circumferential.
    Return a separate burn location for each limb structure mentioned if there is laterality. If it is described as bilateral, return two locations.
    Return data according to the BurnData model structure.
    If information is not found, use empty lists or default values.
    """
)

def extract_burn_data(filename):
    """Extract burn data from markdown file"""
    md_content = read_md_file(filename)
    if md_content:
        try:
            result = agent.run_sync(md_content)
            return result.data if result else None
        except Exception as e:
            print(f"Extraction error: {str(e)}")
            return None
    return None

if __name__ == "__main__":
    
    # Construct path to test file
    file_path = project_root / "data" / "md-final" / "2301.md"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        exit(1)
    else:
        print(f"Extracting burn data from {file_path}")
        
    result = extract_burn_data(str(file_path))
    if result:
        print(result.model_dump_json(indent=2))