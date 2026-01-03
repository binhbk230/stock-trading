"""
Demo phân tích cổ phiếu với tích hợp VNINDEX
"""
from main import StockAnalyzer
from vnindex_analyzer import VNIndexAnalyzer

def demo_with_vnindex():
    """Demo phân tích có tích hợp VNINDEX"""
    print("\n" + "="*80)
    print("DEMO: PHÂN TÍCH CỔ PHIẾU VỚI VNINDEX")
    print("="*80)
    
    # 1. Phân tích VNINDEX trước
    print("\n1️⃣ Bước 1: Kiểm tra tình trạng thị trường (VNINDEX)")
    print("-" * 80)
    vnindex = VNIndexAnalyzer(interval='1D')  # Sử dụng interval 1D mặc định
    vnindex.fetch_data()
    vnindex_status = vnindex.get_summary()
    
    print(f"\n📊 VNINDEX: {vnindex_status['status']} ({vnindex_status['percentage']:.0f}%)")
    print(f"💹 Giá: {vnindex_status['current_price']:.2f}")
    print(f"💡 {vnindex_status['recommendation']}")
    
    # 2. Phân tích cổ phiếu
    print("\n\n2️⃣ Bước 2: Phân tích cổ phiếu")
    print("-" * 80)
    
    # Ví dụ với VNM
    stock_symbol = "VNM"
    print(f"\n🔍 Phân tích {stock_symbol}...")
    
    analyzer = StockAnalyzer(stock_symbol, check_vnindex=True)
    result = analyzer.run()
    
    # 3. Kết quả
    print("\n\n3️⃣ Kết quả:")
    print("-" * 80)
    
    if result:
        signal = result['signal']
        confidence = result['confidence']
        
        print(f"\n🎯 Tín hiệu: {signal}")
        print(f"📊 Độ tin cậy: {confidence:.1f}%")
        
        if result.get('vnindex_warning'):
            print(f"\n⚠️  {result['vnindex_warning']}")
        
        # Giải thích
        print("\n\n💡 GIẢI THÍCH:")
        if 'CHỜ - VNINDEX YẾU' in signal:
            print("""
   ⛔ Hệ thống KHÔNG khuyến nghị mua vì:
   - VNINDEX đang yếu
   - Thị trường chung có xu hướng giảm
   - Rủi ro cao trong giai đoạn này
   
   👉 Nên chờ VNINDEX phục hồi trước khi vào lệnh mới
            """)
        elif 'MUA (THẬN TRỌNG)' in signal:
            print("""
   ⚠️  Có thể cân nhắc mua nhưng:
   - VNINDEX chỉ ở mức TRUNG BÌNH
   - Nên giảm tỷ lệ vốn đầu tư
   - Đặt stop-loss chặt chẽ
            """)
        elif 'MUA' in signal:
            print("""
   ✅ Có thể mua vì:
   - VNINDEX ở trạng thái TỐT
   - Cổ phiếu có tín hiệu kỹ thuật tích cực
   - Thị trường đang hỗ trợ xu hướng tăng
   
   🎯 Lưu ý: Vẫn nên đặt stop-loss để quản lý rủi ro
            """)
    
    print("\n" + "="*80)
    print("KẾT THÚC DEMO")
    print("="*80 + "\n")


def demo_compare_stocks():
    """Demo so sánh nhiều cổ phiếu"""
    print("\n" + "="*80)
    print("DEMO: SO SÁNH NHIỀU CỔ PHIẾU")
    print("="*80)
    
    stocks = ['VNM', 'VCB', 'HPG']
    
    # Lấy VNINDEX một lần
    print("\n📊 Kiểm tra VNINDEX...")
    vnindex = VNIndexAnalyzer(interval='1D')  # Sử dụng interval 1D mặc định
    vnindex.fetch_data()
    vnindex_status = vnindex.get_summary()
    print(f"VNINDEX: {vnindex_status['status']} ({vnindex_status['percentage']:.0f}%)")
    
    print("\n" + "-"*80)
    print("Kết quả phân tích:")
    print("-"*80)
    
    results = []
    for symbol in stocks:
        print(f"\n🔍 {symbol}...", end=" ")
        try:
            analyzer = StockAnalyzer(symbol, check_vnindex=True)
            if analyzer.fetch_data() is not None:
                analyzer.calculate_indicators()
                result = analyzer.analyze()
                
                results.append({
                    'symbol': symbol,
                    'signal': result['signal'],
                    'confidence': result['confidence'],
                    'vnindex_warning': result.get('vnindex_warning')
                })
                print(f"✓ {result['signal']} ({result['confidence']:.0f}%)")
            else:
                print("✗ Lỗi")
        except Exception as e:
            print(f"✗ Lỗi: {e}")
    
    # Tổng kết
    print("\n" + "="*80)
    print("TỔNG KẾT")
    print("="*80)
    
    for r in results:
        icon = "🟢" if "MUA" in r['signal'] else "🔴" if "BÁN" in r['signal'] else "🟡"
        print(f"\n{icon} {r['symbol']}: {r['signal']} ({r['confidence']:.0f}%)")
        if r['vnindex_warning']:
            print(f"   ⚠️  {r['vnindex_warning']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  DEMO HỆ THỐNG PHÂN TÍCH CỔ PHIẾU VỚI VNINDEX              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("\nChọn demo:")
    print("1. Phân tích chi tiết 1 cổ phiếu (có VNINDEX)")
    print("2. So sánh nhiều cổ phiếu")
    
    choice = input("\nLựa chọn (1 hoặc 2): ").strip()
    
    if choice == "1":
        demo_with_vnindex()
    elif choice == "2":
        demo_compare_stocks()
    else:
        print("⚠️ Lựa chọn không hợp lệ!")
