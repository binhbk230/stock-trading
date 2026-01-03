"""
Script phân tích chi tiết VNINDEX với tất cả các chỉ báo kỹ thuật
"""
from vnindex_analyzer import VNIndexAnalyzer
import pandas as pd
from datetime import datetime

def print_detailed_analysis():
    """In ra phân tích chi tiết VNINDEX"""
    print("\n" + "="*100)
    print("🔍 PHÂN TÍCH CHI TIẾT CHỈ SỐ VNINDEX (DAILY)")
    print("="*100)
    
    # Khởi tạo analyzer với interval 1D để có đủ dữ liệu cho MA200 và BB
    analyzer = VNIndexAnalyzer(interval='1D')
    
    print("\n📥 Đang tải dữ liệu VNINDEX...")
    data = analyzer.fetch_data()
    
    if data is None or data.empty:
        print("❌ Không thể tải dữ liệu VNINDEX")
        return
    
    print(f"✅ Đã tải {len(data)} điểm dữ liệu")
    
    # Tính toán indicators
    print("\n🔢 Đang tính toán các chỉ báo kỹ thuật...")
    df = analyzer.calculate_indicators()
    
    # Lấy dữ liệu mới nhất
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    print("\n" + "="*100)
    print("📊 THÔNG TIN GIÁ HIỆN TẠI")
    print("="*100)
    
    price_change = latest['close'] - prev['close']
    price_change_pct = (price_change / prev['close']) * 100 if prev['close'] > 0 else 0
    
    print(f"\n💹 Giá đóng cửa:        {latest['close']:.2f}")
    print(f"📈 Giá mở cửa:         {latest['open']:.2f}")
    print(f"⬆️  Giá cao nhất:       {latest['high']:.2f}")
    print(f"⬇️  Giá thấp nhất:      {latest['low']:.2f}")
    print(f"📊 Khối lượng:         {latest['volume']:,.0f}")
    
    change_icon = "🟢" if price_change >= 0 else "🔴"
    print(f"{change_icon} Thay đổi:          {price_change:+.2f} ({price_change_pct:+.2f}%)")
    
    # Phần RSI
    print("\n" + "="*100)
    print("📈 CHỈ SỐ RSI (Relative Strength Index)")
    print("="*100)
    if 'rsi' in df.columns and not pd.isna(latest['rsi']):
        rsi = latest['rsi']
        print(f"\n🎯 RSI:                {rsi:.2f}")
        
        if rsi > 70:
            print(f"   ⚠️  CẢNH BÁO: RSI > 70 - Thị trường QUÁ MUA")
            print(f"   💡 Giải thích: RSI {rsi:.1f} cho thấy thị trường đang quá nóng")
            print(f"      Rủi ro điều chỉnh cao, không nên mua vào lúc này")
        elif rsi > 65:
            print(f"   ⚠️  CHÚ Ý: RSI đang ở mức cao")
            print(f"   💡 Giải thích: RSI {rsi:.1f} gần vùng quá mua, cần thận trọng")
        elif rsi > 35:
            print(f"   ✅ TỐT: RSI ở vùng cân bằng")
            print(f"   💡 Giải thích: RSI {rsi:.1f} cho thấy thị trường ổn định")
        elif rsi > 30:
            print(f"   ⚠️  CHÚ Ý: RSI đang ở mức thấp")
            print(f"   💡 Giải thích: RSI {rsi:.1f} gần vùng quá bán")
        else:
            print(f"   ⚠️  CẢNH BÁO: RSI < 30 - Thị trường QUÁ BÁN")
            print(f"   💡 Giải thích: RSI {rsi:.1f} cho thấy thị trường quá lạnh")
    
    # Phần MACD
    print("\n" + "="*100)
    print("📉 CHỈ SỐ MACD (Moving Average Convergence Divergence)")
    print("="*100)
    if 'macd' in df.columns and not pd.isna(latest['macd']):
        macd = latest['macd']
        macd_signal = latest.get('macd_signal', 0)
        macd_hist = latest.get('macd_hist', 0)
        
        print(f"\n🎯 MACD:               {macd:.2f}")
        print(f"📊 Signal:             {macd_signal:.2f}")
        print(f"📊 Histogram:          {macd_hist:.2f}")
        
        if macd > macd_signal:
            trend_icon = "🟢"
            trend = "TĂNG"
            strength = "MẠNH" if macd > 0 else "YẾU"
            print(f"\n   {trend_icon} Tín hiệu: MACD đang XU HƯỚNG {trend} {strength}")
            if macd > 0:
                print(f"   💡 Giải thích: MACD > 0 và > Signal - Xu hướng tăng mạnh")
            else:
                print(f"   💡 Giải thích: MACD < 0 nhưng > Signal - Xu hướng phục hồi")
        else:
            trend_icon = "🔴"
            trend = "GIẢM"
            strength = "MẠNH" if macd < 0 else "YẾU"
            print(f"\n   {trend_icon} Tín hiệu: MACD đang XU HƯỚNG {trend} {strength}")
            if macd < 0:
                print(f"   💡 Giải thích: MACD < 0 và < Signal - Xu hướng giảm mạnh")
            else:
                print(f"   💡 Giải thích: MACD > 0 nhưng < Signal - Xu hướng suy yếu")
    
    # Phần Moving Averages
    print("\n" + "="*100)
    print("📊 ĐƯỜNG TRUNG BÌNH ĐỘNG (Moving Averages)")
    print("="*100)
    
    current_price = latest['close']
    ma_data = []
    
    for ma_name, period in [('sma_20', 20), ('sma_50', 50), ('sma_200', 200)]:
        if ma_name in df.columns and not pd.isna(latest[ma_name]):
            ma_value = latest[ma_name]
            diff = current_price - ma_value
            diff_pct = (diff / ma_value) * 100
            position = "TRÊN" if diff > 0 else "DƯỚI"
            icon = "🟢" if diff > 0 else "🔴"
            
            ma_data.append({
                'name': f'MA{period}',
                'value': ma_value,
                'diff': diff,
                'diff_pct': diff_pct,
                'position': position,
                'icon': icon
            })
    
    if ma_data:
        print(f"\n💹 Giá hiện tại: {current_price:.2f}\n")
        for ma in ma_data:
            print(f"{ma['icon']} {ma['name']:<8} {ma['value']:>8.2f}  |  Giá {ma['position']:<4} {abs(ma['diff']):>6.2f} điểm ({ma['diff_pct']:>+6.2f}%)")
        
        above_count = sum(1 for ma in ma_data if ma['position'] == "TRÊN")
        total_count = len(ma_data)
        
        print(f"\n📊 Tổng quan: Giá TRÊN {above_count}/{total_count} đường MA")
        if above_count == total_count:
            print(f"   ✅ XU HƯỚNG TĂNG MẠNH - Giá trên tất cả các đường MA")
        elif above_count >= total_count / 2:
            print(f"   ⚠️  XU HƯỚNG TĂNG YẾU - Giá trên một số đường MA")
        else:
            print(f"   ❌ XU HƯỚNG GIẢM - Giá dưới hầu hết các đường MA")
    
    # Phần Bollinger Bands
    print("\n" + "="*100)
    print("📊 BOLLINGER BANDS")
    print("="*100)
    
    if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
        bb_upper = latest['bb_upper']
        bb_lower = latest['bb_lower']
        bb_middle = latest['bb_middle']
        
        if not pd.isna(bb_upper) and not pd.isna(bb_lower):
            bb_width = bb_upper - bb_lower
            bb_position = (current_price - bb_lower) / bb_width if bb_width > 0 else 0.5
            
            print(f"\n📈 BB Upper:           {bb_upper:.2f}")
            print(f"📊 BB Middle:          {bb_middle:.2f}")
            print(f"📉 BB Lower:           {bb_lower:.2f}")
            print(f"💹 Giá hiện tại:       {current_price:.2f}")
            print(f"📊 Vị trí trong band:  {bb_position*100:.1f}%")
            
            if bb_position > 0.8:
                print(f"\n   🔴 CẢNH BÁO: Giá gần BB Upper - Có thể quá mua")
                print(f"   💡 Giải thích: Giá ở {bb_position*100:.0f}% trong band, gần biên trên")
            elif bb_position > 0.5:
                print(f"\n   🟢 TỐT: Giá trên BB Middle")
                print(f"   💡 Giải thích: Giá ở {bb_position*100:.0f}% trong band, xu hướng tích cực")
            elif bb_position > 0.2:
                print(f"\n   ⚠️  CHÚ Ý: Giá dưới BB Middle")
                print(f"   💡 Giải thích: Giá ở {bb_position*100:.0f}% trong band, xu hướng yếu")
            else:
                print(f"\n   🟢 CƠ HỘI: Giá gần BB Lower - Có thể quá bán")
                print(f"   💡 Giải thích: Giá ở {bb_position*100:.0f}% trong band, gần biên dưới")
    
    # Phần Volume
    print("\n" + "="*100)
    print("📊 KHỐI LƯỢNG GIAO DỊCH (Volume)")
    print("="*100)
    
    if len(df) >= 20:
        current_volume = latest['volume']
        avg_volume_20 = df['volume'].iloc[-20:].mean()
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
        
        print(f"\n📊 Volume hiện tại:    {current_volume:,.0f}")
        print(f"📊 Volume TB 20 phiên: {avg_volume_20:,.0f}")
        print(f"📊 Tỷ lệ:              {volume_ratio:.2f}x")
        
        if volume_ratio > 1.5:
            print(f"\n   🔥 RẤT CAO: Khối lượng giao dịch tăng mạnh {volume_ratio:.1f}x")
            print(f"   💡 Giải thích: Thị trường đang rất sôi động, nhiều người tham gia")
        elif volume_ratio > 1.0:
            print(f"\n   ✅ TỐT: Khối lượng cao hơn trung bình {volume_ratio:.1f}x")
            print(f"   💡 Giải thích: Thanh khoản tốt, thị trường hoạt động ổn định")
        elif volume_ratio > 0.7:
            print(f"\n   ⚠️  TRUNG BÌNH: Khối lượng ở mức bình thường {volume_ratio:.1f}x")
            print(f"   💡 Giải thích: Thanh khoản chấp nhận được")
        else:
            print(f"\n   ❌ THẤP: Khối lượng thấp hơn trung bình {volume_ratio:.1f}x")
            print(f"   💡 Giải thích: Thanh khoản yếu, ít người tham gia thị trường")
    
    # Xu hướng giá
    print("\n" + "="*100)
    print("📈 XU HƯỚNG GIÁ (Price Trend)")
    print("="*100)
    
    if len(df) >= 5:
        recent_prices = df['close'].iloc[-5:].values
        print(f"\n📊 5 phiên gần nhất:")
        for i, price in enumerate(recent_prices, 1):
            change = ""
            if i > 1:
                prev_price = recent_prices[i-2]
                diff = price - prev_price
                change = f"  ({diff:+.2f})" if diff != 0 else ""
            print(f"   {i}. {price:.2f}{change}")
        
        # Tính hệ số xu hướng
        import numpy as np
        coefficients = np.polyfit(range(5), recent_prices, 1)
        trend_slope = coefficients[0]
        
        if trend_slope > 5:
            print(f"\n   🟢 XU HƯỚNG TĂNG MẠNH: +{trend_slope:.2f} điểm/phiên")
        elif trend_slope > 0:
            print(f"\n   🟢 XU HƯỚNG TĂNG NHẸ: +{trend_slope:.2f} điểm/phiên")
        elif trend_slope > -5:
            print(f"\n   🔴 XU HƯỚNG GIẢM NHẸ: {trend_slope:.2f} điểm/phiên")
        else:
            print(f"\n   🔴 XU HƯỚNG GIẢM MẠNH: {trend_slope:.2f} điểm/phiên")
    
    # Phân tích tổng quan
    print("\n" + "="*100)
    print("🎯 PHÂN TÍCH TỔNG QUAN & KHUYẾN NGHỊ")
    print("="*100)
    
    summary = analyzer.get_summary()
    
    print(f"\n📊 Tình trạng:         {summary['status']}")
    print(f"📈 Điểm số:            {summary['score']}/100 ({summary['percentage']:.1f}%)")
    print(f"⏰ Dữ liệu:            {summary.get('data_date', 'N/A')}")
    if summary.get('data_age_warning'):
        print(f"⚠️  Cảnh báo:          {summary['data_age_warning']}")
    
    print(f"\n💡 KHUYẾN NGHỊ:")
    print(f"   {summary['recommendation']}")
    
    print(f"\n📋 CHI TIẾT ĐÁNH GIÁ:")
    for condition in summary['conditions']:
        print(f"   {condition}")
    
    print("\n" + "="*100)
    print("✅ HOÀN THÀNH PHÂN TÍCH CHI TIẾT")
    print("="*100 + "\n")


if __name__ == "__main__":
    print_detailed_analysis()
