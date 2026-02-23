"""
Module phân tích chỉ số VNINDEX
Đánh giá xu hướng thị trường để quyết định có nên mua cổ phiếu hay không
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from vnstock import Vnstock
from src.core.technical_indicators import TechnicalIndicators


class VNIndexAnalyzer:
    """Lớp phân tích chỉ số VNINDEX"""
    
    def __init__(self, start_date=None, end_date=None, interval='1D'):
        """
        Khởi tạo công cụ phân tích VNINDEX
        
        Args:
            start_date: Ngày bắt đầu (mặc định 6 tháng trước)
            end_date: Ngày kết thúc (mặc định hôm nay)
            interval: Khung thời gian ('1D', '1H', '30m', '15m')
        """
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date
        
        if start_date is None:
            # Nếu interval ngắn, chỉ lấy dữ liệu gần đây hơn
            if interval in ['15m', '30m', '1H']:
                start = datetime.now() - timedelta(days=7)  # 1 tuần cho intraday
            else:
                start = datetime.now() - timedelta(days=180)  # 6 tháng cho daily
            self.start_date = start.strftime('%Y-%m-%d')
        else:
            self.start_date = start_date
        
        self.interval = interval
        self.data = None
        self.indicators = None
        self.last_update = None
        self.last_fetch_time = None
    
    def fetch_data(self, force_refresh=False):
        """
        Lấy dữ liệu lịch sử VNINDEX
        
        Args:
            force_refresh: Bắt buộc tải lại dữ liệu (bỏ qua cache)
        
        Returns:
            DataFrame chứa dữ liệu
        """
        try:
            # Kiểm tra cache (chỉ tải lại nếu chưa có hoặc force_refresh)
            if not force_refresh and self.data is not None and self.last_fetch_time is not None:
                # Nếu interval ngắn, cache 5 phút
                # Nếu interval dài (1D), cache 1 giờ
                cache_duration = timedelta(minutes=5) if self.interval in ['15m', '30m', '1H'] else timedelta(hours=1)
                if datetime.now() - self.last_fetch_time < cache_duration:
                    print(f"💾 Sử dụng dữ liệu cache ({self.interval})")
                    return self.data
            
            # Sử dụng vnstock để lấy dữ liệu VNINDEX (chỉ số thị trường)
            # VNINDEX là chỉ số, không phải cổ phiếu, nên cần xử lý khác
            stock = Vnstock().stock(symbol='VNINDEX', source='VCI')
            
            # Danh sách interval để thử (ưu tiên interval được yêu cầu)
            intervals_to_try = [self.interval]
            
            # Nếu interval ngắn không được, fallback về daily
            if self.interval in ['15m', '30m', '1H']:
                intervals_to_try.extend(['1H', '1D'])
            
            df = None
            used_interval = None
            
            # Thử lấy dữ liệu với các interval
            for interval in intervals_to_try:
                try:
                    print(f"📊 Đang thử lấy VNINDEX với interval {interval}...")
                    df = stock.quote.history(
                        start=self.start_date,
                        end=self.end_date,
                        interval=interval
                    )
                    if df is not None and not df.empty:
                        used_interval = interval
                        if interval != self.interval:
                            print(f"⚠️ Không hỗ trợ {self.interval}, sử dụng {interval}")
                        break
                except Exception as e:
                    print(f"⚠️ Thất bại với interval {interval}: {e}")
                    continue
            
            # Nếu tất cả đều thất bại, thử với VN30
            if df is None or df.empty:
                print("⚠️ Không thể lấy VNINDEX, thử VN30 làm proxy...")
                stock = Vnstock().stock(symbol='VN30', source='VCI')
                df = stock.quote.history(
                    start=self.start_date,
                    end=self.end_date,
                    interval='1D'
                )
                used_interval = '1D'
            
            if df is None or df.empty:
                raise ValueError("Không có dữ liệu VNINDEX")
            
            # Chuẩn hóa tên cột
            df.columns = df.columns.str.lower()
            
            # Đảm bảo có đủ các cột cần thiết
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Dữ liệu VNINDEX thiếu các cột: {missing_columns}")
            
            # Lấy thời gian của dữ liệu mới nhất
            try:
                # Nếu có cột 'time', dùng nó
                if 'time' in df.columns:
                    last_time = df['time'].iloc[-1]
                    if isinstance(last_time, str):
                        parsed_time = pd.to_datetime(last_time)
                        # Force timezone-naive để tránh conflict giữa server và local
                        if hasattr(parsed_time, 'tz_localize'):
                            self.last_update = parsed_time.tz_localize(None) if parsed_time.tzinfo else parsed_time
                        else:
                            self.last_update = parsed_time.replace(tzinfo=None) if hasattr(parsed_time, 'tzinfo') and parsed_time.tzinfo else parsed_time
                    else:
                        self.last_update = last_time
                # Nếu index là datetime
                elif hasattr(df.index, 'max') and hasattr(df.index.max(), 'strftime'):
                    self.last_update = df.index.max()
                else:
                    # Fallback: dùng ngày hiện tại
                    self.last_update = datetime.now()
                
                # Ensure timezone-naive datetime (double-check)
                if hasattr(self.last_update, 'tzinfo') and self.last_update.tzinfo is not None:
                    self.last_update = self.last_update.replace(tzinfo=None)
                elif hasattr(self.last_update, 'tz_localize'):
                    try:
                        self.last_update = self.last_update.tz_localize(None)
                    except:
                        pass
                    
            except Exception as e:
                # Nếu không parse được, dùng datetime hiện tại
                print(f"⚠️ Không thể xác định thời gian dữ liệu: {e}")
                self.last_update = datetime.now()
            
            self.data = df
            self.last_fetch_time = datetime.now()
            self.interval = used_interval if used_interval else self.interval
            
            # Hiển thị thông tin dữ liệu
            try:
                # Ensure last_update is a datetime and handle timezone issues
                if self.last_update is not None:
                    # Convert to timezone-naive if needed
                    last_update_naive = self.last_update.replace(tzinfo=None) if hasattr(self.last_update, 'replace') else self.last_update
                    data_age = (datetime.now() - last_update_naive).total_seconds() / 60
                    
                    if data_age < 60:
                        print(f"✅ Dữ liệu VNINDEX ({used_interval or self.interval}): {len(df)} điểm, cập nhật {data_age:.0f} phút trước")
                    else:
                        hours_age = data_age / 60
                        print(f"✅ Dữ liệu VNINDEX ({used_interval or self.interval}): {len(df)} điểm, cập nhật {hours_age:.1f} giờ trước")
                else:
                    print(f"✅ Dữ liệu VNINDEX ({used_interval or self.interval}): {len(df)} điểm")
            except Exception as e:
                print(f"✅ Dữ liệu VNINDEX ({used_interval or self.interval}): {len(df)} điểm")
            
            return df
            
        except Exception as e:
            print(f"⚠️ Lỗi khi tải dữ liệu VNINDEX: {str(e)}")
            return None
    
    def refresh_data(self):
        """
        Làm mới dữ liệu VNINDEX (bắt buộc tải lại)
        Hữu ích để lấy dữ liệu mới nhất trong phiên
        
        Returns:
            DataFrame chứa dữ liệu mới
        """
        print("🔄 Đang làm mới dữ liệu VNINDEX...")
        # Cập nhật end_date về hiện tại
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        # Xóa indicators cũ
        self.indicators = None
        # Tải lại dữ liệu
        return self.fetch_data(force_refresh=True)
    
    def calculate_indicators(self):
        """
        Tính toán các chỉ báo kỹ thuật cho VNINDEX
        
        Returns:
            DataFrame với các chỉ báo
        """
        if self.data is None:
            raise ValueError("Chưa có dữ liệu VNINDEX")
        
        self.indicators = TechnicalIndicators(self.data)
        df_with_indicators = self.indicators.calculate_all()
        
        return df_with_indicators
    
    def analyze_trend(self):
        """
        Phân tích xu hướng của VNINDEX
        
        Returns:
            Dictionary chứa kết quả phân tích xu hướng
        """
        if self.indicators is None:
            self.calculate_indicators()
        
        df = self.indicators.df
        current_price = df['close'].iloc[-1]
        
        # Kiểm tra các điều kiện
        conditions = []
        score = 0
        
        # 1. RSI (30-70 là tốt, quá thấp hoặc quá cao là không tốt)
        if 'rsi' in df.columns and not pd.isna(df['rsi'].iloc[-1]):
            rsi = df['rsi'].iloc[-1]
            if 35 < rsi < 65:
                conditions.append(f"✅ RSI tốt ({rsi:.1f})")
                score += 20
            elif rsi < 30:
                conditions.append(f"⚠️ RSI quá bán ({rsi:.1f})")
                score -= 5  # Trừ điểm vì quá bán
            elif rsi > 70:
                conditions.append(f"❌ RSI quá mua ({rsi:.1f})")
                score -= 10  # Trừ điểm vì quá mua - nguy hiểm hơn
            else:
                conditions.append(f"⚠️ RSI trung bình ({rsi:.1f})")
                score += 5  # RSI 65-70 hoặc 30-35: trung lập nhẹ
        
        # 2. MACD - Xu hướng tăng
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            macd = df['macd'].iloc[-1]
            macd_signal = df['macd_signal'].iloc[-1]
            
            if not pd.isna(macd) and not pd.isna(macd_signal):
                if macd > macd_signal and macd > 0:
                    conditions.append("✅ MACD xu hướng tăng mạnh")
                    score += 25
                elif macd > macd_signal:
                    conditions.append("✅ MACD xu hướng tăng")
                    score += 15
                elif macd < macd_signal and macd < 0:
                    conditions.append("❌ MACD xu hướng giảm mạnh")
                    score -= 20  # Giảm mạnh = trừ điểm nhiều
                else:
                    conditions.append("⚠️ MACD xu hướng giảm")
                    score -= 10  # Giảm nhẹ = trừ ít
        
        # 3. Moving Averages - Giá trên các MA
        ma_above_count = 0
        ma_total = 0
        
        for ma_col in ['sma_20', 'sma_50', 'sma_200']:
            if ma_col in df.columns and not pd.isna(df[ma_col].iloc[-1]):
                ma_total += 1
                if current_price > df[ma_col].iloc[-1]:
                    ma_above_count += 1
        
        if ma_total > 0:
            ma_ratio = ma_above_count / ma_total
            if ma_ratio >= 0.66:
                conditions.append(f"✅ Giá trên {ma_above_count}/{ma_total} đường MA")
                score += 20
            elif ma_ratio >= 0.5:
                conditions.append(f"⚠️ Giá trên {ma_above_count}/{ma_total} đường MA")
                score += 10
            elif ma_ratio >= 0.33:
                conditions.append(f"⚠️ Giá dưới phần lớn đường MA")
                score -= 5
            else:
                conditions.append(f"❌ Giá dưới hầu hết đường MA")
                score -= 15  # Giá dưới hầu hết MA = xu hướng giảm mạnh
        
        # 4. Kiểm tra xu hướng giá (5 phiên gần nhất)
        if len(df) >= 5:
            recent_prices = df['close'].iloc[-5:].values
            price_trend = np.polyfit(range(5), recent_prices, 1)[0]
            
            if price_trend > 0:
                conditions.append("✅ Xu hướng giá 5 phiên tăng")
                score += 15
            else:
                # Kiểm tra xem có phải pullback trong xu hướng tăng không
                macd = df.get('macd', pd.Series([None])).iloc[-1]
                macd_signal = df.get('macd_signal', pd.Series([None])).iloc[-1]
                
                # Nếu MACD > 0 và đang tăng (macd > signal) → Chỉ là pullback, không trừ điểm
                if not pd.isna(macd) and not pd.isna(macd_signal) and macd > 0 and macd > macd_signal:
                    conditions.append("⚠️ Xu hướng giá 5 phiên giảm (pullback trong xu hướng tăng)")
                    # Không trừ điểm vì momentum vẫn tốt - pullback là cơ hội mua
                else:
                    # MACD yếu hoặc giảm → Xu hướng giảm thực sự
                    conditions.append("❌ Xu hướng giá 5 phiên giảm")
                    score -= 15  # Xu hướng giảm = trừ điểm
        
        # 5. Volume - Khối lượng giao dịch
        if len(df) >= 20:
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].iloc[-20:].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Kiểm tra xem có phải đang trong phiên giao dịch không (cho 1D)
            is_intraday = False
            if self.interval == '1D' and self.last_update:
                try:
                    from datetime import datetime, time
                    
                    # Lấy ngày và giờ hiện tại
                    now = datetime.now()
                    
                    # Lấy ngày của dữ liệu
                    if isinstance(self.last_update, str):
                        parsed = pd.to_datetime(self.last_update)
                        # Remove timezone nếu có
                        if hasattr(parsed, 'tz_localize'):
                            parsed = parsed.tz_localize(None) if parsed.tzinfo else parsed
                        elif hasattr(parsed, 'tzinfo') and parsed.tzinfo:
                            parsed = parsed.replace(tzinfo=None)
                        update_date = parsed.date()
                    else:
                        update_date = self.last_update.date()
                    
                    # Nếu dữ liệu là của hôm nay VÀ giờ hiện tại trong khung giao dịch
                    # → Đang trong phiên (dữ liệu chưa đủ)
                    market_open = time(9, 0)
                    market_close = time(15, 0)
                    
                    if update_date == now.date() and market_open <= now.time() < market_close:
                        is_intraday = True
                except Exception as e:
                    print(f"⚠️ Lỗi khi kiểm tra thời gian phiên: {e}")
                    is_intraday = False
            
            if is_intraday:
                # Trong phiên giao dịch, KHÔNG đánh giá volume (vì chưa đủ)
                conditions.append(f"⏰ Phiên chưa kết thúc ({now.strftime('%H:%M')}) - Volume tạm thời {volume_ratio:.1f}x")
                # Không cộng, không trừ điểm
            else:
                # Sau giờ giao dịch hoặc dữ liệu ngày hôm trước, đánh giá bình thường
                if volume_ratio > 1.2:
                    conditions.append(f"✅ Khối lượng cao ({volume_ratio:.1f}x)")
                    score += 10
                elif volume_ratio > 0.8:
                    conditions.append(f"✅ Khối lượng ổn định ({volume_ratio:.1f}x)")
                    score += 5
                elif volume_ratio > 0.5:
                    conditions.append(f"⚠️ Khối lượng thấp ({volume_ratio:.1f}x)")
                    # Không cộng, không trừ
                else:
                    conditions.append(f"❌ Khối lượng rất thấp ({volume_ratio:.1f}x)")
                    score -= 5  # Volume quá thấp = thiếu thanh khoản
        
        # 6. Bollinger Bands - Vị trí trong band
        if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
            bb_upper = df['bb_upper'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            bb_middle = df['bb_middle'].iloc[-1]
            
            if not any(pd.isna([bb_upper, bb_lower, bb_middle])):
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
                
                if bb_position > 0.7:
                    conditions.append(f"✅ Giá gần BB Upper ({bb_position*100:.0f}%)")
                    score += 10
                elif bb_position > 0.5:
                    conditions.append(f"✅ Giá trên BB Middle ({bb_position*100:.0f}%)")
                    score += 5
                elif bb_position > 0.3:
                    conditions.append(f"⚠️ Giá dưới BB Middle ({bb_position*100:.0f}%)")
                    score -= 5
                else:
                    conditions.append(f"❌ Giá gần BB Lower ({bb_position*100:.0f}%)")
                    score -= 10
        
        # Đánh giá tổng thể
        max_score = 100
        percentage = (score / max_score) * 100
        
        if percentage >= 70:
            status = "TỐT"
            recommendation = "✅ Thị trường tích cực, phù hợp để tìm cơ hội MUA"
            allow_buy = True
        elif percentage >= 50:
            status = "TRUNG BÌNH"
            recommendation = "⚠️ Thị trường trung lập, nên thận trọng khi MUA"
            allow_buy = True  # Vẫn cho phép nhưng với cảnh báo
        else:
            status = "YẾU"
            recommendation = "❌ Thị trường yếu, KHÔNG NÊN MUA mới, ưu tiên bảo toàn vốn"
            allow_buy = False
        
        return {
            'status': status,
            'score': score,
            'percentage': percentage,
            'recommendation': recommendation,
            'allow_buy': allow_buy,
            'conditions': conditions,
            'current_price': current_price,
            'data': df
        }
    
    def get_summary(self):
        """
        Lấy tóm tắt tình trạng VNINDEX
        
        Returns:
            Dictionary chứa thông tin tóm tắt
        """
        try:
            if self.data is None:
                self.fetch_data()
            
            result = self.analyze_trend()
            
            # Kiểm tra xem dữ liệu có phải hôm nay không
            data_date = None
            is_today = False
            data_age_warning = None
            
            if self.last_update is not None:
                try:
                    if isinstance(self.last_update, str):
                        data_date = self.last_update
                        data_datetime = pd.to_datetime(self.last_update)
                        # Remove timezone nếu có
                        if hasattr(data_datetime, 'tz_localize'):
                            data_datetime = data_datetime.tz_localize(None) if data_datetime.tzinfo else data_datetime
                        elif hasattr(data_datetime, 'tzinfo') and data_datetime.tzinfo:
                            data_datetime = data_datetime.replace(tzinfo=None)
                    else:
                        data_datetime = self.last_update
                        # Format hiển thị dựa trên interval
                        if self.interval in ['15m', '30m', '1H']:
                            data_date = self.last_update.strftime('%Y-%m-%d %H:%M')
                        else:
                            data_date = self.last_update.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"⚠️ Lỗi khi format thời gian: {e}")
                    data_datetime = None
                    data_date = None
                
                if data_datetime is not None:
                    today = datetime.now().strftime('%Y-%m-%d')
                    is_today = (data_datetime.strftime('%Y-%m-%d') == today)
                    
                    # Tính độ cũ của dữ liệu
                    try:
                        data_datetime_naive = data_datetime.replace(tzinfo=None) if hasattr(data_datetime, 'replace') else data_datetime
                        data_age_minutes = (datetime.now() - data_datetime_naive).total_seconds() / 60
                        
                        if self.interval in ['15m', '30m', '1H']:
                            # Với intraday, cảnh báo nếu cũ hơn 30 phút
                            if data_age_minutes < 15:
                                data_age_warning = f"🟢 Dữ liệu mới ({data_age_minutes:.0f} phút trước)"
                            elif data_age_minutes < 60:
                                data_age_warning = f"🟡 Dữ liệu {data_age_minutes:.0f} phút trước"
                            else:
                                hours = data_age_minutes / 60
                                data_age_warning = f"🔴 Dữ liệu {hours:.1f} giờ trước (cũ)"
                        else:
                            # Với daily, cảnh báo theo ngày
                            if not is_today:
                                try:
                                    days_ago = (datetime.now() - data_datetime.replace(tzinfo=None)).days
                                    if days_ago == 1:
                                        data_age_warning = "⏰ Dữ liệu từ ngày hôm qua (chưa có phiên hôm nay)"
                                    elif days_ago > 1:
                                        data_age_warning = f"⏰ Dữ liệu từ {days_ago} ngày trước (cũ)"
                                except:
                                    data_age_warning = f"⏰ Dữ liệu từ ngày {data_date}"
                    except Exception as e:
                        print(f"⚠️ Lỗi khi tính độ cũ của dữ liệu: {e}")
                        data_age_warning = None
            
            return {
                'status': result['status'],
                'score': result['score'],
                'percentage': result['percentage'],
                'recommendation': result['recommendation'],
                'allow_buy': result['allow_buy'],
                'current_price': result['current_price'],
                'conditions': result['conditions'],
                'data_date': data_date,
                'is_today': is_today,
                'data_age_warning': data_age_warning,
                'interval': self.interval
            }
            
        except Exception as e:
            print(f"⚠️ Lỗi khi phân tích VNINDEX: {str(e)}")
            # Trả về kết quả mặc định nếu có lỗi
            return {
                'status': 'UNKNOWN',
                'score': 50,
                'percentage': 50,
                'recommendation': '⚠️ Không thể phân tích VNINDEX, hãy thận trọng',
                'allow_buy': True,  # Vẫn cho phép nếu không lấy được dữ liệu
                'current_price': None,
                'conditions': ['⚠️ Không thể lấy dữ liệu VNINDEX']
            }
    
    def print_report(self):
        """
        In báo cáo phân tích VNINDEX
        """
        # Đảm bảo đã có dữ liệu
        if self.data is None:
            self.fetch_data()
            
        result = self.analyze_trend()
        
        print("\n" + "="*80)
        print("📊 PHÂN TÍCH CHỈ SỐ VNINDEX")
        print("="*80)
        
        # Hiển thị thời gian dữ liệu
        if self.last_update is not None:
            try:
                if isinstance(self.last_update, str):
                    data_date_str = self.last_update
                else:
                    data_date_str = self.last_update.strftime('%Y-%m-%d %H:%M:%S') if hasattr(self.last_update, 'strftime') else str(self.last_update)
                
                today = datetime.now().strftime('%Y-%m-%d')
                is_today = data_date_str.startswith(today)
                
                if is_today:
                    print(f"⏰ Thời gian dữ liệu: {data_date_str} ✅ (Hôm nay)")
                else:
                    print(f"⏰ Thời gian dữ liệu: {data_date_str} ⚠️ (Không phải hôm nay)")
                    print("   💡 Lưu ý: Dữ liệu chỉ cập nhật sau khi thị trường đóng cửa (15h)")
            except Exception as e:
                print(f"⏰ Thời gian dữ liệu: Không xác định")
                print(f"   ⚠️ Lỗi khi hiển thị thời gian: {e}")
        else:
            print(f"⏰ Thời gian dữ liệu: Không xác định")
        
        print(f"\n🎯 TÌNH TRẠNG: {result['status']}")
        print(f"📈 Điểm số: {result['score']:.0f}/100 ({result['percentage']:.1f}%)")
        print(f"💹 Giá hiện tại: {result['current_price']:.2f}")
        
        print(f"\n📋 CÁC CHỈ TIÊU:")
        for condition in result['conditions']:
            print(f"   {condition}")
        
        print(f"\n💡 KHUYẾN NGHỊ:")
        print(f"   {result['recommendation']}")
        
        print("\n" + "="*80 + "\n")
        
        return result


def main():
    """Hàm test"""
    print("🔍 PHÂN TÍCH CHỈ SỐ VNINDEX (DAILY)")
    print("="*80)
    
    analyzer = VNIndexAnalyzer(interval='1D')  # Mặc định 1D
    result = analyzer.print_report()
    
    print(f"\nCho phép mua: {result['allow_buy']}")


if __name__ == "__main__":
    main()
