"""
GUI for the stock tracker app
Built with Tkinter - not the prettiest but it works!
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Optional, Dict
import webbrowser

from .data_fetcher import IndianStockDataFetcher, format_currency, format_percentage, format_large_number
from .excel_handler import IndianStockExcelHandler
from .excel_live_updater import ExcelLiveUpdater
from .config import GUI_CONFIG, REFRESH_INTERVALS, DEFAULT_STOCKS

# Try to import xlwings updater
try:
    from .excel_xlwings_updater import ExcelXlwingsUpdater
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    ExcelXlwingsUpdater = None

logger = logging.getLogger(__name__)

class IndianStockTrackerGUI:
    """
    Modern and professional GUI for Indian Stock Tracker
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI
        Arguments:
            root: Tkinter root window
        """
        self.root = root
        self.data_fetcher = IndianStockDataFetcher()
        self.excel_handler = IndianStockExcelHandler(Path("data"))
        
        # GUI state variables
        self.is_auto_refresh = tk.BooleanVar()
        self.refresh_interval = tk.StringVar(value="5 minutes")
        self.selected_stocks = []
        self.current_data = None
        self.refresh_thread = None
        self.stop_refresh = threading.Event()
        
        # Excel live update variables
        self.is_excel_live_update = tk.BooleanVar()
        self.excel_live_updater = None
        self.excel_file_path = tk.StringVar()
        self.excel_update_interval = tk.StringVar(value="30 seconds")
        
        # XLWings specific variables
        self.use_xlwings = tk.BooleanVar(value=False)
        self.xlwings_visible = tk.BooleanVar(value=False)
        self.excel_xlwings_updater = None
        
        # Initialize GUI
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        
        # Load default Indian stocks
        self._load_default_stocks()
        
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title(GUI_CONFIG["window_title"])
        self.root.geometry(GUI_CONFIG["window_size"])
        self.root.minsize(*GUI_CONFIG["min_size"])
        self.root.configure(bg=GUI_CONFIG["theme"]["bg_color"])
        
        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Center window on screen
        self.root.eval('tk::PlaceWindow . center')
    
    def _create_widgets(self):
        """Create and arrange all GUI widgets"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Create header
        self._create_header(main_frame)
        
        # Create control panel
        self._create_control_panel(main_frame)
        
        # Create stock display
        self._create_stock_display(main_frame)
        
        # Create status bar
        self._create_status_bar(main_frame)
        
    def _create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🇮🇳 Indian Stock Tracker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Market status
        self.market_status_var = tk.StringVar()
        self.market_status_label = ttk.Label(header_frame, textvariable=self.market_status_var,
                                            font=("Arial", 10))
        self.market_status_label.grid(row=0, column=1, sticky="e")
        
        # Update market status
        self._update_market_status()
    
    def _create_control_panel(self, parent):
        """Create control panel for stock management"""
        control_frame = ttk.LabelFrame(parent, text="Stock Management", padding="10")
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        control_frame.columnconfigure(1, weight=1)
        
        # Stock input section
        input_frame = ttk.Frame(control_frame)
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Add Indian Stock:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.symbol_entry = ttk.Entry(input_frame, font=("Arial", 10))
        self.symbol_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        add_button = ttk.Button(input_frame, text="Add Stock", command=self._add_stock)
        add_button.grid(row=0, column=2, padx=(0, 5))
        
        popular_button = ttk.Button(input_frame, text="Load Popular", command=self._load_popular_stocks)
        popular_button.grid(row=0, column=3)
        
        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(action_frame, text="🔄 Refresh", command=self._refresh_data).pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="💾 Save Excel", command=self._save_to_excel).pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="🗑️ Remove", command=self._remove_stock).pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="📁 Data Folder", command=self._open_data_folder).pack(side="left", padx=(0, 15))
        
        # Auto-refresh controls
        auto_frame = ttk.Frame(action_frame)
        auto_frame.pack(side="right")
        
        ttk.Checkbutton(auto_frame, text="✓ Auto Refresh", variable=self.is_auto_refresh,
                       command=self._toggle_auto_refresh).pack(side="left", padx=(0, 5))
        
        refresh_combo = ttk.Combobox(auto_frame, textvariable=self.refresh_interval, 
                                   values=list(REFRESH_INTERVALS.keys()),
                                   width=12, state="readonly")
        refresh_combo.pack(side="left")
        
        # Excel Live Update Section
        excel_frame = ttk.LabelFrame(control_frame, text="📊 Live Excel Updates", padding="10")
        excel_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        excel_frame.columnconfigure(1, weight=1)
        
        # Excel file selection
        file_frame = ttk.Frame(excel_frame)
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Excel File:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.excel_file_entry = ttk.Entry(file_frame, textvariable=self.excel_file_path, font=("Arial", 9))
        self.excel_file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self._browse_excel_file).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(file_frame, text="New", command=self._create_new_excel_file).grid(row=0, column=3)
        
        # Excel live update controls
        excel_controls_frame = ttk.Frame(excel_frame)
        excel_controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Checkbutton(excel_controls_frame, text="🔄 Live Excel Updates", 
                       variable=self.is_excel_live_update,
                       command=self._toggle_excel_live_updates).pack(side="left", padx=(0, 10))
        
        ttk.Label(excel_controls_frame, text="Update Every:").pack(side="left", padx=(0, 5))
        excel_interval_combo = ttk.Combobox(excel_controls_frame, textvariable=self.excel_update_interval,
                                          values=["5 seconds", "10 seconds", "30 seconds", "1 minute", "2 minutes", "5 minutes"],
                                          width=12, state="readonly")
        excel_interval_combo.pack(side="left", padx=(0, 10))
        
        ttk.Button(excel_controls_frame, text="📋 Manage Stocks", command=self._manage_excel_stocks).pack(side="left", padx=(0, 5))
        ttk.Button(excel_controls_frame, text="🔄 Update Now", command=self._manual_excel_update).pack(side="left")
        
        # XLWings options frame
        xlwings_frame = ttk.Frame(excel_frame)
        xlwings_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # XLWings option
        xlwings_enabled = XLWINGS_AVAILABLE
        xlwings_checkbutton = ttk.Checkbutton(xlwings_frame, 
                                            text=f"⚡ Use XLWings (Ultra-Smooth)" + ("" if xlwings_enabled else " - Not Available"),
                                            variable=self.use_xlwings,
                                            command=self._on_xlwings_toggle,
                                            state="normal" if xlwings_enabled else "disabled")
        xlwings_checkbutton.pack(side="left", padx=(0, 15))
        
        # XLWings visibility option
        self.xlwings_visible_checkbutton = ttk.Checkbutton(xlwings_frame, 
                                                         text="👀 Show Excel",
                                                         variable=self.xlwings_visible,
                                                         state="disabled" if not xlwings_enabled else "normal")
        self.xlwings_visible_checkbutton.pack(side="left", padx=(0, 10))
        
        # Info label for XLWings
        if xlwings_enabled:
            info_text = "💡 XLWings provides ultra-smooth real-time Excel updates"
        else:
            info_text = "💡 Install xlwings for ultra-smooth Excel updates: pip install xlwings"
        
        self.xlwings_info_label = ttk.Label(xlwings_frame, text=info_text, 
                                          font=("Arial", 8), foreground="gray")
        self.xlwings_info_label.pack(side="left")
        
    def _create_stock_display(self, parent):
        """Create the main stock data display"""
        
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Define columns for Indian stocks
        columns = ("Symbol", "Company Name", "Price (₹)", "Change (₹)", "Change %", 
                  "Volume", "Market Cap", "P/E", "52W High", "52W Low", "Source")
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure column headings and widths for Indian data
        column_widths = {
            "Symbol": 120,
            "Company Name": 250,
            "Price (₹)": 100,
            "Change (₹)": 100,
            "Change %": 90,
            "Volume": 120,
            "Market Cap": 120,
            "P/E": 70,
            "52W High": 100,
            "52W Low": 100,
            "Source": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)
    
    def _create_status_bar(self, parent):
        """Create status bar at the bottom"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Add Indian stocks to start tracking")
        
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                relief="sunken", padding="5")
        status_label.grid(row=0, column=0, sticky="ew")
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.symbol_entry.bind('<Return>', lambda e: self._add_stock())
        self.tree.bind('<Double-1>', self._on_stock_double_click)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _load_default_stocks(self):
        """Load default Indian stocks"""
        self.selected_stocks = DEFAULT_STOCKS.copy()
        self._update_status(f"Loaded {len(self.selected_stocks)} popular Indian stocks")
        self._refresh_data()
    
    def _add_stock(self):
        """Add a new Indian stock symbol"""
        symbol = self.symbol_entry.get().strip().upper()
        
        if not symbol:
            return
        
        # Auto-add .NS if not present
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol += '.NS'
        
        if symbol in self.selected_stocks:
            messagebox.showwarning("Duplicate Symbol", f"Stock {symbol} is already being tracked.")
            return
        
        # Validate symbol
        self._update_status(f"Validating {symbol}...")
        
        def validate_and_add():
            if self.data_fetcher.validate_symbol(symbol):
                self.selected_stocks.append(symbol)
                self.symbol_entry.delete(0, tk.END)
                self._update_status(f"Added {symbol} to tracking list")
                self._refresh_data()
            else:
                messagebox.showerror("Invalid Symbol", f"Symbol {symbol} not found. Please check the symbol.")
                self._update_status("Ready")
        
        # Run validation in thread to avoid GUI freezing
        threading.Thread(target=validate_and_add, daemon=True).start()
    
    def _remove_stock(self):
        """Remove selected stock from tracking"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a stock to remove.")
            return
        
        item = self.tree.item(selection[0])
        symbol = item['values'][0]
        
        if symbol in self.selected_stocks:
            self.selected_stocks.remove(symbol)
            self._refresh_data()
            self._update_status(f"Removed {symbol} from tracking")
    
    def _refresh_data(self):
        """Refresh stock data for all tracked stocks"""
        if not self.selected_stocks:
            return
        
        def fetch_data():
            try:
                self._update_status("Fetching Indian stock data...")
                self.current_data = self.data_fetcher.get_multiple_stocks_batch(self.selected_stocks)
                
                # Update GUI in main thread
                self.root.after(0, self._update_display)
                
            except Exception as e:
                logger.error(f"Error fetching data: {str(e)}")
                self.root.after(0, lambda: self._update_status(f"Error: {str(e)}"))
        
        # Run in separate thread
        threading.Thread(target=fetch_data, daemon=True).start()
    
    def _auto_refresh_data(self):
        """Refresh stock data for auto-refresh (forces fresh data)"""
        if not self.selected_stocks:
            return
        
        def fetch_fresh_data():
            try:
                self._update_status("Auto-refreshing stock data...")
                # Force refresh to bypass cache and get fresh data
                self.current_data = self.data_fetcher.get_multiple_stocks_batch(self.selected_stocks, force_refresh=True)
                
                # Update GUI in main thread
                self.root.after(0, self._update_display)
                
            except Exception as e:
                logger.error(f"Error in auto refresh: {str(e)}")
                self.root.after(0, lambda: self._update_status("Auto-refresh failed"))
        
        # Run in background thread
        threading.Thread(target=fetch_fresh_data, daemon=True).start()
    
    def _update_display(self):
        """Update the stock display with current data"""
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        if self.current_data is None or self.current_data.empty:
            self._update_status("No data to display")
            return
        
        # Populate treeview with Indian stock data
        for _, row in self.current_data.iterrows():
            # Format values for display
            values = (
                row.get('symbol', ''),
                (row.get('name', '')[:35] + '...' if len(str(row.get('name', ''))) > 35 
                 else row.get('name', '')),
                format_currency(row.get('current_price'), 'INR'),
                format_currency(row.get('change'), 'INR'),
                format_percentage(row.get('change_percent')),
                f"{row.get('volume', 0):,}" if row.get('volume') else 'N/A',
                format_large_number(row.get('market_cap'), 'INR'),
                f"{row.get('pe_ratio', 0):.2f}" if row.get('pe_ratio') else 'N/A',
                format_currency(row.get('fifty_two_week_high'), 'INR'),
                format_currency(row.get('fifty_two_week_low'), 'INR'),
                row.get('source', 'Unknown')
            )
            
            # Add with color coding
            item_id = self.tree.insert('', 'end', values=values)
            
            # Color code based on change
            if row.get('change', 0) > 0:
                self.tree.set(item_id, "Change (₹)", f"+{format_currency(row.get('change'), 'INR')}")
                self.tree.set(item_id, "Change %", format_percentage(row.get('change_percent')))
        
        self._update_status(f"Updated {len(self.current_data)} Indian stocks at {datetime.now().strftime('%H:%M:%S')}")
    
    def _save_to_excel(self):
        """Save current data to Excel file"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("No Data", "No data to save. Please fetch stock data first.")
            return
        
        try:
            filepath = self.excel_handler.save_stock_data(self.current_data)
            messagebox.showinfo("Success", f"Indian stock data saved to {Path(filepath).name}")
            self._update_status("Data exported to Excel successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def _load_popular_stocks(self):
        """Load popular Indian stocks"""
        try:
            trending = self.data_fetcher.get_trending_stocks()
            
            added_count = 0
            for symbol in trending:
                if symbol not in self.selected_stocks:
                    self.selected_stocks.append(symbol)
                    added_count += 1
            
            if added_count > 0:
                self._update_status(f"Added {added_count} popular Indian stocks")
                self._refresh_data()
            else:
                self._update_status("All popular stocks already being tracked")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load popular stocks: {str(e)}")
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        if self.is_auto_refresh.get():
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh in background thread"""
        # Stop any existing refresh first
        if hasattr(self, 'refresh_thread') and self.refresh_thread and self.refresh_thread.is_alive():
            self.stop_refresh.set()
            self.refresh_thread.join(timeout=1)
        
        # Clear the stop event and start fresh
        self.stop_refresh.clear()
        
        def auto_refresh_loop():
            print(f"Auto refresh started with interval: {self.refresh_interval.get()}")
            
            while not self.stop_refresh.is_set():
                interval_name = self.refresh_interval.get()
                interval_seconds = REFRESH_INTERVALS.get(interval_name, 300)
                print(f"Waiting {interval_seconds} seconds for next refresh...")
                
                # Wait for the interval or until stop is signaled
                if self.stop_refresh.wait(interval_seconds):
                    print("Auto refresh stopped")
                    break
                
                # Refresh data if still enabled and not stopped
                if self.is_auto_refresh.get() and not self.stop_refresh.is_set():
                    try:
                        print("Triggering auto refresh...")
                        self.root.after(0, self._auto_refresh_data)
                    except Exception as e:
                        print(f"Auto refresh error: {e}")
                else:
                    print("Auto refresh disabled or stopped")
                    break
        
        self.refresh_thread = threading.Thread(target=auto_refresh_loop, daemon=True)
        self.refresh_thread.start()
        
        # Do an immediate refresh when auto-refresh is enabled
        self._refresh_data()
        self._update_status("Auto-refresh enabled ✓")
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh"""
        self.stop_refresh.set()
        if self.refresh_thread and self.refresh_thread.is_alive():
            self.refresh_thread.join(timeout=1)
        self._update_status("Auto-refresh disabled")
    
    def _update_market_status(self):
        """Update Indian market status indicator"""
        try:
            is_open = self.data_fetcher.is_market_open()
            status = "🟢 NSE Open" if is_open else "🔴 NSE Closed"
            self.market_status_var.set(status)
        except Exception:
            self.market_status_var.set("❓ Market Status Unknown")
        
        # Schedule next update in 60 seconds
        self.root.after(60000, self._update_market_status)
    
    def _update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def _on_stock_double_click(self, event):
        """Handle double-click on stock item - open NSE page"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            symbol = item['values'][0]
            # Open NSE page for the stock
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            url = f"https://www.nseindia.com/get-quotes/equity?symbol={clean_symbol}"
            webbrowser.open(url)
    
    def _open_data_folder(self):
        """Open the data folder"""
        try:
            import os
            os.startfile(str(Path("data").absolute()))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")
    
    def _browse_excel_file(self):
        """Browse for an Excel file to use for live updates"""
        filename = filedialog.askopenfilename(
            title="Select Excel File for Live Updates",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            defaultextension=".xlsx"
        )
        if filename:
            self.excel_file_path.set(filename)
            self._update_status(f"Selected Excel file: {Path(filename).name}")
    
    def _create_new_excel_file(self):
        """Create a new Excel file for live updates"""
        filename = filedialog.asksaveasfilename(
            title="Create New Excel File for Live Updates",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            defaultextension=".xlsx",
            initialname=f"live_stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        if filename:
            self.excel_file_path.set(filename)
            self._update_status(f"Will create Excel file: {Path(filename).name}")
    
    def _toggle_excel_live_updates(self):
        """Toggle Excel live updates on/off"""
        if self.is_excel_live_update.get():
            self._start_excel_live_updates()
        else:
            self._stop_excel_live_updates()
    
    def _on_xlwings_toggle(self):
        """Handle xlwings option toggle"""
        if not XLWINGS_AVAILABLE:
            self.use_xlwings.set(False)
            messagebox.showinfo("XLWings Not Available", 
                              "XLWings is not installed. Install it with:\npip install xlwings")
            return
        
        # Update info text based on selection
        if self.use_xlwings.get():
            self.xlwings_info_label.config(text="💡 XLWings will provide ultra-smooth Excel updates", 
                                         foreground="green")
        else:
            self.xlwings_info_label.config(text="💡 XLWings provides ultra-smooth real-time Excel updates", 
                                         foreground="gray")
    
    def _start_excel_live_updates(self):
        """Start Excel live updates (openpyxl or xlwings)"""
        try:
            excel_file = self.excel_file_path.get().strip()
            if not excel_file:
                messagebox.showwarning("No Excel File", 
                                     "Please select or create an Excel file first.")
                self.is_excel_live_update.set(False)
                return
            
            # Parse update interval
            interval_text = self.excel_update_interval.get()
            if "second" in interval_text:
                interval_seconds = int(interval_text.split()[0])
            elif "minute" in interval_text:
                interval_seconds = int(interval_text.split()[0]) * 60
            else:
                interval_seconds = 30  # Default
            
            # Choose updater based on xlwings selection
            if self.use_xlwings.get() and XLWINGS_AVAILABLE:
                # Use xlwings for ultra-smooth updates
                visible = self.xlwings_visible.get()
                self.excel_xlwings_updater = ExcelXlwingsUpdater(
                    excel_file, 
                    interval_seconds, 
                    visible=visible
                )
                self.excel_xlwings_updater.set_status_callback(self._update_status)
                
                # Add current stocks to the Excel file
                if self.selected_stocks:
                    for stock in self.selected_stocks:
                        self.excel_xlwings_updater.add_stock(stock)
                
                # Start live updates
                self.excel_xlwings_updater.start_live_updates()
                self._update_status("⚡ XLWings ultra-smooth Excel live updates started!")
                
            else:
                # Use standard openpyxl updater
                self.excel_live_updater = ExcelLiveUpdater(excel_file, interval_seconds)
                self.excel_live_updater.set_status_callback(self._update_status)
                
                # Add current stocks to the Excel file
                if self.selected_stocks:
                    for stock in self.selected_stocks:
                        self.excel_live_updater.add_stock(stock)
                
                # Start live updates
                self.excel_live_updater.start_live_updates()
                self._update_status("🔄 Excel live updates started!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Excel live updates: {str(e)}")
            self.is_excel_live_update.set(False)
            self._update_status("Failed to start Excel live updates")
    
    def _stop_excel_live_updates(self):
        """Stop Excel live updates (both openpyxl and xlwings)"""
        if self.excel_live_updater:
            self.excel_live_updater.stop_live_updates()
            self.excel_live_updater.cleanup()
            self.excel_live_updater = None
        
        if self.excel_xlwings_updater:
            self.excel_xlwings_updater.stop_live_updates()
            self.excel_xlwings_updater.cleanup()
            self.excel_xlwings_updater = None
        
        self._update_status("Excel live updates stopped")
    
    def _manage_excel_stocks(self):
        """Open a dialog to manage stocks in Excel live updates"""
        current_updater = self.excel_live_updater or self.excel_xlwings_updater
        if not current_updater:
            messagebox.showwarning("Not Running", 
                                 "Excel live updates must be started first.")
            return
        
        # Create a simple dialog to show current stocks and allow adding/removing
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Excel Live Update Stocks")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Current stocks list
        ttk.Label(dialog, text="Stocks in Excel Live Updates:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        listbox = tk.Listbox(list_frame, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate listbox
        def refresh_list():
            listbox.delete(0, tk.END)
            if current_updater:
                for stock in current_updater.tracked_stocks:
                    listbox.insert(tk.END, stock)
        
        refresh_list()
        
        # Add/Remove controls
        controls_frame = ttk.Frame(dialog)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Add stock
        add_frame = ttk.Frame(controls_frame)
        add_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(add_frame, text="Add Stock:").pack(side="left", padx=(0, 10))
        stock_entry = ttk.Entry(add_frame)
        stock_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def add_stock():
            symbol = stock_entry.get().strip().upper()
            if symbol and current_updater:
                if current_updater.add_stock(symbol):
                    stock_entry.delete(0, tk.END)
                    refresh_list()
        
        def remove_stock():
            selection = listbox.curselection()
            if selection and current_updater:
                symbol = listbox.get(selection[0])
                if current_updater.remove_stock(symbol):
                    refresh_list()
        
        ttk.Button(add_frame, text="Add", command=add_stock).pack(side="left")
        stock_entry.bind('<Return>', lambda e: add_stock())
        
        # Remove stock
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Remove Selected", command=remove_stock).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="right")
    
    def _manual_excel_update(self):
        """Trigger a manual Excel update"""
        current_updater = self.excel_live_updater or self.excel_xlwings_updater
        
        if not current_updater:
            if not self.excel_file_path.get().strip():
                messagebox.showwarning("No Excel File", 
                                     "Please select or create an Excel file first.")
                return
            
            # Create a temporary updater for manual update
            try:
                if self.use_xlwings.get() and XLWINGS_AVAILABLE:
                    temp_updater = ExcelXlwingsUpdater(
                        self.excel_file_path.get(), 
                        30, 
                        visible=self.xlwings_visible.get()
                    )
                else:
                    temp_updater = ExcelLiveUpdater(self.excel_file_path.get(), 30)
                
                temp_updater.set_status_callback(self._update_status)
                
                # Add current stocks
                if self.selected_stocks:
                    for stock in self.selected_stocks:
                        temp_updater.add_stock(stock)
                
                # Perform manual update
                temp_updater.manual_update()
                temp_updater.cleanup()
                
            except Exception as e:
                messagebox.showerror("Error", f"Manual update failed: {str(e)}")
        else:
            current_updater.manual_update()
    
    def _on_closing(self):
        """Handle application closing"""
        self._stop_auto_refresh()
        self._stop_excel_live_updates()
        self.root.destroy()

def create_modern_style():
    """Create modern styling for the application"""
    style = ttk.Style()
    
    # Configure modern theme
    style.theme_use('clam')
    
    # Configure styles
    style.configure("TLabel", font=("Arial", 9))
    style.configure("TButton", font=("Arial", 9))
    style.configure("TFrame", background=GUI_CONFIG["theme"]["bg_color"])
    
    return style
