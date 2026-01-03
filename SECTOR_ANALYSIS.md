# Hướng dẫn Phân tích Ngành (Sector Analysis)

## 📋 Tổng quan

Tính năng phân tích ngành giúp bạn xác định **nhóm ngành nào đang mạnh, nhóm ngành nào đang yếu** trên thị trường chứng khoán Việt Nam. Điều này rất quan trọng vì:

- **Xu hướng ngành** thường ảnh hưởng đến tất cả các cổ phiếu trong ngành đó
- Đầu tư vào **ngành mạnh** tăng xác suất thành công
- Tránh **ngành yếu** giúp bảo toàn vốn
- Xác định **thời điểm phù hợp** để chuyển đổi danh mục đầu tư

---

## 🏭 Danh sách 12 Nhóm Ngành Phân Tích

### 1. Ngân hàng
**Mã cổ phiếu:** ACB, MBB, TCB, VCB, VPB, CTG, BID, STB, HDB

**Đặc điểm:** Nhóm có vốn hóa lớn, ảnh hưởng mạnh đến VNINDEX

### 2. Chứng khoán
**Mã cổ phiếu:** SSI, VCI, VND, HCM, FTS, SHS

**Đặc điểm:** Biến động theo thanh khoản thị trường

### 3. Bất động sản
**Mã cổ phiếu:** VHM, VIC, NVL, DXG, KDH, DIG, PDR

**Đặc điểm:** Chu kỳ dài, phụ thuộc chính sách và lãi suất

### 4. Bán lẻ
**Mã cổ phiếu:** MWG, FRT, PNJ, DGW

**Đặc điểm:** Phụ thuộc vào sức mua và tiêu dùng nội địa

### 5. Thép
**Mã cổ phiếu:** HPG, HSG, NKG, TLH

**Đặc điểm:** Theo chu kỳ kinh tế, ảnh hưởng bởi giá nguyên liệu

### 6. Dầu khí
**Mã cổ phiếu:** PVD, PVS, PVT, BSR, PLX

**Đặc điểm:** Phụ thuộc giá dầu thế giới

### 7. Điện
**Mã cổ phiếu:** POW, NT2, PC1, REE

**Đặc điểm:** Ổn định, cổ tức cao

### 8. Vận tải & Logistics
**Mã cổ phiếu:** GMD, HVN, VJC, VTP

**Đặc điểm:** Phục hồi sau đại dịch

### 9. Thực phẩm & Đồ uống
**Mã cổ phiếu:** VNM, SAB, MSN, MCH, VHC

**Đặc điểm:** Phòng thủ tốt, cổ tức ổn định

### 10. Dược phẩm
**Mã cổ phiếu:** DHG, DMC, DVN, IMP

**Đặc điểm:** Tăng trưởng ổn định, nhu cầu bền vững

### 11. Công nghệ
**Mã cổ phiếu:** FPT, CMG, VGI

**Đặc điểm:** Tiềm năng tăng trưởng cao

### 12. Xây dựng
**Mã cổ phiếu:** CTD, HBC, VCG, LCG

**Đặc điểm:** Chu kỳ theo đầu tư công và bất động sản

---

## 📊 Cách Tính Điểm Ngành (Sector Score)

### Quy trình phân tích:

1. **Lấy dữ liệu:** Thu thập dữ liệu lịch sử của tất cả cổ phiếu trong ngành (mặc định 90 ngày)

2. **Phân tích từng cổ phiếu:** Mỗi cổ phiếu được đánh giá dựa trên 5 tiêu chí (tổng 100 điểm):

   **a) RSI (20 điểm)**
   - RSI 40-60: 20 điểm (trung lập tốt)
   - RSI 30-40: 15 điểm (tích cực)
   - RSI < 30: 10 điểm (quá bán)
   - RSI 60-70: 15 điểm (mạnh)
   - RSI > 70: 5 điểm (quá mua)

   **b) MACD (20 điểm)**
   - MACD > Signal: 20 điểm (tích cực)
   - MACD ≈ Signal (90%): 10 điểm (trung lập)
   - MACD < Signal: 0 điểm (tiêu cực)

   **c) MA Crossover (20 điểm)**
   - MA20 > MA50: 20 điểm (xu hướng tăng)
   - MA20 ≈ MA50 (98%): 10 điểm (trung lập)
   - MA20 < MA50: 0 điểm (xu hướng giảm)

   **d) Xu hướng giá 20 ngày (20 điểm)**
   - Tăng > 5%: 20 điểm
   - Tăng 0-5%: 15 điểm
   - Giảm 0-5%: 10 điểm
   - Giảm > 5%: 5 điểm

   **e) Volume (20 điểm)**
   - Volume 20 ngày > 120% Volume 50 ngày: 20 điểm (tăng mạnh)
   - Volume 20 ngày > Volume 50 ngày: 15 điểm (tăng)
   - Còn lại: 10 điểm (bình thường)

