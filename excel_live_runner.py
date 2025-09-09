#!/usr/bin/env python3
"""
Standalone Excel Live Updates Runner
Run this script to update stock prices directly in Excel files without the GUI
"""
import sys
import os
import time
import signal
from pathlib import Path
from datetime import datetime
import argparse

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

from modules.excel_live_updater import ExcelLiveUpdater

class ExcelLiveRunner:
    """
    Command-line runner for Excel live updates
    """
    
    def __init__(self):
        self.updater = None
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            print("\n🛑 Shutting down Excel live updates...")
            if self.updater:
                self.updater.stop_live_updates()
                self.updater.cleanup()
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self, excel_file: str, stocks: list, update_interval: int = 30):
        """
        Run Excel live updates
        
        Arguments:
            excel_file: Path to Excel file
            stocks: List of stock symbols to track
            update_interval: Update interval in seconds
        """
        try:
            print("📊 Indian Stock Tracker - Excel Live Updates")
            print("=" * 50)
            print(f"Excel File: {excel_file}")
            print(f"Update Interval: {update_interval} seconds")
            print(f"Stocks to track: {', '.join(stocks)}")
            print("=" * 50)
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Create Excel live updater
            self.updater = ExcelLiveUpdater(excel_file, update_interval)
            
            # Add status callback
            def status_callback(message):
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] {message}")
            
            self.updater.set_status_callback(status_callback)
            
            # Add stocks
            print("\n📈 Adding stocks to tracking...")
            for stock in stocks:
                if self.updater.add_stock(stock):
                    print(f"  ✓ Added {stock}")
                else:
                    print(f"  ❌ Failed to add {stock}")
            
            if not self.updater.tracked_stocks:
                print("❌ No valid stocks to track. Exiting.")
                return 1
            
            # Start live updates
            print(f"\n🔄 Starting live updates...")
            self.updater.start_live_updates()
            self.running = True
            
            # Keep running until interrupted
            try:
                while self.running and self.updater.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1
        finally:
            if self.updater:
                self.updater.stop_live_updates()
                self.updater.cleanup()

def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Excel Live Stock Updates - Update stock prices directly in Excel files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update popular Indian stocks every 30 seconds
  python excel_live_runner.py live_stocks.xlsx
  
  # Update specific stocks every 60 seconds
  python excel_live_runner.py my_stocks.xlsx --stocks RELIANCE.NS TCS.NS INFY.NS --interval 60
  
  # Create new file with popular stocks
  python excel_live_runner.py new_file.xlsx --popular
        """
    )
    
    parser.add_argument('excel_file', 
                       help='Excel file path (will be created if it doesn\'t exist)')
    
    parser.add_argument('--stocks', '-s', 
                       nargs='+', 
                       help='Stock symbols to track (e.g., RELIANCE.NS TCS.NS)')
    
    parser.add_argument('--interval', '-i', 
                       type=int, 
                       default=30, 
                       help='Update interval in seconds (default: 30)')
    
    parser.add_argument('--popular', '-p', 
                       action='store_true',
                       help='Use popular Indian stocks')
    
    args = parser.parse_args()
    
    # Determine stocks to track
    if args.popular:
        # Popular Indian stocks
        stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "KOTAKBANK.NS",
            "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS"
        ]
    elif args.stocks:
        stocks = args.stocks
    else:
        # Default popular stocks if none specified
        stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"
        ]
    
    # Validate interval
    if args.interval < 10:
        print("❌ Update interval must be at least 10 seconds")
        return 1
    
    # Run the updater
    runner = ExcelLiveRunner()
    return runner.run(args.excel_file, stocks, args.interval)

if __name__ == "__main__":
    sys.exit(main())
