"""
Indian Stock Tracker - Main Entry Point
A real-time stock tracking application for Indian markets (NSE/BSE)
"""
import sys
import logging
from pathlib import Path

# Add modules directory to path
sys.path.append(str(Path(__file__).parent / "modules"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_tracker.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Main entry point for the application"""
    try:
        # Import after path setup
        from modules.app import StockTrackerApp
        
        print("🇮🇳 Indian Stock Tracker v1.0.0")
        print("=" * 50)
        
        # Create and run the application
        app = StockTrackerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        logging.error(f"Application failed to start: {e}")

if __name__ == "__main__":
    main()
