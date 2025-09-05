# 🇮🇳 Indian Stock Tracker

A professional real-time stock tracking application specifically designed for Indian markets (NSE/BSE). Built with Python and featuring a modern GUI, live data updates, and Excel export capabilities.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

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
- Summary sheets with market statistics
- Automatic file management and cleanup
- Historical data tracking

### 🛡️ **Robust & Reliable**
- Rate limiting protection for APIs
- Fallback data sources (NSE API → Yahoo Finance)
- Error handling and retry mechanisms
- Comprehensive logging

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Internet connection for live data

### Installation

1. **Download/Clone the project**
   ```bash
   git clone <repository-url>
   cd IndianStockTracker_Final
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
IndianStockTracker_Final/
│
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
│
├── modules/                  # Core application modules
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration settings
│   ├── app.py               # Main application controller
│   ├── gui.py               # GUI interface
│   ├── data_fetcher.py      # Stock data fetching
│   └── excel_handler.py     # Excel export functionality
│
├── data/                    # Excel exports and data files
└── dist/                    # Built executables (if created)
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
- 30 seconds
- 1 minute
- 5 minutes (default)
- 15 minutes
- 30 minutes
- 1 hour

## 📊 Usage Guide

### **Getting Started**
1. Launch the application using `python main.py`
2. The app loads with 15 popular Indian stocks pre-configured
3. Click "🔄 Refresh" to fetch latest data
4. Enable "Auto Refresh" for continuous updates

### **Managing Stocks**
- **Add Stock**: Enter symbol and click "Add Stock"
- **Remove Stock**: Select a stock in the table and click "🗑️ Remove"
- **Load Popular**: Click "Load Popular" to add trending stocks

### **Viewing Data**
- **Price Changes**: Green for gains, orange for losses
- **Market Status**: 🟢 for open, 🔴 for closed
- **Double-click**: Opens stock page on NSE website
- **Columns**: Symbol, Company Name, Price, Change, Volume, etc.

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

#### **No data or rate limiting errors**
- Check internet connection
- Wait a few minutes and try again
- Verify stock symbols are correct (use .NS for NSE stocks)

#### **GUI not starting**
- Ensure Python supports Tkinter: `python -m tkinter`
- Update to Python 3.7+

#### **Excel export errors**
- Ensure `data/` directory exists and is writable
- Close any open Excel files with same name
- Check disk space

### **Symbol Format**
- **NSE stocks**: `SYMBOL.NS` (e.g., `RELIANCE.NS`)
- **BSE stocks**: `SYMBOL.BO` (e.g., `RELIANCE.BO`)
- **Auto-completion**: App adds `.NS` if no suffix provided

## 📈 Performance

- **Data Updates**: Sub-second refresh capability
- **Multiple Stocks**: Supports 50+ stocks simultaneously
- **Memory Usage**: ~50MB for typical usage
- **Network**: Optimized API calls with rate limiting

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
- **Yahoo Finance** for reliable API
- **Indian Stock Market** community
- **Python** and **Tkinter** communities

---

**Built with ❤️ for Indian Stock Market traders and investors**

*Happy Trading! 📈🇮🇳*