3. **Tính điểm trung bình ngành:**
   ```
   Điểm ngành = Trung bình điểm của tất cả cổ phiếu trong ngành
   ```

4. **Xếp hạng trạng thái:**
   - **MẠNH:** Điểm ≥ 70
   - **TRUNG BÌNH:** Điểm 50-70
   - **YẾU:** Điểm < 50

---

## 💡 Cách Sử Dụng Phân Tích Ngành

### Chiến lược 1: Chọn ngành trước, chọn cổ phiếu sau

```
Bước 1: Xác định các ngành MẠNH (điểm ≥ 70)
Bước 2: Trong các ngành mạnh, tìm cổ phiếu có tín hiệu MUA
Bước 3: Đầu tư vào các cổ phiếu này với tỷ trọng phù hợp
```

**Ví dụ:**
- Ngành Ngân hàng đang MẠNH (75 điểm)
- Trong ngành, TCB và MBB có tín hiệu MUA MẠNH
- → Ưu tiên mua TCB và MBB

### Chiến lược 2: Tránh ngành yếu

```
Nếu đang nắm giữ cổ phiếu trong ngành YẾU:
- Cân nhắc bán hoặc giảm tỷ trọng
- Chuyển vốn sang ngành mạnh hơn
```

**Ví dụ:**
- Ngành Bất động sản đang YẾU (45 điểm)
- Bạn đang nắm VHM
- → Cân nhắc bán VHM, chuyển sang ngành khác

### Chiến lược 3: Kết hợp với VNINDEX

| VNINDEX | Ngành | Khuyến nghị |
|---------|-------|-------------|
| TỐT | MẠNH | ✅ MUA MẠNH - Cơ hội rất tốt |
| TỐT | TRUNG BÌNH | ✅ MUA (thận trọng) |
| TỐT | YẾU | ⚠️ CHỜ - Ngành chưa theo kịp |
| TRUNG BÌNH | MẠNH | ✅ MUA - Ngành tốt hơn thị trường |
| TRUNG BÌNH | TRUNG BÌNH | ⏸️ CHỜ - Quan sát thêm |
| TRUNG BÌNH | YẾU | ⛔ TRÁNH |
| YẾU | MẠNH | 🟡 CHỜ - Ngành tốt nhưng thị trường yếu |
| YẾU | TRUNG BÌNH | ⛔ KHÔNG MUA |
| YẾU | YẾU | 🔴 BÁN - Bảo vệ vốn |

---

## 📈 Ví dụ Thực Tế

### Ví dụ 1: Thị trường tích cực

**Tình huống:**
```
VNINDEX: TỐT (72%)
Ngành Ngân hàng: MẠNH (78 điểm)
  - TCB: 85 điểm
  - MBB: 80 điểm
  - VCB: 75 điểm
```

**Quyết định:**
✅ Đây là cơ hội tốt để mua cổ phiếu ngân hàng
- Ưu tiên: TCB > MBB > VCB
- Tỷ trọng đề xuất: 60-80% vốn

### Ví dụ 2: Thị trường yếu

**Tình huống:**
```
VNINDEX: YẾU (45%)
Ngành Bất động sản: YẾU (42 điểm)
  - VHM: 40 điểm
  - VIC: 38 điểm
  - NVL: 45 điểm
```

**Quyết định:**
🔴 Không nên mua, nếu đang nắm giữ thì cần:
- Bán ngay nếu lỗ > 7%
- Giảm tỷ trọng xuống 30-50% nếu đang lãi
- Chờ thị trường phục hồi

### Ví dụ 3: Thị trường hỗn hợp

**Tình huống:**
```
VNINDEX: TRUNG BÌNH (62%)
Ngành Thực phẩm: MẠNH (73 điểm)
Ngành Bất động sản: YẾU (48 điểm)
```

**Quyết định:**
📊 Lựa chọn ngành cẩn thận:
- ✅ Mua cổ phiếu thực phẩm (VNM, SAB)
- ⛔ Tránh bất động sản
- 🎯 Tỷ trọng: 40-60% vốn

---

## ⚙️ Sử Dụng Trong Ứng Dụng

### 1. Giao diện Web (Streamlit)

```python
# Chọn chế độ "🏭 Phân tích ngành"
# Điều chỉnh số ngày phân tích (30-180 ngày)
# Nhấn "📊 Phân tích ngành"
```

