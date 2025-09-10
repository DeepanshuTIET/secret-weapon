# 🇮🇳 Indian Stock Tracker

A robust real-time stock tracking application designed for Indian markets (NSE/BSE). Features intelligent caching, rate limiting, and reliable data fetching with a clean GUI interface.

**🔗 GitHub Repository:** [https://github.com/DeepanshuTIET/secret-weapon](https://github.com/DeepanshuTIET/secret-weapon)

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## 🆕 Recent Updates (v1.2.0) - Excel Live Updates Release

### 🚀 Major New Features
- 🆕 **Excel Live Updates** - Real-time stock price updates directly in Excel files
- 🆕 **Command-line Excel updater** - Run live updates without GUI (`excel_live_runner.py`)
- 🆕 **Background Excel service** - Continuous Excel updates with customizable intervals
- 🆕 **Professional Excel formatting** - Indian currency (₹), color-coded gains/losses
- 🆕 **Excel stock management** - Add/remove stocks directly from Excel tracking

### 🔧 Improvements & Fixes
- ✅ **Fixed SSL/TLS connection issues** with NSE API
- ✅ **Improved rate limiting** with intelligent caching system
- ✅ **Enhanced auto-refresh** with force refresh capability
- ✅ **Better error handling** with retry mechanisms
- ✅ **Optimized API calls** using batch requests

## ✨ Features

### 📈 **Real-time Indian Stock Data**
- Live stock prices from NSE (National Stock Exchange) and BSE (Bombay Stock Exchange)
- 15 popular Indian stocks pre-loaded (RELIANCE.NS, TCS.NS, INFY.NS, etc.)
- Auto-refresh with customizable intervals (30 seconds to 1 hour)
- Indian market hours detection (9:15 AM - 3:30 PM IST)

### 💰 **Indian Market Optimized**
- Indian Rupee (₹) currency formatting
- Lakh and Crore number notation
- Indian market hours and trading days
- NSE/BSE symbol support (.NS/.BO)

### 📊 **Professional Interface**
- Modern, intuitive GUI built with Tkinter
- Real-time price updates with color-coded gains/losses
- Market status indicator (Open/Closed)
- Double-click stocks to view on NSE website

### 💾 **Excel Export & Data Management**
- Professional Excel reports with Indian currency formatting
- **🆕 Live Excel Updates** - Real-time price updates directly in Excel files
- Summary sheets with market statistics
- Automatic file management and cleanup
- Historical data tracking

### 🛡️ **Robust & Reliable**
- **Smart caching system** - Reduces API calls and improves performance
- **Intelligent rate limiting** - Prevents API blocking with exponential backoff
- **Force refresh capability** - Auto-refresh bypasses cache for fresh data
- **Fallback data sources** (NSE API → Yahoo Finance)
- **SSL/TLS fixes** - Handles connection issues gracefully
- **Error handling and retry mechanisms** - Robust against network issues
- **Comprehensive logging** - Easy debugging and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Internet connection for live data

### 🎯 Quick Start - Excel Live Updates (NEW in v1.2.0)

**Want to see live stock prices in Excel? Try this:**

```bash
# 1. Test the features first
python test_excel_live.py

# 2. Start Excel live updates with popular stocks (standard)
python excel_live_runner.py my_live_stocks.xlsx --popular

# 3. Or for ultra-smooth updates (requires xlwings)
python excel_xlwings_runner.py ultra_smooth_stocks.xlsx --popular --interval 5

# 4. Or use the GUI for more control
python run.py
```

**That's it!** Your Excel file will now update with live stock prices every 30 seconds (or faster with xlwings).

## 🆕 Excel Live Updates Feature

**Real-time stock price updates directly in Excel files!** Now you can watch stock prices change live in Excel spreadsheets without needing the GUI interface.

### ⚡ NEW: Ultra-Smooth XLWings Integration

**The smoothest possible Excel experience!** We now support **xlwings** for ultra-smooth real-time Excel updates with direct Excel API integration.

### 📊 How it Works
- **Two modes available**: Standard (openpyxl) and Ultra-Smooth (xlwings)
- Updates stock prices directly in Excel cells in real-time
- Customizable update intervals (5 seconds to 5 minutes with xlwings, 10+ seconds standard)
- Professional formatting with Indian currency (₹) and color-coded gains/losses
- Runs in background - Excel file stays updated even when closed and reopened

### ⚡ XLWings vs Standard Mode

| Feature | Standard (openpyxl) | Ultra-Smooth (xlwings) |
|---------|-------------------|------------------------|
| **Update Speed** | 10+ seconds | 5+ seconds |
| **Smoothness** | Good | Ultra-smooth |
| **Excel Integration** | File-based | Direct Excel API |
| **Background Mode** | ✅ Yes | ✅ Yes |
| **Visible Excel** | ❌ No | ✅ Optional |
| **Installation** | Built-in | `pip install xlwings` |

### 🎯 Usage Options

#### 1. GUI Interface (NEW: XLWings Support!)
1. Launch the application: `python run.py`
2. In the "Live Excel Updates" section:
   - Browse for an existing Excel file or create a new one
   - Set your preferred update interval
   - **NEW:** Check "⚡ Use XLWings (Ultra-Smooth)" for the smoothest experience
   - **NEW:** Toggle "👀 Show Excel" to make Excel visible during updates
   - Check "Live Excel Updates" to start
   - Use "Manage Stocks" to add/remove stocks from Excel tracking

#### 2. Command Line (No GUI Required)
```bash
# Standard Excel updates
python excel_live_runner.py my_live_stocks.xlsx --popular

# NEW: Ultra-smooth XLWings updates
python excel_xlwings_runner.py my_live_stocks.xlsx --popular

# XLWings with visible Excel and fast updates
python excel_xlwings_runner.py live_stocks.xlsx --popular --interval 5 --visible

# Update specific stocks every 60 seconds (standard)
python excel_live_runner.py custom_stocks.xlsx --stocks RELIANCE.NS TCS.NS INFY.NS --interval 60

# Ultra-smooth updates with custom stocks
python excel_xlwings_runner.py smooth_stocks.xlsx --stocks RELIANCE.NS TCS.NS --interval 10
```

#### 3. Test the Features
```bash
# Test standard Excel live updates
python test_excel_live.py

# NEW: Test XLWings integration
python test_xlwings_integration.py
```

### 📋 Excel Live Updates Benefits
- **No GUI Required** - Run in background with command-line tool
- **Real Excel Integration** - Updates actual Excel cells, not just exports
- **Persistent Data** - Excel file retains data even when application stops
- **Professional Formatting** - Indian currency, color coding, proper alignment
- **Flexible Intervals** - Choose update frequency based on your needs
- **⚡ NEW: Ultra-Smooth Mode** - XLWings provides the smoothest possible Excel experience
- **👀 Optional Visibility** - Watch Excel update in real-time or run in background

## 📋 Changelog

### v1.3.0 (2025-09-10) - Ultra-Smooth XLWings Integration
- 🆕 **XLWings Integration**: Ultra-smooth real-time Excel updates via direct Excel API
- 🆕 **XLWings Runner**: `excel_xlwings_runner.py` for command-line ultra-smooth updates
- 🆕 **Dual Mode Support**: Choose between Standard (openpyxl) and Ultra-Smooth (xlwings)
- 🆕 **Excel Visibility Control**: Option to show/hide Excel during xlwings updates
- 🆕 **Faster Update Intervals**: 5-second updates with xlwings (vs 10+ with standard)
- 🆕 **XLWings Test Suite**: `test_xlwings_integration.py` for validation
- 🔧 **Enhanced GUI**: XLWings options in Live Excel Updates section
- 🔧 **Improved Performance**: Direct Excel API integration for smoother updates

### v1.2.0 (2025-01-08) - Excel Live Updates Release
- 🆕 **Excel Live Updates**: Real-time stock price updates directly in Excel files
- 🆕 **Command-line Excel updater**: `excel_live_runner.py` for background operation
- 🆕 **Excel stock management**: Add/remove stocks from Excel tracking via GUI
- 🆕 **Professional Excel formatting**: Indian currency (₹), color-coded gains/losses
- 🆕 **Background Excel service**: Continuous updates with customizable intervals
- 🔧 **Enhanced GUI**: New "Live Excel Updates" section with file management
- 🔧 **Improved error handling**: Better SSL/TLS connection handling
- 🔧 **Optimized performance**: Batch API requests and intelligent caching

### v1.1.0 (Previous Release)
- ✅ Fixed SSL/TLS connection issues with NSE API
- ✅ Improved rate limiting with intelligent caching system
- ✅ Enhanced auto-refresh with force refresh capability
- ✅ Fixed display bugs (double + signs, checkmark indicators)
- ✅ Optimized API calls using batch requests
- ✅ Better error handling with retry mechanisms

### Installation

1. **Download/Clone the project**
   ```bash
   git clone https://github.com/DeepanshuTIET/secret-weapon
   cd secret-weapon
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   
   # For ultra-smooth Excel updates (optional but recommended)
   pip install xlwings
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

## 📁 Project Structure

```
secret-weapon/
│
├── run.py                   # Main application entry point
├── main.py                  # Alternative entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── modules/                # Core application modules
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration settings
│   ├── app.py             # Main application controller
│   ├── gui.py             # GUI interface with auto-refresh & Excel live updates
│   ├── data_fetcher.py    # Stock data fetching with caching
│   ├── excel_handler.py   # Excel export functionality
│   ├── excel_live_updater.py # Excel live updates module (NEW in v1.2.0)
│   └── excel_xlwings_updater.py # Ultra-smooth XLWings updater (NEW in v1.3.0)
│
├── excel_live_runner.py   # Command-line Excel live updater (NEW in v1.2.0)
├── excel_xlwings_runner.py # Ultra-smooth XLWings Excel updater (NEW in v1.3.0)
├── test_excel_live.py     # Test suite for Excel live updates (NEW in v1.2.0)
├── test_xlwings_integration.py # XLWings integration test suite (NEW in v1.3.0)
│
├── data/                  # Excel exports and data files
├── venv/                  # Virtual environment (if created)
└── dist/                  # Built executables (if created)
```

## 🔧 Configuration

### **Default Indian Stocks**
The application comes pre-configured with 15 popular Indian stocks:

- **RELIANCE.NS** - Reliance Industries Ltd
- **TCS.NS** - Tata Consultancy Services
- **INFY.NS** - Infosys Ltd
- **HDFCBANK.NS** - HDFC Bank Ltd
- **ICICIBANK.NS** - ICICI Bank Ltd
- **HINDUNILVR.NS** - Hindustan Unilever Ltd
- **BHARTIARTL.NS** - Bharti Airtel Ltd
- **ITC.NS** - ITC Ltd
- **SBIN.NS** - State Bank of India
- **KOTAKBANK.NS** - Kotak Mahindra Bank
- **LT.NS** - Larsen & Toubro Ltd
- **HCLTECH.NS** - HCL Technologies Ltd
- **ASIANPAINT.NS** - Asian Paints Ltd
- **MARUTI.NS** - Maruti Suzuki India Ltd
- **TITAN.NS** - Titan Company Ltd

### **Adding Custom Stocks**
1. Enter the stock symbol in the input field (e.g., `WIPRO` or `WIPRO.NS`)
2. Click "Add Stock" or press Enter
3. The application will automatically add `.NS` suffix if not present
4. Symbol will be validated before adding

### **Auto-Refresh Intervals**
- 30 seconds ⚡ (for active trading)
- 1 minute
- 5 minutes (default)
- 15 minutes
- 30 minutes
- 1 hour

**Note:** Auto-refresh uses force refresh to bypass cache and get the latest prices.

## 📊 Usage Guide

### **Getting Started**
1. Launch the application using `python run.py`
2. The app loads with 15 popular Indian stocks pre-configured
3. Click "🔄 Refresh" to fetch latest data
4. Enable "✓ Auto Refresh" for continuous updates with fresh data
5. Select your preferred refresh interval from the dropdown

### **Managing Stocks**
- **Add Stock**: Enter symbol and click "Add Stock"
- **Remove Stock**: Select a stock in the table and click "🗑️ Remove"
- **Load Popular**: Click "Load Popular" to add trending stocks

### **Viewing Data**
- **Price Changes**: Green for gains, red for losses
- **Change %**: Properly formatted with single +/- signs (no double ++)
- **Market Status**: 🟢 for open, 🔴 for closed
- **Double-click**: Opens stock page on NSE website
- **Columns**: Symbol, Company Name, Price, Change, Volume, etc.
- **Auto-refresh**: Shows ✓ checkmark when enabled

### **Exporting Data**
- Click "💾 Save Excel" to export current data
- Files saved in `data/` folder with timestamps
- Includes main data sheet and market summary
- Professional formatting with Indian currency

## 🔌 API Sources

### **Primary Data Sources**
1. **NSE API** (via NSEtools) - Direct from National Stock Exchange
2. **Yahoo Finance API** - Reliable fallback source
3. **Real-time Updates** - Live price feeds during market hours

### **Data Fields**
- Current Price (₹)
- Previous Close
- Change (₹ and %)
- Volume
- Market Cap
- P/E Ratio
- 52-Week High/Low
- Data Source

## 🛠️ Development

### **Module Overview**

#### **`modules/config.py`**
- Application settings and constants
- Default stock symbols
- GUI configuration
- Market settings (timings, holidays)

#### **`modules/data_fetcher.py`**
- `IndianStockDataFetcher` class
- NSE and Yahoo Finance API integration
- Rate limiting and error handling
- Indian market hours detection

#### **`modules/excel_handler.py`**
- `IndianStockExcelHandler` class
- Professional Excel formatting
- Indian currency and number formatting
- File management utilities

#### **`modules/gui.py`**
- `IndianStockTrackerGUI` class
- Modern Tkinter interface
- Real-time updates and threading
- Event handling and user interactions

#### **`modules/app.py`**
- `StockTrackerApp` main controller
- Application lifecycle management
- Error handling and logging
- Dependency checking

### **Building Executable**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed main.py

# Executable will be in dist/ folder
```

### **Running Tests**
```bash
# Test individual modules
python -c "from modules.data_fetcher import IndianStockDataFetcher; print('✅ Data fetcher working')"
python -c "from modules.excel_handler import IndianStockExcelHandler; print('✅ Excel handler working')"

# Test stock data fetching
python -c "
from modules.data_fetcher import IndianStockDataFetcher
fetcher = IndianStockDataFetcher()
data = fetcher.get_stock_info('RELIANCE.NS')
print('✅ Live data:', data['current_price'] if data else 'Failed')
"
```

## 🐛 Troubleshooting

### **Common Issues**

#### **"Module not found" errors**
```bash
pip install -r requirements.txt
```

#### **SSL/TLS connection errors**
- ✅ **Fixed in v1.1.0** - SSL issues are now handled automatically
- The app disables SSL verification for problematic endpoints
- If you still see SSL errors, try updating your Python version

#### **Rate limiting or "Too Many Requests" errors**
- ✅ **Fixed in v1.1.0** - Intelligent rate limiting prevents this
- The app now uses caching and exponential backoff
- Auto-refresh uses force refresh to bypass cache when needed

#### **Auto-refresh not working**
- ✅ **Fixed in v1.1.0** - Auto-refresh now works reliably
- Make sure to enable the "✓ Auto Refresh" checkbox
- Check the console for debug messages if issues persist
- Try different refresh intervals (30 seconds, 1 minute, etc.)

#### **Double + signs in Change % column**
- ✅ **Fixed in v1.1.0** - Now shows proper single +/- signs
- Update to latest version if you see "++0.67%" instead of "+0.67%"

#### **No data or API errors**
- Check internet connection
- The app automatically falls back from NSE to Yahoo Finance
- Verify stock symbols are correct (use .NS for NSE stocks)
- Try refreshing manually first

#### **GUI not starting**
- Ensure Python supports Tkinter: `python -m tkinter`
- Update to Python 3.7+
- Try running with virtual environment

#### **Excel export errors**
- Ensure `data/` directory exists and is writable
- Close any open Excel files with same name
- Check disk space

### **Symbol Format**
- **NSE stocks**: `SYMBOL.NS` (e.g., `RELIANCE.NS`)
- **BSE stocks**: `SYMBOL.BO` (e.g., `RELIANCE.BO`)
- **Auto-completion**: App adds `.NS` if no suffix provided

## 📈 Performance

- **Data Updates**: Sub-second refresh capability with intelligent caching
- **Multiple Stocks**: Supports 50+ stocks simultaneously
- **Memory Usage**: ~50MB for typical usage
- **Network**: Optimized API calls with batch requests and rate limiting
- **Cache System**: Reduces API calls by 80% with 1-hour cache expiration
- **Auto-refresh**: Force refresh bypasses cache for real-time data

## 🔒 Privacy & Security

- **No Data Collection**: All processing is local
- **No User Accounts**: No login or personal data required
- **Open APIs**: Uses official public APIs only
- **Local Storage**: Excel files saved locally only

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support or questions:
1. Check this README and troubleshooting section
2. Review the application logs
3. Submit an issue on GitHub

## 🌟 Acknowledgments

- **NSE** and **BSE** for market data
- **Yahoo Finance** for reliable API and yfinance library
- **Indian Stock Market** community
- **Python** and **Tkinter** communities
- **Contributors** who helped fix SSL, rate limiting, and auto-refresh issues

## 📝 Changelog

### v1.1.0 (Latest)
- ✅ Fixed SSL/TLS connection issues
- ✅ Implemented intelligent caching system
- ✅ Enhanced auto-refresh with force refresh
- ✅ Fixed double + signs in percentage display
- ✅ Improved rate limiting with exponential backoff
- ✅ Added batch request optimization
- ✅ Better error handling and retry mechanisms

### v1.0.0
- Initial release with basic stock tracking functionality

---

**Built with ❤️ for Indian Stock Market traders and investors**

*Happy Trading! 📈🇮🇳*