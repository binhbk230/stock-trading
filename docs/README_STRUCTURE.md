# Stock Trading Analysis System

Hệ thống phân tích và gợi ý giao dịch cổ phiếu Việt Nam

## Cấu trúc dự án

```
stock-trading/
├── app.py                      # Streamlit web application
├── requirements.txt            # Python dependencies
├── README.md
│
├── src/                        # Source code chính
│   ├── __init__.py
│   ├── core/                   # Core modules
│   │   ├── __init__.py
│   │   ├── stock_analyzer.py   # Main stock analyzer (trước đây là main.py)
│   │   ├── technical_indicators.py
│   │   ├── signal_generator.py
│   │   └── portfolio_manager.py
│   │
│   ├── analyzers/              # Các module phân tích chuyên sâu
│   │   ├── __init__.py
│   │   ├── vnindex_analyzer.py
│   │   ├── sector_analyzer.py
│   │   └── batch_analyzer.py
│   │
│   └── utils/                  # Utilities và data
│       ├── __init__.py
│       └── top_stocks.py
│
├── tests/                      # Test files
│   ├── test_*.py
│
├── scripts/                    # Demo và debugging scripts
│   ├── demo.py
│   ├── analyze_*.py
│   ├── compare_*.py
│   └── debug_*.py
│
├── config/                     # Configuration files
│   ├── users_config.json
│   └── users_config.example.json
│
├── portfolios/                 # User portfolios data
│   └── *.json
│
└── docs/                       # Documentation
    ├── AUTHENTICATION.md
    ├── DATA_TIMING.md
    ├── HOLDING_RECOMMENDATIONS.md
    ├── PORTFOLIO_FEATURE.md
    ├── SECTOR_ANALYSIS.md
    ├── SELL_WITH_VNINDEX.md
    ├── VNINDEX_INVESTMENT_STRATEGY.md
    └── VNINDEX_LOGIC.md
```

## Cài đặt

```bash
# Clone repository
git clone <your-repo-url>
cd stock-trading

# Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình users
cp config/users_config.example.json config/users_config.json
# Chỉnh sửa config/users_config.json với thông tin của bạn
```

## Chạy ứng dụng

```bash
# Chạy Streamlit app
streamlit run app.py

# Hoặc sử dụng Python để phân tích
python -c "from src.core.stock_analyzer import StockAnalyzer; analyzer = StockAnalyzer('VNM'); print(analyzer.analyze())"
```

## Modules chính

### Core (`src/core/`)
- **stock_analyzer.py**: Module phân tích chính cho từng cổ phiếu
- **technical_indicators.py**: Các chỉ báo kỹ thuật (RSI, MACD, Bollinger Bands, etc.)
- **signal_generator.py**: Sinh tín hiệu mua/bán
- **portfolio_manager.py**: Quản lý danh mục đầu tư

### Analyzers (`src/analyzers/`)
- **vnindex_analyzer.py**: Phân tích VNINDEX
- **sector_analyzer.py**: Phân tích theo ngành
- **batch_analyzer.py**: Phân tích hàng loạt cổ phiếu

### Utils (`src/utils/`)
- **top_stocks.py**: Danh sách cổ phiếu và phân loại ngành

## Tính năng

- ✅ Phân tích kỹ thuật đầy đủ
- ✅ Tín hiệu mua/bán thông minh
- ✅ Phân tích VNINDEX
- ✅ Phân tích theo ngành
- ✅ Quản lý danh mục đầu tư
- ✅ Web interface với Streamlit
- ✅ Batch analysis cho nhiều cổ phiếu

## License

Private project
