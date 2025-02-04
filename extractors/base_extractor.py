from pathlib import Path

class BaseExtractor:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def read_md_file(self, filename: str | Path) -> str | None:
        """Read content from a markdown file."""
        try:
            file_path = Path(filename)
            if not file_path.is_absolute():
                file_path = self.project_root / file_path
                
            print(f"Reading file {file_path}")
            return file_path.read_text(encoding='utf-8')
            
        except FileNotFoundError:
            print(f"File {file_path} not found")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return None
