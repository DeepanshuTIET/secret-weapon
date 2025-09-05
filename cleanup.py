#!/usr/bin/env python3
"""
Cleanup script for Indian Stock Tracker
Removes temporary files, logs, and cached data
"""
import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up temporary files and directories"""
    print("🧹 Cleaning up Indian Stock Tracker project...")
    
    # Directories to clean
    cleanup_dirs = [
        "__pycache__",
        "modules/__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "*.egg-info"
    ]
    
    # Files to clean
    cleanup_files = [
        "*.pyc",
        "*.pyo", 
        "*.log",
        "*.tmp",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    base_path = Path(__file__).parent
    
    # Clean directories
    for dir_pattern in cleanup_dirs:
        for dir_path in base_path.glob(dir_pattern):
            if dir_path.is_dir():
                print(f"🗑️  Removing directory: {dir_path}")
                shutil.rmtree(dir_path, ignore_errors=True)
    
    # Clean files
    for file_pattern in cleanup_files:
        for file_path in base_path.rglob(file_pattern):
            if file_path.is_file():
                print(f"🗑️  Removing file: {file_path}")
                file_path.unlink(missing_ok=True)
    
    # Clean data directory (ask user)
    data_dir = base_path / "data"
    if data_dir.exists() and any(data_dir.iterdir()):
        response = input("🗂️  Clean data directory (Excel files)? (y/N): ")
        if response.lower() == 'y':
            for file_path in data_dir.glob("*.xlsx"):
                print(f"🗑️  Removing Excel file: {file_path}")
                file_path.unlink(missing_ok=True)
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    cleanup_project()
