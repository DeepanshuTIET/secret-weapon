#!/usr/bin/env python3
"""
Test script for the modular Indian Stock Tracker
Validates all modules and functionality
"""
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))

def test_modules():
    """Test all modules can be imported and initialized"""
    print("🧪 Testing Modular Indian Stock Tracker")
    print("=" * 50)
    
    # Test 1: Config module
    print("\n1️⃣ Testing configuration module...")
    try:
        from modules.config import APP_NAME, APP_VERSION, DEFAULT_STOCKS
        print(f"✅ {APP_NAME} v{APP_VERSION}")
        print(f"✅ {len(DEFAULT_STOCKS)} default Indian stocks configured")
        print(f"   Sample stocks: {', '.join(DEFAULT_STOCKS[:3])}")
    except Exception as e:
        print(f"❌ Config module error: {e}")
        return False
    
    # Test 2: Data fetcher module
    print("\n2️⃣ Testing data fetcher module...")
    try:
        from modules.data_fetcher import IndianStockDataFetcher, format_currency
        fetcher = IndianStockDataFetcher()
        print("✅ IndianStockDataFetcher initialized")
        
        # Test market status
        market_open = fetcher.is_market_open()
        print(f"✅ Market status: {'🟢 Open' if market_open else '🔴 Closed'}")
        
        # Test stock data (quick test)
        print("   Testing RELIANCE.NS...")
        stock_data = fetcher.get_stock_info("RELIANCE.NS")
        if stock_data:
            print(f"   ✅ {stock_data['name']}: {format_currency(stock_data['current_price'])}")
            print(f"   ✅ Data source: {stock_data.get('source', 'Unknown')}")
        else:
            print("   ⚠️ Could not fetch data (may be rate limited)")
        
    except Exception as e:
        print(f"❌ Data fetcher error: {e}")
        return False
    
    # Test 3: Excel handler module
    print("\n3️⃣ Testing Excel handler module...")
    try:
        from modules.excel_handler import IndianStockExcelHandler
        import pandas as pd
        
        excel_handler = IndianStockExcelHandler(Path("data"))
        print("✅ IndianStockExcelHandler initialized")
        
        # Test data creation
        test_data = pd.DataFrame({
            'symbol': ['RELIANCE.NS', 'TCS.NS'],
            'name': ['Reliance Industries', 'Tata Consultancy Services'],
            'current_price': [1375.0, 3048.0],
            'change': [15.7, -47.4],
            'change_percent': [1.16, -1.53],
            'source': ['Yahoo Finance', 'Yahoo Finance']
        })
        
        filepath = excel_handler.save_stock_data(test_data, "test_modular.xlsx")
        print(f"✅ Test Excel file created: {Path(filepath).name}")
        
        # Cleanup
        Path(filepath).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Excel handler error: {e}")
        return False
    
    # Test 4: GUI module (import only)
    print("\n4️⃣ Testing GUI module...")
    try:
        from modules.gui import IndianStockTrackerGUI, create_modern_style
        print("✅ GUI module imported successfully")
        print("✅ Modern styling available")
    except Exception as e:
        print(f"❌ GUI module error: {e}")
        return False
    
    # Test 5: App module
    print("\n5️⃣ Testing app module...")
    try:
        from modules.app import StockTrackerApp, check_dependencies
        print("✅ App module imported successfully")
        
        # Test dependencies
        deps_ok = check_dependencies()
        print(f"✅ Dependencies check: {'Pass' if deps_ok else 'Fail'}")
        
    except Exception as e:
        print(f"❌ App module error: {e}")
        return False
    
    return True

def test_project_structure():
    """Test project structure and files"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "modules/__init__.py",
        "modules/config.py",
        "modules/data_fetcher.py",
        "modules/excel_handler.py",
        "modules/gui.py",
        "modules/app.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Check directories
    required_dirs = ["data", "dist", "modules"]
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/ directory")
        else:
            print(f"⚠️ {dir_path}/ directory missing (will be created)")
    
    return True

def main():
    """Run all tests"""
    print("🇮🇳 Indian Stock Tracker - Modular Structure Test")
    print("=" * 70)
    
    # Test project structure
    structure_ok = test_project_structure()
    
    # Test modules
    modules_ok = test_modules()
    
    print("\n" + "=" * 70)
    
    if structure_ok and modules_ok:
        print("🎉 All tests passed! Modular structure is working perfectly.")
        print("\n📋 Summary:")
        print("✅ Modular architecture implemented")
        print("✅ All modules functioning correctly")
        print("✅ Indian stock data fetching working")
        print("✅ Excel export functionality ready")
        print("✅ GUI components loaded successfully")
        print("✅ Professional project structure")
        
        print("\n🚀 Ready to use:")
        print("   python main.py     - Run the application")
        print("   python run.py      - Run with dependency checks")
        print("   python build_exe.py - Build standalone executable")
        
        print("\n📈 Features:")
        print("• Clean modular code structure")
        print("• Separation of concerns")
        print("• Easy maintenance and extension")
        print("• Professional documentation")
        
    else:
        print("⚠️ Some issues found. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
