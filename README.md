# 📈 Công cụ Gợi ý Mua Bán Cổ Phiếu Việt Nam

Công cụ phân tích kỹ thuật và đưa ra tín hiệu gợi ý mua/bán cổ phiếu trên thị trường chứng khoán Việt Nam dựa trên nhiều chỉ báo kỹ thuật, **tích hợp phân tích chỉ số VNINDEX** để đưa ra quyết định thông minh hơn.

## 🎯 Tính năng

### ⭐ Tính năng mới: Phân tích VNINDEX
- ✅ Phân tích tình trạng thị trường qua chỉ số VNINDEX
- ✅ Đánh giá xu hướng tổng thể (TỐT/TRUNG BÌNH/YẾU)
- ✅ **CHỈ gợi ý MUA khi VNINDEX ở trạng thái tốt**
- ✅ Cảnh báo khi thị trường yếu để bảo toàn vốn
- ✅ **Khuyến nghị riêng cho người đang nắm giữ cổ phiếu**

### 💼 Tính năng khuyến nghị kép (Mới!)
Hệ thống cung cấp **2 loại khuyến nghị riêng biệt**:

1. **Cho người chưa mua**: Có nên vào lệnh không?
2. **Cho người đang nắm giữ**: Giữ, bán hay mua thêm?

Ví dụ:
```
💡 CHƯA MUA → Cân nhắc MUA (thận trọng)
💼 ĐANG NẮM GIỮ → GIỮ TIẾP nhưng KHÔNG MUA THÊM
```

### Các tính năng phân tích
- ✅ Tải dữ liệu lịch sử giá cổ phiếu từ thị trường Việt Nam (sử dụng vnstock)
- ✅ Tính toán các chỉ báo kỹ thuật phổ biến:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Moving Averages (SMA, EMA)
  - Bollinger Bands
  - Stochastic Oscillator
  - Volume Analysis
  - Support/Resistance Levels
  
- ✅ Phân tích tín hiệu từ mỗi chỉ báo
- ✅ Tổng hợp tín hiệu tổng thể (MUA/BÁN/CHỜ)
- ✅ Báo cáo chi tiết với độ tin cậy và khuyến nghị
- ✅ Giao diện web Streamlit đẹp mắt và dễ sử dụng

## 📊 Logic phân tích VNINDEX

Hệ thống đánh giá VNINDEX dựa trên 6 tiêu chí:
1. **RSI** - Chỉ số sức mạnh tương đối
2. **MACD** - Xu hướng tăng/giảm
3. **Moving Averages** - Vị trí giá so với các đường MA
4. **Xu hướng giá** - Phân tích 5 phiên gần nhất
5. **Volume** - Khối lượng giao dịch
6. **Bollinger Bands** - Vị trí trong band

### Ngưỡng quyết định:
- **≥ 70%**: VNINDEX TỐT → Cho phép gợi ý MUA
- **50-70%**: VNINDEX TRUNG BÌNH → Gợi ý MUA nhưng thận trọng  
- **< 50%**: VNINDEX YẾU → **KHÔNG** gợi ý MUA (CHỜ)

## 📋 Yêu cầu

- Python 3.8 trở lên
- Các thư viện được liệt kê trong `requirements.txt`

## 🚀 Cài đặt

1. Clone hoặc tải project về máy

2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## 💻 Cách sử dụng

### 1. Giao diện Web (Khuyến nghị) 🌐

Chạy ứng dụng Streamlit:

```bash
streamlit run app.py
```

Sau đó truy cập: http://localhost:8501

**Tính năng giao diện:**
- 📊 Hiển thị tình trạng VNINDEX ngay đầu trang
- 🎯 Phân tích đơn lẻ: Phân tích chi tiết 1 mã cổ phiếu
- 📈 Phân tích hàng loạt: Quét nhiều mã cùng lúc
- 🔍 Quét thị trường: Tìm cơ hội trong top 100
- 📉 Biểu đồ tương tác với Plotly
- ⚠️ Cảnh báo VNINDEX tự động

### 2. Sử dụng script chính

Chạy file `main.py` và làm theo hướng dẫn:

```bash
python main.py
```

### 3. Test phân tích VNINDEX

```bash
python test_vnindex.py
```

### 4. Sử dụng như thư viện

```python
from main import StockAnalyzer
from vnindex_analyzer import VNIndexAnalyzer

# Phân tích VNINDEX trước
vnindex = VNIndexAnalyzer()
vnindex_result = vnindex.print_report()

if vnindex_result['allow_buy']:
    # Chỉ phân tích cổ phiếu khi VNINDEX tốt
    analyzer = StockAnalyzer('VNM', check_vnindex=True)
    result = analyzer.run()
else:
    print("⚠️ VNINDEX yếu, không nên mua!")
```

### 5. Tắt kiểm tra VNINDEX (không khuyến nghị)

```python
# Nếu muốn phân tích mà không quan tâm VNINDEX
analyzer = StockAnalyzer('VNM', check_vnindex=False)
result = analyzer.run()
```

