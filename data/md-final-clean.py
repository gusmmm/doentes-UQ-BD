import os
from pathlib import Path
import re
from typing import List, Set

def load_file_content(file_path: Path) -> List[str]:
    """Read file content and return as list of lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def should_remove_line(line: str) -> bool:
    """Check if line should be removed based on patterns."""
    patterns_to_remove = [
        r'<!-- image -->',
        r'H\. SAO JOAO ALAMEDA',
        r'Tel\. :',
        r'Email:',
        r'Data de Criação',
        r'Data de Bloqueio',
        r'Versão',
        r'Criado por',
        r'Local :',
        r'\\_\\_',  # Continuous underscores
        r'_ _ _ _',     # Spaced underscores
        r'\-\-\-\-\-',  # Continuous dashes
        r'- - - -',     # Spaced dashes
        r'O\(A\) Médico',
        r'PORTO,',
        r'^\s*$',       # Empty lines
        r'código de barras',
    ]
    
    # Additional check for lines containing only dashes or underscores
    if all(c in '-_' for c in line.strip()):
        return True
        
    return any(re.search(pattern, line) for pattern in patterns_to_remove)

def clean_content(lines: List[str]) -> List[str]:
    """Clean and standardize content."""
    seen_lines = set()
    cleaned_lines = []
    
    for line in lines:
        # Strip whitespace
        line = line.strip()
        
        # Skip if line should be removed
        if should_remove_line(line):
            continue
            
        # Skip if empty after cleaning
        if not line:
            continue
            
        # Skip duplicate lines
        if line in seen_lines:
            continue
            
        # Clean section headers
        if line.startswith('##'):
            line = line.replace('##', '').strip()
            
        # Add to cleaned content
        cleaned_lines.append(line)
        seen_lines.add(line)
    
    return cleaned_lines

def process_directory(input_dir: Path, output_dir: Path) -> None:
    """Process all .md files in directory."""
    output_dir.mkdir(exist_ok=True)
    
    for file_path in input_dir.glob('*.md'):
        print(f"Processing {file_path.name}")
        
        # Read and clean content
        content = load_file_content(file_path)
        cleaned_content = clean_content(content)
        
        # Write cleaned content
        output_path = output_dir / file_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_content))
        
        print(f"Saved cleaned file to {output_path}")

def main():
    """Main execution function."""
    base_dir = Path(__file__).parent
    input_dir = base_dir / "md-merged"
    output_dir = base_dir / "md-final"
    
    print("Starting cleanup process...")
    process_directory(input_dir, output_dir)
    print("Cleanup complete!")

if __name__ == "__main__":
    main()