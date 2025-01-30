import re
from pydantic import BaseModel, Field, validator, model_validator
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

 # connect to openrouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")


model = OpenAIModel(
    'deepseek/deepseek-chat',
    #'deepseek/deepseek-r1-distill-llama-70b',
    #'openai/gpt-4o-mini',  # This model supports function calling through OpenRouter
    #'anthropic/claude-3.5-haiku-20241022:beta',
    base_url='https://openrouter.ai/api/v1',
    api_key=OPENROUTER_API_KEY,
)
# connect to gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# add this glossary to the agent
with open(project_root / 'instructions' / 'dicionario-PT.md', 'r') as f:
    PT_GLOSSARY = f.read()

# Load extraction instructions
with open(project_root / 'instructions' / 'patient-extraction.md', 'r') as f:
    PATIENT_CONTEXT = f.read()

class PatientData(BaseModel):
    id_patient: int = Field(description="Patient ID from filename")
    gender: str | None = Field(default=None)
    date_of_birth: str | None = Field(default=None)  # dd-mm-yyyy
    process_number: int | None = Field(default=None)
    full_name: str | None = Field(default=None)
    location: str | None = Field(default=None)
    date_of_admission_UQ: str | None = Field(default=None) # dd-mm-yyyy
    origin: str | None = Field(default=None)
    date_of_discharge: str | None = Field(default=None) # dd-mm-yyyy
    destination: str | None = Field(default=None)
  
# Define the tools/functions first
def extract_patient_id(filename: str) -> int:
    """Extract numeric ID from filename."""
    match = re.search(r'(\d+)', filename)
    if not match:
        raise ValueError(f"No numeric ID found in filename: {filename}")
    return int(match.group(1))

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

# Initialize agent with tools instead of functions
agent = Agent(
    model=model,
    #'gemini-1.5-pro',
    result_type=PatientData,
    system_prompt=f"""
    Using these instructions and Portuguese medical glossary:
    
    {PATIENT_CONTEXT}
    {PT_GLOSSARY}
    
    Extract the following information from the Portuguese text:
    - The patient's gender (M/F).
    - Date of birth of the patient in format dd-mm-yyyy.
    - Process number.
    - Full name of the patient.
    - Location is where the patient lives, the address. Just return the city or region.
    - Date of admission in the burns unit (UQ). In format dd-mm-yyyy.
    - Origin of the patient, where the patient was transferred from - before being transfered to the burns unit.
    - Date of discharge from the burns unit. In format dd-mm-yyyy.
    - Destination of the patient, where the patient was transferred to - after being discharged from the burns unit.
   
    Return a complete PatientData object.
    """
)

def extract_data(filename: str) -> Optional[PatientData]:
    """Extract patient data from medical report."""
    try:
        patient_id = int(re.search(r'(\d+)', filename).group(1))
        md_content = read_md_file(filename)
        if not md_content:
            return None
        print("Sending request to API...")
        result = agent.run_sync(md_content)
        if not result:
            return None
        result.data.id_patient = patient_id
        return result.data
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    file_path = project_root / "data" / "md-final" / "2301.md"
    result = extract_data(str(file_path))
    if result:
        print(result.model_dump_json(indent=2))
