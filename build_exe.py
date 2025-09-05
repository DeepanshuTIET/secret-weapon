#!/usr/bin/env python3
"""
Build script to create standalone executable for Indian Stock Tracker
"""
import subprocess
import sys
import shutil
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller"""
    print("🔨 Building Indian Stock Tracker Executable")
    print("=" * 50)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed")
    
    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🗑️ Cleaned previous dist directory")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("🗑️ Cleaned previous build directory")
    
    # PyInstaller command for Indian Stock Tracker
    cmd = [
        "pyinstaller",
        "--onefile",                           # Single executable file
        "--windowed",                          # No console window (GUI app)
        "--name", "IndianStockTracker",        # Executable name
        "--add-data", "modules;modules",       # Include modules directory
        "--hidden-import", "tkinter",          # Ensure tkinter is included
        "--hidden-import", "pandas",           # Ensure pandas is included
        "--hidden-import", "yfinance",         # Ensure yfinance is included
        "--hidden-import", "openpyxl",         # Ensure openpyxl is included
        "--hidden-import", "nsetools",         # Ensure nsetools is included
        "--hidden-import", "pytz",             # Ensure pytz is included
        "--icon", "NONE",                      # No icon (can be added later)
        "--clean",                             # Clean PyInstaller cache
        "main.py"
    ]
    
    print(f"🏗️ Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = dist_dir / "IndianStockTracker.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Create data directory next to executable
            exe_data_dir = dist_dir / "data"
            exe_data_dir.mkdir(exist_ok=True)
            print(f"📁 Created data directory: {exe_data_dir}")
            
            # Copy README to dist
            readme_path = Path("README.md")
            if readme_path.exists():
                shutil.copy2(readme_path, dist_dir / "README.md")
                print("📖 Copied README.md")
            
            print(f"\n🎉 Build successful!")
            print(f"   📦 Executable: {exe_path}")
            print(f"   📁 Ready for distribution: {dist_dir}/")
            
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main build function"""
    print("🇮🇳 Indian Stock Tracker - Build Script")
    print("=" * 60)
    
    if build_executable():
        print("\n✅ Build completed successfully!")
        print("Ready to distribute the Indian Stock Tracker!")
    else:
        print("\n❌ Build failed. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
