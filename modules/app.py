"""
Main application controller for Indian Stock Tracker
Handles application lifecycle and coordination between modules
"""
import tkinter as tk
from tkinter import messagebox
import logging
import sys
from pathlib import Path

from .gui import IndianStockTrackerGUI, create_modern_style
from .config import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)

class StockTrackerApp:
    """
    Main application class for Indian Stock Tracker
    """
    
    def __init__(self):
        """Initialize the application"""
        self.root = None
        self.gui = None
        
    def run(self):
        """Run the Indian Stock Tracker application"""
        try:
            logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
            
            # Create main window
            self.root = tk.Tk()
            
            # Set up modern styling
            create_modern_style()
            
            # Create and initialize GUI
            self.gui = IndianStockTrackerGUI(self.root)
            
            # Set up global error handling
            self.root.report_callback_exception = self._handle_exception
            
            logger.info("Application started successfully")
            
            # Start the main event loop
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}")
            self._show_error("Startup Error", f"Failed to start {APP_NAME}:\n{str(e)}")
            sys.exit(1)
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions in the GUI"""
        if issubclass(exc_type, KeyboardInterrupt):
            self.root.destroy()
            return
        
        logger.error("Uncaught GUI exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        error_msg = f"An unexpected error occurred:\n{exc_type.__name__}: {exc_value}"
        self._show_error("Application Error", error_msg)
    
    def _show_error(self, title: str, message: str):
        """Show error message to user"""
        try:
            if self.root:
                messagebox.showerror(title, message)
            else:
                # Fallback if no GUI is available
                print(f"ERROR - {title}: {message}")
        except:
            print(f"ERROR - {title}: {message}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'pandas',
        'openpyxl',
        'yfinance',
        'requests',
        'pytz'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Missing required modules: {', '.join(missing_modules)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += f"pip install {' '.join(missing_modules)}"
        
        print(error_msg)
        
        # Try to show GUI error if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Missing Dependencies", error_msg)
            root.destroy()
        except:
            pass
        
        return False
    
    return True
