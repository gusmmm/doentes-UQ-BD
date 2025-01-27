import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def get_patient_id(filename: str) -> str:
    """Extract patient ID from filename."""
    return ''.join(filter(str.isdigit, filename))

def get_file_type(filename: str) -> str:
    """Get file type (E, A, O, BIC) from filename."""
    suffix = ''.join(filter(str.isalpha, filename.split('.')[0]))
    return suffix

def read_file_content(file_path: Path) -> str:
    """Read file content and remove empty lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return ''.join(line for line in lines if line.strip())

def group_files_by_patient(source_dir: Path) -> Dict[str, Dict[str, Path]]:
    """Group files by patient ID and type."""
    patient_files = defaultdict(dict)
    for file_path in source_dir.glob('*.md'):
        patient_id = get_patient_id(file_path.name)
        file_type = get_file_type(file_path.name)
        patient_files[patient_id][file_type] = file_path
    return patient_files

def create_merged_content(file_group: Dict[str, Path]) -> str:
    """Create merged content with proper section markers."""
    sections = []
    
    # Order: E -> A -> BIC -> O
    section_types = {
        'E': 'unit admission note',
        'A': 'unit discharge note',
        'BIC': 'death notice information',
        'O': 'death certificate'
    }
    
    for file_type, section_name in section_types.items():
        if file_type in file_group:
            content = read_file_content(file_group[file_type])
            sections.append(f"\n>> {section_name} <<\n{content}\n>> END {section_name} <<\n")
    
    return ''.join(sections)

def merge_patient_files(source_dir: Path, target_dir: Path) -> None:
    """Main function to merge files."""
    print(f"Reading files from {source_dir}")
    target_dir.mkdir(exist_ok=True)
    
    # Group files by patient
    patient_files = group_files_by_patient(source_dir)
    print(f"Found {len(patient_files)} patients to process")
    
    # Process each patient's files
    for patient_id, file_group in patient_files.items():
        output_path = target_dir / f"{patient_id}.md"
        merged_content = create_merged_content(file_group)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        print(f"Created merged file for patient {patient_id}")

def main():
    """Main execution function."""
    base_dir = Path(__file__).parent
    source_dir = base_dir / "md-from-pdf"
    target_dir = base_dir / "md-final"
    
    print("Starting file merge process...")
    merge_patient_files(source_dir, target_dir)
    print("Merge complete!")

if __name__ == "__main__":
    main()