**Kết quả hiển thị:**
- Tổng quan: Số ngành mạnh/trung bình/yếu
- Bảng xếp hạng 12 ngành
- Chi tiết TOP 3 ngành mạnh nhất
- Khuyến nghị đầu tư cụ thể

### 2. Console (main.py)

```python
from sector_analyzer import SectorAnalyzer

# Khởi tạo analyzer
analyzer = SectorAnalyzer(days_back=90)

# Phân tích tất cả ngành
analyzer.analyze_all_sectors()

# In tóm tắt
analyzer.print_summary()
```

### 3. Tích hợp trong phân tích cổ phiếu

Khi phân tích một cổ phiếu cụ thể, hệ thống **tự động phân tích ngành** của cổ phiếu đó:

```python
analyzer = StockAnalyzer('VCB', check_sector=True)
result = analyzer.analyze()
# Sẽ tự động phân tích ngành Ngân hàng
```

**Hiển thị:**
```
🏭 NGÀNH: Ngân hàng
   Trạng thái: MẠNH (78 điểm)
   Khuyến nghị ngành: NÊN MUA
```

---

## 🎯 Các Trường Hợp Đặc Biệt

### Trường hợp 1: Cổ phiếu tốt nhưng ngành yếu

**Tình huống:** VHM có tín hiệu MUA MẠNH nhưng ngành Bất động sản YẾU

**Khuyến nghị:**
- ⚠️ Có thể mua nhưng **giảm tỷ trọng xuống 50-70%**
- 🎯 Đặt stop-loss chặt chẽ hơn (5% thay vì 7%)
- 👀 Theo dõi sát để sẵn sàng thoát nếu ngành xấu đi

### Trường hợp 2: Cổ phiếu yếu nhưng ngành mạnh

**Tình huống:** TCB có tín hiệu BÁN nhưng ngành Ngân hàng MẠNH

**Khuyến nghị:**
- 🟡 **Giữ tiếp** nếu đang nắm giữ
- 🔄 Có thể chuyển sang cổ phiếu khác trong cùng ngành (MBB, VCB)
- ⏰ Chờ TCB phục hồi theo ngành

### Trường hợp 3: Ngành chuyển đổi xu hướng

**Dấu hiệu:** Ngành từ YẾU lên TRUNG BÌNH hoặc TRUNG BÌNH lên MẠNH

**Khuyến nghị:**
- 🚀 **Cơ hội tốt** để vào lệnh sớm
- 📈 Tăng tỷ trọng dần khi ngành xác nhận xu hướng
- 💡 Chọn cổ phiếu đầu ngành (vốn hóa lớn, thanh khoản cao)

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Thời gian phân tích

- **90 ngày (mặc định):** Cân bằng giữa xu hướng trung hạn và ngắn hạn
- **30-60 ngày:** Phù hợp với giao dịch ngắn hạn
- **120-180 ngày:** Phù hợp với đầu tư dài hạn

### 2. Độ tin cậy

- Phân tích ngành **chính xác hơn** khi có nhiều mã trong ngành
- Ngành có < 5 mã: Kết quả có thể không đại diện
- Luôn kết hợp với phân tích cổ phiếu cụ thể

### 3. Giới hạn

- ❌ Không dự đoán thời điểm đảo chiều chính xác
- ❌ Không thay thế phân tích cơ bản
- ❌ Không tính đến yếu tố vĩ mô, chính sách

### 4. Tần suất cập nhật

- **Nên phân tích lại:** 1-2 tuần/lần
- **Hoặc khi:** Có sự kiện lớn ảnh hưởng đến ngành
- **Tránh:** Phân tích quá thường xuyên (gây nhiễu)

---

## 📚 Kết Luận

Phân tích ngành là **công cụ mạnh mẽ** giúp:

✅ **Tăng xác suất thành công:** Chọn đúng ngành = 50% thành công

✅ **Giảm rủi ro:** Tránh ngành yếu giúp bảo toàn vốn

✅ **Tối ưu danh mục:** Phân bổ vốn vào ngành phù hợp

✅ **Xác định thời điểm:** Biết khi nào nên vào/ra khỏi một ngành

**Nhớ rằng:** Phân tích ngành là một phần trong quy trình đầu tư toàn diện. Hãy kết hợp với:
- Phân tích VNINDEX
- Phân tích kỹ thuật cổ phiếu
- Quản lý vốn và rủi ro
- Phân tích cơ bản (nếu có thể)

---

*Chúc bạn đầu tư thành công! 🚀*
