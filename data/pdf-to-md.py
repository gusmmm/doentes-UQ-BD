import os
from pathlib import Path
from typing import List
from datetime import datetime
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

def log_message(message: str) -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def setup_directories() -> tuple[Path, Path]:
    """Create necessary directories and return source and target paths."""
    log_message("Setting up directories...")
    base_dir = Path(__file__).parent
    pdf_dir = base_dir / "pdf-originals"
    md_dir = base_dir / "md-from-pdf"
    md_dir.mkdir(exist_ok=True)
    log_message(f"Input directory: {pdf_dir}")
    log_message(f"Output directory: {md_dir}")
    return pdf_dir, md_dir

def get_pdf_files(directory: Path) -> List[Path]:
    """Return list of PDF files in directory."""
    files = list(directory.glob("*.pdf"))
    log_message(f"Found {len(files)} PDF files to process")
    return files

def file_exists(pdf_path: Path, output_dir: Path) -> bool:
    """Check if corresponding MD file exists."""
    md_path = output_dir / f"{pdf_path.stem}.md"
    return md_path.exists()

def convert_pdf_to_md(pdf_path: Path, output_dir: Path, current: int, total: int) -> None:
    """Convert single PDF to Markdown, preserving Portuguese characters."""
    try:
        log_message(f"Processing [{current}/{total}]: {pdf_path.name}")
        
        if file_exists(pdf_path, output_dir):
            log_message(f"Skipping {pdf_path.name} - MD file already exists")
            return
        
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        converter = DocumentConverter()
        
        log_message(f"Converting {pdf_path.name}...")
        result = converter.convert(str(pdf_path))
        
        output_path = output_dir / f"{pdf_path.stem}.md"
        markdown_text = result.document.export_to_markdown()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
            
        log_message(f"Successfully saved: {output_path.name}")
        
    except Exception as e:
        log_message(f"ERROR converting {pdf_path.name}: {str(e)}")

def main():
    """Main execution function."""
    log_message("Starting PDF to Markdown conversion")
    pdf_dir, md_dir = setup_directories()
    pdf_files = get_pdf_files(pdf_dir)
    
    if not pdf_files:
        log_message("No PDF files found. Exiting.")
        return
    
    total_files = len(pdf_files)
    converted = 0
    skipped = 0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        if file_exists(pdf_file, md_dir):
            skipped += 1
        else:
            converted += 1
        convert_pdf_to_md(pdf_file, md_dir, idx, total_files)
    
    log_message(f"Conversion complete. Processed {total_files} files:")
    log_message(f"- Converted: {converted}")
    log_message(f"- Skipped: {skipped}")

if __name__ == "__main__":
    main()