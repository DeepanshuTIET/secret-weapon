"""
Excel XLWings Live Updater module for ultra-smooth real-time stock price updates
This module uses xlwings for direct Excel API integration providing the smoothest possible updates
"""
import xlwings as xw
import pandas as pd
import threading
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
import queue
from dataclasses import dataclass

from .data_fetcher import IndianStockDataFetcher

logger = logging.getLogger(__name__)

@dataclass
class StockPosition:
    """Track stock position in Excel for efficient updates"""
    symbol: str
    row: int
    last_price: float = 0.0
    last_change: float = 0.0

class ExcelXlwingsUpdater:
    """
    Ultra-smooth Excel live updater using xlwings for direct Excel API integration
    Provides seamless real-time updates with minimal Excel file locks
    """
    
    def __init__(self, excel_file_path: str, update_interval_seconds: int = 15, visible: bool = False):
        """
        Initialize the xlwings Excel live updater
        
        Arguments:
            excel_file_path: Path to the Excel file to update
            update_interval_seconds: How often to update prices (in seconds, minimum 5)
            visible: Whether Excel should be visible (False for background updates)
        """
        self.excel_file_path = Path(excel_file_path)
        self.update_interval = max(5, update_interval_seconds)  # Minimum 5 seconds for xlwings
        self.visible = visible
        self.data_fetcher = IndianStockDataFetcher()
        
        # Threading control
        self.is_running = False
        self.update_thread = None
        self.stop_event = threading.Event()
        
        # Stock tracking with positions
        self.tracked_stocks = []
        self.stock_positions: Dict[str, StockPosition] = {}
        self.last_update_time = None
        
        # XLWings objects
        self.app = None
        self.workbook = None
        self.worksheet = None
        
        # Status callback for GUI updates
        self.status_callback = None
        
        # Performance optimization
        self.batch_update_queue = queue.Queue()
        self.update_batch_size = 10  # Process updates in batches
        
        # Column mapping for efficient updates
        self.columns = {
            'symbol': 1, 'name': 2, 'current_price': 3, 'previous_close': 4,
            'change': 5, 'change_percent': 6, 'volume': 7, 'market_cap': 8,
            'pe_ratio': 9, 'high_52w': 10, 'low_52w': 11, 'timestamp': 12, 'source': 13
        }
        
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback function for status updates"""
        self.status_callback = callback
        
    def _update_status(self, message: str):
        """Update status via callback or log"""
        if self.status_callback:
            self.status_callback(message)
        else:
            logger.info(message)
    
    def _initialize_excel_connection(self):
        """Initialize xlwings connection to Excel"""
        try:
            # Start Excel application
            self.app = xw.App(visible=self.visible, add_book=False)
            self.app.display_alerts = False  # Disable alerts for smoother operation
            self.app.screen_updating = False  # Disable screen updates for better performance
            
            # Open or create workbook
            if self.excel_file_path.exists():
                self.workbook = self.app.books.open(str(self.excel_file_path))
                self._update_status(f"Opened existing Excel file: {self.excel_file_path}")
            else:
                self.workbook = self.app.books.add()
                self.workbook.save(str(self.excel_file_path))
                self._update_status(f"Created new Excel file: {self.excel_file_path}")
            
            # Get or create the live data sheet
            sheet_name = "Live Stock Data"
            try:
                self.worksheet = self.workbook.sheets[sheet_name]
                self._load_existing_stocks()
            except KeyError:
                self.worksheet = self.workbook.sheets.add(sheet_name)
                self._setup_headers()
            
            # Enable screen updating after initial setup
            self.app.screen_updating = True
            
            self._update_status("XLWings Excel connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Excel connection: {str(e)}")
            self._update_status(f"Failed to connect to Excel: {str(e)}")
            self._cleanup_excel_connection()
            return False
    
    def _setup_headers(self):
        """Setup column headers with professional formatting"""
        headers = [
            "Symbol", "Company Name", "Current Price (₹)", "Previous Close (₹)", 
            "Change (₹)", "Change %", "Volume", "Market Cap", "P/E Ratio", 
            "52W High (₹)", "52W Low (₹)", "Last Updated", "Source"
        ]
        
        try:
            # Write headers in one operation for efficiency
            header_range = self.worksheet.range(f"A1:{chr(64 + len(headers))}1")
            header_range.value = headers
            
            # Apply formatting
            header_range.color = (31, 78, 121)  # Dark blue background
            header_range.font.bold = True
            header_range.font.color = (255, 255, 255)  # White text
            header_range.font.size = 11
            
            # Set column widths
            column_widths = [15, 35, 15, 15, 12, 10, 15, 15, 10, 15, 15, 20, 15]
            for i, width in enumerate(column_widths, 1):
                self.worksheet.range(f"{chr(64 + i)}:{chr(64 + i)}").column_width = width
            
            self._update_status("Excel headers configured successfully")
            
        except Exception as e:
            logger.error(f"Error setting up headers: {str(e)}")
    
    def _load_existing_stocks(self):
        """Load existing stocks from the Excel file"""
        try:
            self.tracked_stocks = []
            self.stock_positions = {}
            
            # Find the last row with data
            last_row = self.worksheet.range('A1').end('down').row if self.worksheet.range('A1').value else 1
            
            if last_row > 1:  # Has data beyond headers
                # Get all symbols at once for efficiency
                symbols_range = self.worksheet.range(f'A2:A{last_row}')
                symbols = symbols_range.value
                
                # Handle single vs multiple values
                if not isinstance(symbols, list):
                    symbols = [symbols]
                
                for row, symbol in enumerate(symbols, 2):
                    if symbol and str(symbol).strip():
                        clean_symbol = str(symbol).strip().upper()
                        self.tracked_stocks.append(clean_symbol)
                        
                        # Get current price for position tracking
                        current_price = self.worksheet.range(f'C{row}').value or 0.0
                        current_change = self.worksheet.range(f'E{row}').value or 0.0
                        
                        self.stock_positions[clean_symbol] = StockPosition(
                            symbol=clean_symbol,
                            row=row,
                            last_price=float(current_price) if current_price else 0.0,
                            last_change=float(current_change) if current_change else 0.0
                        )
            
            self._update_status(f"Loaded {len(self.tracked_stocks)} existing stocks from Excel")
            
        except Exception as e:
            logger.error(f"Error loading existing stocks: {str(e)}")
    
    def add_stock(self, symbol: str) -> bool:
        """
        Add a stock to live tracking with xlwings optimization
        
        Arguments:
            symbol: Stock symbol to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symbol = symbol.upper().strip()
            
            # Auto-add .NS if not present
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol += '.NS'
            
            if symbol in self.tracked_stocks:
                self._update_status(f"Stock {symbol} already being tracked")
                return False
            
            # Validate symbol first
            self._update_status(f"Validating stock symbol {symbol}...")
            stock_data = self.data_fetcher.get_stock_info(symbol)
            
            if not stock_data:
                self._update_status(f"Invalid stock symbol: {symbol}")
                return False
            
            # Add to tracking list
            self.tracked_stocks.append(symbol)
            
            # Find next available row
            next_row = len(self.stock_positions) + 2  # +2 for header row
            
            # Create position tracking
            self.stock_positions[symbol] = StockPosition(
                symbol=symbol,
                row=next_row,
                last_price=stock_data.get('current_price', 0.0),
                last_change=stock_data.get('change', 0.0)
            )
            
            # Add initial data to Excel
            self._update_stock_row_xlwings(symbol, stock_data)
            
            # Save workbook
            if self.workbook:
                self.workbook.save()
            
            self._update_status(f"Added {symbol} to live tracking")
            return True
            
        except Exception as e:
            logger.error(f"Error adding stock {symbol}: {str(e)}")
            self._update_status(f"Error adding stock: {str(e)}")
            return False
    
    def remove_stock(self, symbol: str) -> bool:
        """
        Remove a stock from live tracking
        
        Arguments:
            symbol: Stock symbol to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symbol = symbol.upper().strip()
            
            if symbol not in self.tracked_stocks:
                return False
            
            # Remove from tracking
            self.tracked_stocks.remove(symbol)
            position = self.stock_positions.pop(symbol, None)
            
            if position and self.worksheet:
                # Delete the row
                self.worksheet.range(f'{position.row}:{position.row}').delete()
                
                # Update positions for remaining stocks
                for stock, pos in self.stock_positions.items():
                    if pos.row > position.row:
                        pos.row -= 1
                
                # Save workbook
                if self.workbook:
                    self.workbook.save()
            
            self._update_status(f"Removed {symbol} from live tracking")
            return True
            
        except Exception as e:
            logger.error(f"Error removing stock {symbol}: {str(e)}")
            return False
    
    def _update_stock_row_xlwings(self, symbol: str, stock_data: Dict):
        """Update a single stock row using xlwings with optimized performance"""
        try:
            if symbol not in self.stock_positions or not self.worksheet:
                return
            
            position = self.stock_positions[symbol]
            row = position.row
            
            # Check if price actually changed to avoid unnecessary updates
            current_price = stock_data.get('current_price', 0.0)
            current_change = stock_data.get('change', 0.0)
            
            # Prepare values
            values = [
                symbol,
                stock_data.get('name', symbol),
                current_price,
                stock_data.get('previous_close', 0),
                current_change,
                stock_data.get('change_percent', 0) / 100,  # Convert to decimal for Excel percentage
                stock_data.get('volume', 0),
                stock_data.get('market_cap', ''),
                stock_data.get('pe_ratio', ''),
                stock_data.get('fifty_two_week_high', 0),
                stock_data.get('fifty_two_week_low', 0),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                stock_data.get('source', 'Unknown')
            ]
            
            # Update entire row at once for efficiency
            range_address = f"A{row}:{chr(64 + len(values))}{row}"
            self.worksheet.range(range_address).value = values
            
            # Apply conditional formatting for price changes
            if current_change != 0:
                change_cell = self.worksheet.range(f"E{row}")
                percent_cell = self.worksheet.range(f"F{row}")
                
                if current_change > 0:
                    # Green for gains
                    change_cell.color = (226, 239, 218)
                    percent_cell.color = (226, 239, 218)
                else:
                    # Light red for losses
                    change_cell.color = (252, 228, 214)
                    percent_cell.color = (252, 228, 214)
            
            # Update position tracking
            position.last_price = current_price
            position.last_change = current_change
            
        except Exception as e:
            logger.error(f"Error updating row for {symbol}: {str(e)}")
    
    def start_live_updates(self):
        """Start the xlwings live update process"""
        if self.is_running:
            self._update_status("Live updates already running")
            return
        
        if not self.tracked_stocks:
            self._update_status("No stocks to track - add stocks first")
            return
        
        # Initialize Excel connection
        if not self._initialize_excel_connection():
            self._update_status("Failed to establish Excel connection")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        def update_loop():
            self._update_status(f"Started xlwings live Excel updates (every {self.update_interval}s)")
            
            while not self.stop_event.is_set():
                try:
                    # Disable screen updating for batch updates
                    if self.app:
                        self.app.screen_updating = False
                    
                    # Update all tracked stocks
                    self._update_all_stocks_xlwings()
                    
                    # Re-enable screen updating
                    if self.app:
                        self.app.screen_updating = True
                    
                    # Wait for next update or stop signal
                    if self.stop_event.wait(self.update_interval):
                        break
                        
                except Exception as e:
                    logger.error(f"Error in xlwings update loop: {str(e)}")
                    self._update_status(f"Update error: {str(e)}")
                    time.sleep(5)  # Wait before retrying
            
            self.is_running = False
            self._cleanup_excel_connection()
            self._update_status("XLWings live Excel updates stopped")
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def stop_live_updates(self):
        """Stop the xlwings live update process"""
        if not self.is_running:
            return
        
        self.stop_event.set()
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=3)
        
        self.is_running = False
        self._cleanup_excel_connection()
        self._update_status("Stopped xlwings live Excel updates")
    
    def _update_all_stocks_xlwings(self):
        """Update all tracked stocks using xlwings with batch optimization"""
        try:
            if not self.tracked_stocks or not self.worksheet:
                return
            
            self._update_status(f"Updating {len(self.tracked_stocks)} stocks via xlwings...")
            
            # Fetch data for all stocks using batch request
            stock_data_df = self.data_fetcher.get_multiple_stocks_batch(
                self.tracked_stocks, 
                force_refresh=True
            )
            
            if stock_data_df.empty:
                self._update_status("No data received for stocks")
                return
            
            # Update each stock in Excel
            updated_count = 0
            for _, row in stock_data_df.iterrows():
                symbol = row.get('symbol')
                if symbol in self.stock_positions:
                    self._update_stock_row_xlwings(symbol, row.to_dict())
                    updated_count += 1
            
            # Save the workbook (xlwings handles this efficiently)
            if self.workbook:
                self.workbook.save()
            
            self.last_update_time = datetime.now()
            self._update_status(f"Updated {updated_count} stocks via xlwings at {self.last_update_time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error updating all stocks via xlwings: {str(e)}")
            self._update_status(f"XLWings update failed: {str(e)}")
    
    def _cleanup_excel_connection(self):
        """Clean up xlwings Excel connection"""
        try:
            if self.workbook:
                self.workbook.save()
                self.workbook.close()
                self.workbook = None
            
            if self.app:
                self.app.quit()
                self.app = None
            
            self.worksheet = None
            
        except Exception as e:
            logger.error(f"Error cleaning up Excel connection: {str(e)}")
    
    def get_status(self) -> Dict:
        """Get current status of the xlwings live updater"""
        return {
            'is_running': self.is_running,
            'tracked_stocks_count': len(self.tracked_stocks),
            'tracked_stocks': self.tracked_stocks.copy(),
            'excel_file': str(self.excel_file_path),
            'update_interval': self.update_interval,
            'last_update': self.last_update_time.isoformat() if self.last_update_time else None,
            'excel_visible': self.visible,
            'connection_type': 'xlwings'
        }
    
    def set_update_interval(self, interval_seconds: int):
        """Change the update interval"""
        self.update_interval = max(5, interval_seconds)  # Minimum 5 seconds for xlwings
        self._update_status(f"Update interval changed to {self.update_interval} seconds")
    
    def manual_update(self):
        """Trigger a manual update of all stocks"""
        if self.is_running:
            # Don't interfere with automatic updates
            self._update_status("Manual update skipped - automatic updates running")
            return
        
        try:
            if not self._initialize_excel_connection():
                self._update_status("Failed to establish Excel connection for manual update")
                return
            
            self._update_all_stocks_xlwings()
            self._cleanup_excel_connection()
            
        except Exception as e:
            self._update_status(f"Manual update failed: {str(e)}")
    
    def toggle_excel_visibility(self):
        """Toggle Excel application visibility"""
        if self.app:
            self.visible = not self.visible
            self.app.visible = self.visible
            self._update_status(f"Excel visibility: {'On' if self.visible else 'Off'}")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_live_updates()
        self._cleanup_excel_connection()
