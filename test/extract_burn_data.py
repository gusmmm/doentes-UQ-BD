from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing import Optional, List
from enum import Enum
import os
from dotenv import load_dotenv
from pathlib import Path
import traceback

# Get project root directory (2 levels up from test folder)
project_root = Path(__file__).parent.parent

# Load environment variables and context
load_dotenv()
with open(project_root / 'instructions' / 'burns-extraction.md', 'r') as f:
    BURN_CONTEXT = f.read()

with open(project_root / 'instructions' / 'dicionario-PT.md', 'r') as f:
    PT_GLOSSARY = f.read()

 # connect to openrouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")
# connect to novita ai API
NOVITA_API_KEY = os.getenv('NOVITA_API_KEY')
if not NOVITA_API_KEY:
    raise ValueError("NOVITA_API_KEY not found in environment variables")



model = OpenAIModel(
    #'openai/gpt-4o-mini',  # This model supports function calling through OpenRouter
    'deepseek/deepseek-chat',
    base_url='https://openrouter.ai/api/v1',
    #base_url='https://api.novita.ai/v3/openai', #novita ai
    api_key=OPENROUTER_API_KEY,
    #api_key=NOVITA_API_KEY, #novita ai
)
# connect to gemini API
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
    model=model,
    #'gemini-2.0-flash-001',
    result_type=BurnData,
    system_prompt=f"""
    Using this burn classification context and Portuguese medical glossary:
    
    BURN CLASSIFICATION:
    {BURN_CONTEXT}
    
    PORTUGUESE MEDICAL TERMS:
    {PT_GLOSSARY}
    
    Extract burn injury information from Portuguese medical notes into structured data.
    Use the glossary to interpret medical terms, abbreviations, and expressions.
    
    Important rules:
    1. Burn Locations:
       - Each location must include body part, burn depth, laterality (if applicable), and whether it's circumferential
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
    """
)

def extract_burn_data(filename):
    """Extract burn data from markdown file"""
    md_content = read_md_file(filename)
    if not md_content:
        print("Error: No content read from file")
        return None

    try:
        print("Sending request to API...")
        result = agent.run_sync(md_content)
        
        if not result:
            print("Error: No result returned from agent")
            return None
            
        if not result.data:
            print("Error: No data in result")
            return None
            
        # Validate the extracted data
        burn_data = result.data
        if not burn_data.burn_locations:
            print("Warning: No burn locations extracted")
        
        print(f"Successfully extracted data with {len(burn_data.burn_locations)} burn locations")
        return burn_data
            
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        if "No endpoints found that support tool use" in str(e):
            print("\nSuggestion: The selected model doesn't support function calling.")
            print("Try using a different model like 'openai/gpt-3.5-turbo' or 'anthropic/claude-2'")
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
