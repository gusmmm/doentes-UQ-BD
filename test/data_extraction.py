from pathlib import Path
import json
import sys

# Add parent directory to Python path so we can import extractors
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from extractors.patient_extractor import PatientDataExtractor
from extractors.burn_extractor import BurnDataExtractor
from extractors.extraction_utils import extract_and_format_data

def main():
    # Test file path
    file_path = project_root / "data" / "md-final" / "2301.md"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return
        
    print(f"\nExtracting data from {file_path}")
    print("-" * 80)
    
    # Extract and format data for MongoDB
    mongo_doc = extract_and_format_data(file_path, project_root)
    
    if mongo_doc:
        print("\nExtracted MongoDB Document:")
        print("-" * 80)
        print(json.dumps(mongo_doc, indent=2, ensure_ascii=False))
        
        # Optionally save to JSON file
        output_file = project_root / "data" / "json" / f"{file_path.stem}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mongo_doc, f, indent=2, ensure_ascii=False)
            
        print(f"\nSaved JSON output to: {output_file}")
    else:
        print("\nFailed to extract data")

if __name__ == "__main__":
    main()