### 6. Ví dụ tùy chỉnh thời gian

```python
from main import StockAnalyzer

# Phân tích từ ngày cụ thể (có VNINDEX)
analyzer = StockAnalyzer(
    symbol='VCB',
    start_date='2024-01-01',
    end_date='2024-12-23',
    check_vnindex=True
)
)
result = analyzer.run()
```

## 📊 Hiểu kết quả phân tích

### Tín hiệu tổng hợp

- **MUA MẠNH** (🟢): Nhiều chỉ báo cho tín hiệu mua, độ tin cậy > 60%
- **MUA** (🟢): Tín hiệu mua nhẹ, cân nhắc trước khi vào lệnh
- **BÁN MẠNH** (🔴): Nhiều chỉ báo cho tín hiệu bán, nên thoát vị thế
- **BÁN** (🔴): Tín hiệu bán nhẹ, cân nhắc giảm tỷ trọng
- **NEUTRAL** (⚪): Không có tín hiệu rõ ràng, nên chờ

### Độ tin cậy

- **80-100%**: Tín hiệu rất mạnh
- **60-80%**: Tín hiệu tốt
- **50-60%**: Tín hiệu trung bình
- **< 50%**: Tín hiệu yếu hoặc trung lập

### Các chỉ báo

#### RSI (Relative Strength Index)
- < 30: Quá bán → Tín hiệu MUA
- > 70: Quá mua → Tín hiệu BÁN
- 30-70: Trung lập

#### MACD
- MACD cắt lên Signal → Tín hiệu MUA
- MACD cắt xuống Signal → Tín hiệu BÁN

#### Moving Averages
- Giá trên MA → Xu hướng tăng
- Giá dưới MA → Xu hướng giảm

#### Bollinger Bands
- Giá chạm dải dưới → Tín hiệu MUA
- Giá chạm dải trên → Tín hiệu BÁN

#### Stochastic Oscillator
- %K, %D < 20: Quá bán → Tín hiệu MUA
- %K, %D > 80: Quá mua → Tín hiệu BÁN
- %K cắt lên %D → Tín hiệu MUA

## 📁 Cấu trúc Project

```
stock-tradding/
├── main.py                    # File chính, chạy phân tích
├── technical_indicators.py    # Module tính các chỉ báo kỹ thuật
├── signal_generator.py        # Module sinh tín hiệu mua/bán
├── requirements.txt           # Danh sách thư viện cần thiết
└── README.md                  # File hướng dẫn này
```

## ⚠️ Lưu ý quan trọng

1. **Không phải lời khuyên đầu tư**: Công cụ này chỉ mang tính chất tham khảo, phân tích kỹ thuật. KHÔNG phải lời khuyên đầu tư tài chính.

2. **Tự nghiên cứu**: Luôn tự nghiên cứu kỹ và hiểu rõ cổ phiếu trước khi đưa ra quyết định.

3. **Quản lý rủi ro**: Luôn đặt stop-loss và không bỏ tất cả vốn vào một cổ phiếu.

4. **Phân tích kỹ thuật có giới hạn**: Kết hợp với phân tích cơ bản và tin tức thị trường.

5. **Dữ liệu có thể trễ**: Dữ liệu từ vnstock có thể bị trễ hoặc không chính xác 100%.

## 🔧 Khắc phục sự cố

### Lỗi khi cài đặt thư viện

Nếu gặp lỗi khi cài `ta` hoặc các thư viện khác:

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Không lấy được dữ liệu

- Kiểm tra kết nối Internet
- Đảm bảo mã cổ phiếu đúng (viết hoa, không dấu)
- Thử lại sau vài phút (API có thể bị giới hạn)

### Lỗi thiếu module

```bash
pip install pandas numpy vnstock ta matplotlib requests openpyxl
```

## 🎨 Tùy chỉnh

### Thay đổi ngưỡng chỉ báo

Trong file `signal_generator.py`, bạn có thể tùy chỉnh các ngưỡng:

```python
# RSI
def analyze_rsi(self, oversold=30, overbought=70):
    # Thay đổi 30 và 70 theo ý muốn

# Stochastic
def analyze_stochastic(self, oversold=20, overbought=80):
    # Thay đổi 20 và 80 theo ý muốn
```

### Thêm chỉ báo mới

Thêm phương thức mới trong `TechnicalIndicators` và tương ứng trong `SignalGenerator`.

## 📚 Tài liệu tham khảo

- [vnstock Documentation](https://vnstock.site/)
- [Technical Analysis Library](https://technical-analysis-library-in-python.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🤝 Đóng góp

Mọi đóng góp, báo lỗi, đề xuất tính năng đều được hoan nghênh!

## 📄 License

MIT License - Tự do sử dụng cho mục đích cá nhân và học tập.

## 👨‍💻 Tác giả

Công cụ phân tích kỹ thuật cổ phiếu Việt Nam

---

**Chúc bạn đầu tư thành công! 📈💰**

*Remember: Trade what you see, not what you think!*
