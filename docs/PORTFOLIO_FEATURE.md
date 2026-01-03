# 💼 Portfolio Management Feature

## Tính năng quản lý danh mục đầu tư cá nhân

### 🎯 Chức năng chính

#### 1. **Theo dõi danh mục (Portfolio Tracking)**
- ✅ Lưu trữ thông tin cổ phiếu: mã CP, số lượng, giá mua, ngày mua
- ✅ Hiển thị giá hiện tại và % thay đổi
- ✅ Tính tổng giá trị danh mục real-time

#### 2. **Phân tích lãi/lỗ (P&L Analysis)**
- ✅ Tính lãi/lỗ từng mã: `(giá hiện tại - giá mua) × số lượng`
- ✅ Tỷ suất sinh lời (ROI %): `(giá hiện tại - giá mua) / giá mua × 100`
- ✅ Tổng P&L toàn danh mục
- ✅ Best/Worst performers

#### 3. **Cảnh báo tín hiệu bán**
- ✅ Tích hợp `signal_generator.py` để check tín hiệu bán
- ✅ Hiển thị độ tin cậy và điểm bán
- ✅ Khuyến nghị dựa trên phân tích kỹ thuật

#### 4. **Biểu đồ & Báo cáo**
- ✅ Pie chart phân bổ danh mục theo giá trị
- ✅ Bar chart lãi/lỗ theo mã (%)
- ✅ Bảng chi tiết với metrics đầy đủ

---

## 📁 Cấu trúc lưu trữ

### Thư mục portfolios/
```
portfolios/
├── user1.json
└── user2.json
```

### Format file JSON
```json
{
  "username": "user1",
  "holdings": [
    {
      "symbol": "VCB",
      "quantity": 100,
      "buy_price": 85.5,
      "buy_date": "2025-01-15",
      "notes": "Ngân hàng tốt",
      "added_at": "2025-12-30 10:30:00"
    }
  ],
  "last_updated": "2025-12-30 10:30:00"
}
```

---

## 🚀 Cách sử dụng

### 1. Chọn mode "💼 Danh mục của tôi"
- Trong sidebar, chọn "💼 Danh mục của tôi"

### 2. Chọn tài khoản (user1/user2)
- Dropdown ở đầu trang

### 3. Các tab chức năng:

#### Tab "📊 Tổng quan"
- Xem tổng vốn, giá trị hiện tại, lãi/lỗ
- Bảng chi tiết từng mã
- Biểu đồ phân bổ và P&L
- Best/Worst performers

#### Tab "➕ Thêm cổ phiếu"
- Form nhập:
  - Mã cổ phiếu (VD: VCB, VHM...)
  - Số lượng
  - Giá mua
  - Ngày mua
  - Ghi chú (optional)

#### Tab "📋 Quản lý"
- Xem danh sách cổ phiếu đã thêm
- Xóa cổ phiếu
- Link đến phân tích chi tiết

#### Tab "⚠️ Cảnh báo bán"
- **Tự động kiểm tra** tín hiệu bán cho tất cả cổ phiếu
- Hiển thị:
  - Độ tin cậy
  - Điểm bán
  - Lãi/Lỗ nếu bán ngay
  - Khuyến nghị
- Link đến phân tích chi tiết từng mã

---

## 🔧 Technical Details

### Class: `PortfolioManager`

**File:** `portfolio_manager.py`

**Methods chính:**

```python
# Thêm cổ phiếu
add_stock(symbol, quantity, buy_price, buy_date, notes)

# Xóa cổ phiếu
remove_stock(index)

# Lấy giá hiện tại
get_current_prices()

# Tính P&L
calculate_pnl() -> DataFrame

# Tổng hợp danh mục
get_portfolio_summary() -> Dict

# Phân bổ theo %
get_portfolio_distribution() -> DataFrame

# Check tín hiệu bán
check_sell_signals() -> DataFrame
```

---

## 📊 Metrics được tính toán

### Portfolio Level:
- **Total Investment**: Tổng vốn đầu tư
- **Total Current Value**: Tổng giá trị hiện tại
- **Total P&L**: Tổng lãi/lỗ (VND)
- **Total ROI %**: Tỷ suất sinh lời tổng

### Stock Level:
- **Investment**: Số lượng × Giá mua
- **Current Value**: Số lượng × Giá hiện tại
- **P&L**: Current Value - Investment
- **ROI %**: (P&L / Investment) × 100
- **Allocation %**: (Current Value / Total Value) × 100

---

## ⚠️ Lưu ý quan trọng

1. **Dữ liệu lưu local**: Portfolio được lưu ở `portfolios/*.json`
2. **Không có authentication thật**: User chỉ cần chọn từ dropdown
3. **Giá real-time**: Lấy từ API (có thể bị delay)
4. **Tín hiệu kỹ thuật**: Chỉ là công cụ hỗ trợ, không phải lời khuyên đầu tư

---

## 🔮 Future Enhancements

Các tính năng có thể thêm sau:

- [ ] Stop Loss / Take Profit tự động
- [ ] Lịch sử giao dịch (Transaction History)
- [ ] So sánh hiệu suất với VNINDEX
- [ ] Dividend tracking
- [ ] Export portfolio sang Excel/CSV
- [ ] Email alerts khi có tín hiệu bán
- [ ] Multi-portfolio (nhiều danh mục cho 1 user)
- [ ] Authentication thật (username + password)

---

## 📝 Example Usage

```python
from portfolio_manager import PortfolioManager

# Khởi tạo
pm = PortfolioManager("user1")

# Thêm cổ phiếu
pm.add_stock("VCB", 100, 85.5, "2025-01-15", "Ngân hàng lớn")
pm.add_stock("VHM", 50, 45.2, "2025-02-10")

# Xem P&L
pnl_df = pm.calculate_pnl()
print(pnl_df)

# Tổng hợp
summary = pm.get_portfolio_summary()
print(f"Tổng lãi/lỗ: {summary['total_pnl']:,.0f} VND")
print(f"ROI: {summary['total_pnl_pct']:.2f}%")

# Check tín hiệu bán
sell_signals = pm.check_sell_signals()
if not sell_signals.empty:
    print("⚠️ Có tín hiệu bán!")
    print(sell_signals)
```

---

Made with ❤️ for Vietnamese Stock Investors
