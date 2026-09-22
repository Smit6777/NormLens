import shutil
from pathlib import Path
from datetime import datetime
import argparse

def backup_knowledge_base():
    """Backup the data directory containing JSONs and vector index."""
    backend_dir = Path(__file__).parent.parent
    data_dir = backend_dir / "data"
    backup_dir = backend_dir / "backups"
    
    if not data_dir.exists():
        print(f"[ERROR] Data directory not found at {data_dir}")
        return

    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = backup_dir / f"bis_kb_backup_{timestamp}"
    
    print(f"Creating backup of {data_dir}...")
    shutil.make_archive(str(archive_name), 'zip', data_dir)
    print(f"[OK] Backup successfully created at: {archive_name}.zip")

if __name__ == "__main__":
    backup_knowledge_base()
