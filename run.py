#!/usr/bin/env python3
"""
Main runner for the stock tracker
Just runs the app with some basic error checking
"""
import sys
from pathlib import Path

def main():
    """Start the app"""
    print("🇮🇳 Indian Stock Tracker")
    print("=" * 30)
    
    # Add modules to path
    sys.path.append(str(Path(__file__).parent / "modules"))
    
    # Check dependencies
    try:
        from modules.app import check_dependencies, StockTrackerApp
        
        if not check_dependencies():
            print("❌ Missing deps. Run: pip install -r requirements.txt")
            return 1
        
        # Run the application
        app = StockTrackerApp()
        app.run()
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
