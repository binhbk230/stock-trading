"""
Script so sánh điểm VNINDEX giữa các interval khác nhau
Giải thích tại sao điểm chênh lệch
"""
from vnindex_analyzer import VNIndexAnalyzer
from datetime import datetime
import pandas as pd

def compare_intervals():
    """So sánh điểm VNINDEX giữa các interval"""
    print("\n" + "="*100)
    print("🔍 SO SÁNH ĐIỂM VNINDEX GIỮA CÁC INTERVAL")
    print("="*100)
    
    intervals = ['15m', '30m', '1H', '1D']
    results = []
    
    for interval in intervals:
        print(f"\n{'='*100}")
        print(f"📊 Đang phân tích interval: {interval}")
        print("="*100)
        
        try:
            analyzer = VNIndexAnalyzer(interval=interval)
            data = analyzer.fetch_data()
            
            if data is None or data.empty:
                print(f"❌ Không có dữ liệu cho {interval}")
                continue
            
            # Tính indicators
            df = analyzer.calculate_indicators()
            
            # Lấy summary
            summary = analyzer.get_summary()
            
            # Lấy các chỉ báo chi tiết
            latest = df.iloc[-1]
            
            result = {
                'interval': interval,
                'data_points': len(df),
                'status': summary['status'],
                'score': summary['score'],
                'percentage': summary['percentage'],
                'price': summary['current_price'],
                'rsi': latest.get('rsi', None),
                'macd': latest.get('macd', None),
                'macd_signal': latest.get('macd_signal', None),
                'sma_20': latest.get('sma_20', None),
                'sma_50': latest.get('sma_50', None),
                'sma_200': latest.get('sma_200', None),
                'conditions': summary['conditions']
            }
            
            results.append(result)
            
            # In thông tin
            print(f"\n📊 Số điểm dữ liệu: {result['data_points']}")
            print(f"🎯 Tình trạng: {result['status']}")
            print(f"📈 Điểm số: {result['score']}/100 ({result['percentage']:.1f}%)")
            print(f"💹 Giá: {result['price']:.2f}")
            
            if result['rsi']:
                print(f"📊 RSI: {result['rsi']:.2f}")
            if result['macd'] is not None:
                print(f"📊 MACD: {result['macd']:.2f}")
            
            print(f"\n📋 Chi tiết đánh giá:")
            for cond in result['conditions']:
                print(f"   {cond}")
                
        except Exception as e:
            print(f"❌ Lỗi với {interval}: {e}")
    
    # So sánh tổng quan
    print("\n" + "="*100)
    print("📊 BẢNG SO SÁNH TỔNG QUAN")
    print("="*100)
    
    if results:
        # Tạo bảng so sánh
        print(f"\n{'Interval':<10} {'Điểm dữ liệu':<15} {'Trạng thái':<15} {'Điểm':<15} {'RSI':<10} {'Giá':<12}")
        print("-"*100)
        
        for r in results:
            rsi_str = f"{r['rsi']:.2f}" if r['rsi'] else "N/A"
            print(f"{r['interval']:<10} {r['data_points']:<15} {r['status']:<15} {r['score']:<6}/100 ({r['percentage']:>5.1f}%)  {rsi_str:<10} {r['price']:<12.2f}")
    
    # Giải thích sự khác biệt
    print("\n" + "="*100)
    print("💡 GIẢI THÍCH SỰ CHÊNH LỆCH ĐIỂM")
    print("="*100)
    
    print("""
    🔍 TẠI SAO ĐIỂM KHÁC NHAU GIỮA CÁC INTERVAL?
    
    1️⃣ KHUNG THỜI GIAN KHÁC NHAU:
       • 15m: Mỗi "phiên" là 15 phút
       • 1D: Mỗi "phiên" là 1 ngày
       ➡️ "5 phiên gần nhất" có nghĩa khác nhau:
          - 15m: 5 x 15 phút = 75 phút (1.25 giờ)
          - 1D: 5 ngày = 1 tuần
    
    2️⃣ SỐ LƯỢNG DỮ LIỆU:
       • 15m: ~1,728 điểm (11 ngày)
       • 1D: ~131 điểm (6 tháng)
       ➡️ MA200 không tồn tại với 15m (chỉ có 1,728 điểm)
    
    3️⃣ RSI KHÁC NHAU:
       • RSI được tính trên 14 kỳ
       • 15m: RSI dựa trên 14 x 15 phút = 3.5 giờ
       • 1D: RSI dựa trên 14 ngày = 2 tuần
       ➡️ RSI phản ánh xu hướng trong timeframe khác nhau
    
    4️⃣ MACD KHÁC NHAU:
       • MACD = EMA(12) - EMA(26)
       • 15m: MACD dựa trên 12-26 phiên 15 phút (3-6.5 giờ)
       • 1D: MACD dựa trên 12-26 ngày (2-4 tuần)
       ➡️ MACD phản ánh momentum trong timeframe khác nhau
    
    5️⃣ VOLUME RATIO:
       • Tính theo trung bình 20 phiên
       • 15m: So với trung bình 20 phiên 15 phút (5 giờ)
       • 1D: So với trung bình 20 ngày (1 tháng)
       ➡️ Volume "cao" hay "thấp" có nghĩa khác nhau
    
    6️⃣ XU HƯỚNG GIÁ:
       • Xu hướng 5 phiên
       • 15m: Xu hướng trong 75 phút (rất ngắn hạn)
       • 1D: Xu hướng trong 5 ngày (ngắn - trung hạn)
       ➡️ Có thể tăng trong ngày nhưng giảm trong tuần
    
    📌 KẾT LUẬN:
    ✅ Interval NGẮN (15m, 30m, 1H):
       - Phản ánh biến động NGẮN HẠN
       - Nhạy cảm với tin tức, sự kiện trong ngày
       - Phù hợp cho TRADING, SCALPING
       - Dễ bị nhiễu, dao động mạnh
    
    ✅ Interval DÀI (1D):
       - Phản ánh xu hướng TRUNG-DÀI HẠN
       - Ổn định hơn, ít nhiễu
       - Phù hợp cho ĐẦU TƯ, SWING TRADING
       - Có đầy đủ các chỉ báo (MA200, BB)
    
    🎯 KHUYẾN NGHỊ:
    • Sử dụng 1D để đánh giá xu hướng TỔNG THỂ thị trường
    • Sử dụng 15m/1H để tìm điểm VÀO/RA cụ thể trong ngày
    • KHÔNG so sánh trực tiếp điểm giữa các interval
    """)
    
    print("\n" + "="*100)
    print("✅ HOÀN THÀNH SO SÁNH")
    print("="*100 + "\n")


if __name__ == "__main__":
    compare_intervals()
