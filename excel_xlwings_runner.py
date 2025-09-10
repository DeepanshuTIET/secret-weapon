#!/usr/bin/env python3
"""
Standalone Excel XLWings Live Updates Runner
Ultra-smooth real-time stock price updates directly in Excel using xlwings API
Provides the smoothest possible Excel integration experience
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

try:
    from modules.excel_xlwings_updater import ExcelXlwingsUpdater
    XLWINGS_AVAILABLE = True
except ImportError as e:
    print(f"❌ XLWings not available: {e}")
    print("💡 Install xlwings: pip install xlwings")
    XLWINGS_AVAILABLE = False

class ExcelXlwingsRunner:
    """
    Command-line runner for xlwings Excel live updates
    Provides ultra-smooth real-time Excel integration
    """
    
    def __init__(self):
        self.updater = None
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            print("\n🛑 Shutting down xlwings Excel live updates...")
            if self.updater:
                self.updater.stop_live_updates()
                self.updater.cleanup()
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self, excel_file: str, stocks: list, update_interval: int = 15, visible: bool = False):
        """
        Run xlwings Excel live updates
        
        Arguments:
            excel_file: Path to Excel file
            stocks: List of stock symbols to track
            update_interval: Update interval in seconds (minimum 5)
            visible: Whether Excel should be visible
        """
        try:
            print("📊 Indian Stock Tracker - XLWings Excel Live Updates")
            print("=" * 60)
            print(f"Excel File: {excel_file}")
            print(f"Update Interval: {update_interval} seconds")
            print(f"Excel Visibility: {'Visible' if visible else 'Background'}")
            print(f"Stocks to track: {', '.join(stocks)}")
            print("=" * 60)
            print("🚀 Ultra-smooth real-time updates via xlwings API")
            print("💡 This provides the smoothest possible Excel integration!")
            print("=" * 60)
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Create xlwings Excel live updater
            self.updater = ExcelXlwingsUpdater(
                excel_file, 
                update_interval, 
                visible=visible
            )
            
            # Add status callback
            def status_callback(message):
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] {message}")
            
            self.updater.set_status_callback(status_callback)
            
            # Add stocks
            print("\n📈 Adding stocks to xlwings tracking...")
            added_count = 0
            for stock in stocks:
                if self.updater.add_stock(stock):
                    print(f"  ✓ Added {stock}")
                    added_count += 1
                else:
                    print(f"  ❌ Failed to add {stock}")
            
            if added_count == 0:
                print("❌ No valid stocks to track. Exiting.")
                return 1
            
            print(f"\n🔥 Successfully added {added_count} stocks for xlwings tracking!")
            
            # Start live updates
            print(f"\n🔄 Starting ultra-smooth xlwings live updates...")
            print("💡 Excel will update seamlessly in real-time!")
            
            if visible:
                print("👀 Excel is visible - watch the magic happen!")
            else:
                print("🔄 Excel updating in background - open your file to see live updates!")
            
            print("\n⚡ Press Ctrl+C to stop updates")
            print("=" * 60)
            
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

def check_xlwings_installation():
    """Check if xlwings is properly installed and configured"""
    if not XLWINGS_AVAILABLE:
        return False
    
    try:
        import xlwings as xw
        # Test basic xlwings functionality
        print("✓ XLWings library available")
        return True
    except Exception as e:
        print(f"❌ XLWings test failed: {e}")
        print("💡 Try: pip install xlwings")
        return False

def main():
    """Main entry point for xlwings command-line usage"""
    parser = argparse.ArgumentParser(
        description="XLWings Excel Live Stock Updates - Ultra-smooth real-time Excel integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 XLWings Features:
  • Ultra-smooth real-time Excel updates
  • Direct Excel API integration
  • Minimal file locking
  • Seamless background operation
  • Professional formatting with live changes

Examples:
  # Ultra-smooth updates with popular stocks (background)
  python excel_xlwings_runner.py live_stocks.xlsx --popular
  
  # Visible Excel with custom stocks every 10 seconds
  python excel_xlwings_runner.py my_stocks.xlsx --stocks RELIANCE.NS TCS.NS --interval 10 --visible
  
  # Background operation with faster updates
  python excel_xlwings_runner.py smooth_updates.xlsx --popular --interval 5

💡 XLWings provides the smoothest possible Excel integration!
        """
    )
    
    parser.add_argument('excel_file', 
                       help='Excel file path (will be created if it doesn\'t exist)')
    
    parser.add_argument('--stocks', '-s', 
                       nargs='+', 
                       help='Stock symbols to track (e.g., RELIANCE.NS TCS.NS)')
    
    parser.add_argument('--interval', '-i', 
                       type=int, 
                       default=15, 
                       help='Update interval in seconds (minimum 5, default: 15)')
    
    parser.add_argument('--popular', '-p', 
                       action='store_true',
                       help='Use popular Indian stocks')
    
    parser.add_argument('--visible', '-v', 
                       action='store_true',
                       help='Make Excel visible (default: background mode)')
    
    parser.add_argument('--test', '-t', 
                       action='store_true',
                       help='Test xlwings installation and exit')
    
    args = parser.parse_args()
    
    # Test mode
    if args.test:
        print("🧪 Testing xlwings installation...")
        if check_xlwings_installation():
            print("✅ XLWings is ready for ultra-smooth Excel updates!")
            return 0
        else:
            print("❌ XLWings setup incomplete")
            return 1
    
    # Check xlwings availability
    if not check_xlwings_installation():
        print("\n💡 Installation help:")
        print("  pip install xlwings")
        print("  pip install -r requirements.txt")
        return 1
    
    # Determine stocks to track
    if args.popular:
        # Popular Indian stocks optimized for xlwings
        stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "KOTAKBANK.NS",
            "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS"
        ]
    elif args.stocks:
        stocks = args.stocks
    else:
        # Default selection for optimal xlwings performance
        stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"
        ]
    
    # Validate interval (xlwings can handle faster updates)
    if args.interval < 5:
        print("❌ Update interval must be at least 5 seconds for xlwings")
        return 1
    
    # Performance recommendations
    if args.interval < 10:
        print("⚡ Fast updates enabled - xlwings can handle this smoothly!")
    
    if len(stocks) > 20:
        print("📊 Large portfolio detected - xlwings will handle efficiently!")
    
    # Run the xlwings updater
    runner = ExcelXlwingsRunner()
    return runner.run(args.excel_file, stocks, args.interval, args.visible)

if __name__ == "__main__":
    sys.exit(main())
