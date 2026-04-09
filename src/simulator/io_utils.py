from datetime import UTC, datetime
from pathlib import Path

def output_directory(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    return path

def generate_output_filepath(output_dir: str | Path, prefix: str) -> Path:
    directory = output_directory(output_dir)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    
    return directory / f"{prefix}_{timestamp}.jsonl"