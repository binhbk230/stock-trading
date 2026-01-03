"""
Công cụ gợi ý mua bán cổ phiếu Việt Nam
Dựa trên phân tích kỹ thuật và tín hiệu
"""
import pandas as pd
from datetime import datetime, timedelta
from vnstock import Vnstock
from src.core.technical_indicators import TechnicalIndicators
from src.core.signal_generator import SignalGenerator


class StockAnalyzer:
    """Lớp phân tích và gợi ý giao dịch cổ phiếu"""
    
    def __init__(self, symbol, start_date=None, end_date=None, check_vnindex=True, check_sector=True):
        """
        Khởi tạo công cụ phân tích
        
        Args:
            symbol: Mã cổ phiếu (VD: 'VNM', 'VCB', 'HPG')
            start_date: Ngày bắt đầu (mặc định 6 tháng trước)
            end_date: Ngày kết thúc (mặc định hôm nay)
            check_vnindex: Có kiểm tra VNINDEX hay không (mặc định True)
            check_sector: Có phân tích ngành hay không (mặc định True)
        """
        self.symbol = symbol.upper()
        self.check_vnindex = check_vnindex
        self.check_sector = check_sector
        
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date
        
        if start_date is None:
            start = datetime.now() - timedelta(days=180)
            self.start_date = start.strftime('%Y-%m-%d')
        else:
            self.start_date = start_date
        
        self.data = None
        self.indicators = None
        self.signal_gen = None
        self.vnindex_analyzer = None
        self.vnindex_status = None
        self.sector_analyzer = None
        self.sector_info = None
    
    def fetch_data(self):
        """
        Lấy dữ liệu lịch sử giá cổ phiếu
        
        Returns:
            DataFrame chứa dữ liệu
        """
        print(f"Đang tải dữ liệu {self.symbol}...")
        try:
            # Sử dụng vnstock 3.x API
            stock = Vnstock().stock(symbol=self.symbol, source='VCI')
            df = stock.quote.history(
                start=self.start_date,
                end=self.end_date,
                interval='1D'
            )
            
            if df is None or df.empty:
                raise ValueError(f"Không có dữ liệu cho mã {self.symbol}")
            
            # Chuẩn hóa tên cột
            df.columns = df.columns.str.lower()
            
            # Đảm bảo có đủ các cột cần thiết
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Dữ liệu thiếu các cột: {missing_columns}")
            
            self.data = df
            print(f"✓ Đã tải {len(df)} ngày giao dịch")
            return df
            
        except Exception as e:
            print(f"✗ Lỗi khi tải dữ liệu: {str(e)}")
            return None
    
    def calculate_indicators(self):
        """
        Tính toán các chỉ báo kỹ thuật
        
        Returns:
            DataFrame với các chỉ báo
        """
        if self.data is None:
            raise ValueError("Chưa có dữ liệu. Vui lòng gọi fetch_data() trước.")
        
        print("\nĐang tính toán các chỉ báo kỹ thuật...")
        self.indicators = TechnicalIndicators(self.data)
        df_with_indicators = self.indicators.calculate_all()
        print("✓ Đã tính toán tất cả các chỉ báo")
        
        return df_with_indicators
    
    def analyze(self):
        """
        Phân tích và tạo tín hiệu giao dịch
        
        Returns:
            Dictionary chứa kết quả phân tích
        """
        if self.indicators is None:
            self.calculate_indicators()
        
        # Phân tích VNINDEX nếu được yêu cầu
        if self.check_vnindex:
            print("\nĐang phân tích VNINDEX (1D)...")
            try:
                # Lazy import to avoid circular dependency
                from src.analyzers.vnindex_analyzer import VNIndexAnalyzer
                self.vnindex_analyzer = VNIndexAnalyzer(
                    start_date=self.start_date,
                    end_date=self.end_date,
                    interval='1D'  # Sử dụng interval 1D mặc định
                )
                self.vnindex_analyzer.fetch_data()
                self.vnindex_status = self.vnindex_analyzer.get_summary()
                print(f"✓ VNINDEX: {self.vnindex_status['status']} ({self.vnindex_status['percentage']:.0f}%)")
            except Exception as e:
                print(f"⚠️ Không thể phân tích VNINDEX: {str(e)}")
                self.vnindex_status = None
        
        # Phân tích ngành nếu được yêu cầu
        if self.check_sector:
            print("\nĐang phân tích ngành của cổ phiếu...")
            try:
                # Lazy import to avoid circular dependency
                from src.analyzers.sector_analyzer import SectorAnalyzer
                self.sector_analyzer = SectorAnalyzer(days_back=90)
                # Tìm ngành của cổ phiếu
                found_sector = None
                for sector_name, symbols in self.sector_analyzer.SECTORS.items():
                    if self.symbol in symbols:
                        found_sector = sector_name
                        break
                
                if found_sector:
                    sector_result = self.sector_analyzer.analyze_sector(found_sector, 
                                                                         self.sector_analyzer.SECTORS[found_sector])
                    self.sector_info = {
                        'name': found_sector,
                        'score': sector_result['score'],
                        'status': sector_result['status'],
                        'recommendation': sector_result['recommendation']
                    }
                    print(f"✓ Ngành {found_sector}: {sector_result['status']} ({sector_result['score']:.0f} điểm)")
                else:
                    print(f"⚠️ Không tìm thấy ngành của {self.symbol}")
                    self.sector_info = None
            except Exception as e:
                print(f"⚠️ Không thể phân tích ngành: {str(e)}")
                self.sector_info = None
        
        print("\nĐang phân tích tín hiệu...")
        self.signal_gen = SignalGenerator(self.indicators.df, self.vnindex_status, symbol=self.symbol)
        overall_signal = self.signal_gen.get_overall_signal()
        print("✓ Đã hoàn thành phân tích")
        
        return overall_signal
    
    def print_report(self, analysis_result):
        """
        In báo cáo phân tích
        
        Args:
            analysis_result: Kết quả từ phương thức analyze()
        """
        print("\n" + "="*80)
        print(f"BÁO CÁO PHÂN TÍCH KỸ THUẬT: {self.symbol}")
        print("="*80)
        
        # Hiển thị thông tin VNINDEX nếu có
        if self.vnindex_status:
            print(f"\n📊 VNINDEX:")
            print(f"   Tình trạng: {self.vnindex_status['status']} ({self.vnindex_status['percentage']:.0f}%)")
            print(f"   Giá hiện tại: {self.vnindex_status['current_price']:.2f}")
            if self.vnindex_status['conditions']:
                print(f"   Điều kiện:")
                for condition in self.vnindex_status['conditions'][:3]:  # Hiển thị 3 điều kiện đầu
                    print(f"      {condition}")
            print(f"   {self.vnindex_status['recommendation']}")
        
        # Hiển thị thông tin ngành nếu có
        if self.sector_info:
            print(f"\n🏭 NGÀNH: {self.sector_info['name']}")
            print(f"   Trạng thái: {self.sector_info['status']} ({self.sector_info['score']:.0f} điểm)")
            print(f"   Khuyến nghị ngành: {self.sector_info['recommendation']}")
        
        # Hiển thị điểm ngành từ signal generator nếu có
        if 'sector' in analysis_result:
            sector = analysis_result['sector']
            print(f"\n🎯 ĐIỂM NGÀNH (So sánh trong ngành):")
            print(f"   Ngành: {sector['sector']}")
            print(f"   Điểm: {sector['score']:.1f}/100 - {sector['status']}")
            print(f"   Phân tích: {sector['reason']}")
        
        # Thông tin giá hiện tại
        current_price = self.data['close'].iloc[-1]
        prev_price = self.data['close'].iloc[-2]
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        print(f"\n📊 THÔNG TIN GIÁ:")
        print(f"   Giá hiện tại: {current_price:,.0f} VNĐ")
        print(f"   Thay đổi: {price_change:+,.0f} VNĐ ({price_change_pct:+.2f}%)")
        print(f"   Khối lượng: {self.data['volume'].iloc[-1]:,.0f}")
        
        # Tín hiệu tổng hợp
        print(f"\n🎯 TÍN HIỆU TỔNG HỢP:")
        signal = analysis_result['signal']
        confidence = analysis_result['confidence']
        
        # Màu sắc cho tín hiệu
        if 'MUA' in signal:
            signal_icon = "🟢"
        elif 'BÁN' in signal:
            signal_icon = "🔴"
        elif 'CHỜ' in signal:
            signal_icon = "🟡"
        else:
            signal_icon = "⚪"
        
        print(f"   {signal_icon} Tín hiệu: {signal}")
        
        # Hiển thị cảnh báo VNINDEX nếu có
        if analysis_result.get('vnindex_warning'):
            print(f"   {analysis_result['vnindex_warning']}")
        
        print(f"   📈 Độ tin cậy: {confidence:.1f}%")
        print(f"   📊 Điểm mua: {analysis_result['buy_score']:.0f}")
        print(f"   📉 Điểm bán: {analysis_result['sell_score']:.0f}")
        
        # Hiển thị các mức giá khuyến nghị
        if 'stop_loss' in analysis_result:
            print(f"\n💰 CÁC MỨC GIÁ KHUYẾN NGHỊ (từ giá hiện tại):")
            
            # Format giá theo bước giá sàn
            def price_fmt(p):
                if p < 10:
                    return f"{p:,.2f}"  # 2 chữ số thập phân cho giá < 10
                elif p < 50:
                    return f"{p:,.2f}"  # 2 chữ số thập phân cho giá 10-50
                else:
                    return f"{p:,.1f}"  # 1 chữ số thập phân cho giá >= 50
            
            print(f"   📍 Giá hiện tại: {price_fmt(analysis_result['current_price'])} VNĐ")
            
            if analysis_result.get('stop_loss'):
                loss_pct = ((analysis_result['stop_loss'] - current_price) / current_price) * 100
                print(f"   🛑 Cắt lỗ (Stop Loss): {price_fmt(analysis_result['stop_loss'])} VNĐ ({loss_pct:+.1f}%)")
            
            if analysis_result.get('take_profit_1'):
                tp1_pct = ((analysis_result['take_profit_1'] - current_price) / current_price) * 100
                print(f"   ✅ Chốt lời T1 (5%): {price_fmt(analysis_result['take_profit_1'])} VNĐ ({tp1_pct:+.1f}%)")
            
            if analysis_result.get('take_profit_2'):
                tp2_pct = ((analysis_result['take_profit_2'] - current_price) / current_price) * 100
                print(f"   ✅ Chốt lời T2 (10%): {price_fmt(analysis_result['take_profit_2'])} VNĐ ({tp2_pct:+.1f}%)")
            
            if analysis_result.get('take_profit_3'):
                tp3_pct = ((analysis_result['take_profit_3'] - current_price) / current_price) * 100
                print(f"   ✅ Chốt lời T3 (15%): {price_fmt(analysis_result['take_profit_3'])} VNĐ ({tp3_pct:+.1f}%)")
            
            if analysis_result.get('risk_reward_ratio'):
                print(f"   ⚖️  Tỷ lệ Risk/Reward: 1:{analysis_result['risk_reward_ratio']:.2f}")
        
        # Chi tiết các chỉ báo
        print(f"\n📋 CHI TIẾT CÁC CHỈ BÁO:")
        
        details = analysis_result['details']
        
        for indicator_name, indicator_data in details.items():
            signal_text = indicator_data['signal']
            score = indicator_data['score']
            reason = indicator_data['reason']
            
            if signal_text == 'MUA':
                icon = "✅"
            elif signal_text == 'BÁN':
                icon = "❌"
            else:
                icon = "➖"
            
            print(f"\n   {icon} {indicator_name.upper()}:")
            print(f"      Tín hiệu: {signal_text} (Điểm: {score:.0f})")
            print(f"      Lý do: {reason}")
        
        # Giá trị các chỉ báo quan trọng
        print(f"\n📈 CÁC CHỈ SỐ KỸ THUẬT:")
        latest = self.indicators.get_latest_values()
        
        if 'rsi' in latest:
            print(f"   RSI: {latest['rsi']:.2f}")
        if 'macd' in latest:
            print(f"   MACD: {latest['macd']:.2f}")
            print(f"   MACD Signal: {latest['macd_signal']:.2f}")
        if 'sma_20' in latest:
            print(f"   SMA(20): {latest['sma_20']:.2f}")
        if 'sma_50' in latest:
            print(f"   SMA(50): {latest['sma_50']:.2f}")
        if 'bb_upper' in latest and 'bb_lower' in latest:
            print(f"   Bollinger Bands: [{latest['bb_lower']:.2f}, {latest['bb_upper']:.2f}]")
        
        # Khuyến nghị
        print(f"\n💡 KHUYẾN NGHỊ CHO NGƯỜI CHƯA MUA:")
        
        # Cảnh báo nếu ngành yếu
        sector_warning = ""
        if self.sector_info and self.sector_info['status'] == 'YẾU':
            sector_warning = f"\n   ⚠️ CẢNH BÁO: Ngành {self.sector_info['name']} đang YẾU"
        
        if 'CHỜ - VNINDEX YẾU' in signal:
            print("   ⛔ KHÔNG NÊN MUA - VNINDEX đang yếu")
            if sector_warning:
                print(sector_warning)
            print("   🔒 Ưu tiên bảo toàn vốn trong giai đoạn này")
            print("   👀 Chờ thị trường phục hồi trước khi vào lệnh mới")
        elif 'MUA MẠNH' in signal:
            if self.sector_info and self.sector_info['status'] == 'YẾU':
                print(f"   ⚠️ Cổ phiếu có tín hiệu MUA MẠNH nhưng ngành {self.sector_info['name']} đang YẾU")
                print("   ✅ Có thể MUA nhưng giảm tỷ lệ vốn (50-70%)")
            else:
                print("   ✅ Khuyến nghị MUA với tỷ lệ vốn phù hợp")
            print("   🎯 Nên đặt lệnh stop-loss để quản lý rủi ro")
        elif 'MUA (THẬN TRỌNG)' in signal or 'MUA' in signal:
            if self.sector_info and self.sector_info['status'] == 'YẾU':
                print(f"   ⚠️ Ngành {self.sector_info['name']} đang YẾU - NÊN CHỜ")
                print("   🔒 Ưu tiên các ngành khác đang mạnh hơn")
            else:
                print("   ✅ Có thể cân nhắc MUA nhưng cần thận trọng")
                print("   ⚠️  Nên chờ thêm tín hiệu xác nhận")
            if self.vnindex_status and self.vnindex_status['status'] != 'TỐT':
                print("   📊 Lưu ý: Thị trường chung chưa thực sự tốt")
        elif 'BÁN' in signal:
            print("   ❌ KHÔNG nên mua trong giai đoạn này")
            print("   📊 Chờ tín hiệu tích cực hơn")
        elif 'CÂN NHẮC BÁN' in signal:
            print("   ⛔ KHÔNG NÊN MUA - Thị trường yếu")
            print("   ⏰ Chờ thị trường ổn định")
        else:
            print("   ⏸️  NÊN CHỜ - Chưa có tín hiệu rõ ràng")
            print("   👀 Theo dõi để tìm điểm vào/ra tốt hơn")
        
        # Khuyến nghị cho người đang nắm giữ
        print(f"\n💼 KHUYẾN NGHỊ CHO NGƯỜI ĐANG NẮM GIỮ:")
        
        # Thêm cảnh báo ngành cho người đang nắm giữ
        if 'CHỜ - VNINDEX YẾU' in signal or 'CÂN NHẮC BÁN' in signal:
            print("   🔴 CẦN XEM XÉT BÁN/CẮT LỖ")
            print("   ⚠️  VNINDEX yếu có thể kéo giá xuống")
            if self.sector_info and self.sector_info['status'] == 'YẾU':
                print(f"   🔴 CẢNH BÁO: Cả ngành {self.sector_info['name']} đang yếu - BÁN NHANH")
            print("   💰 Chốt lời nếu đang lãi, cắt lỗ nếu lỗ quá 5-7%")
            print("   📉 Ít nhất nên giảm tỷ trọng xuống 50%")
            if 'CÂN NHẮC BÁN' in signal:
                print("   ⏰ Theo dõi sát, nếu xấu hơn thì bán ngay")
        elif 'MUA MẠNH' in signal:
            print("   🟢 GIỮ TIẾP hoặc CÂN NHẮC MUA THÊM")
            if self.sector_info and self.sector_info['status'] == 'MẠNH':
                print(f"   ✅ Ngành {self.sector_info['name']} đang mạnh - Tín hiệu rất tích cực")
            print("   📈 Tín hiệu tích cực, có thể tăng tỷ trọng")
            print("   🎯 Di chuyển stop-loss lên để bảo vệ lợi nhuận")
            print("   💡 Nếu chưa full vốn, cân nhắc mua thêm")
        elif 'MUA (THẬN TRỌNG)' in signal or 'MUA' in signal:
            print("   🟡 GIỮ TIẾP nhưng KHÔNG NÊN MUA THÊM")
            if self.sector_info and self.sector_info['status'] == 'YẾU':
                print(f"   ⚠️ Ngành {self.sector_info['name']} yếu - Cân nhắc BÁN hoặc giảm tỷ trọng")
            print("   📊 Tín hiệu tích cực nhưng thị trường chưa thực sự tốt")
            print("   🎯 Đặt stop-loss chặt chẽ")
            print("   ⚠️  Sẵn sàng bán nếu có dấu hiệu xấu đi")
        elif 'BÁN MẠNH' in signal:
            print("   🔴 NÊN BÁN/CHỐT LỜI NGAY")
            print("   ⚠️  Tín hiệu bán mạnh, rủi ro giảm giá cao")
            if self.sector_info and self.sector_info['status'] == 'YẾU':
                print(f"   🔴 Ngành {self.sector_info['name']} cũng yếu - BÁN NHANH ĐỂ BẢO VỆ VỐN")
            if self.vnindex_status and self.vnindex_status['status'] == 'YẾU':
                print("   ❗ VNINDEX yếu → Nguy cơ giảm sâu, BÁN NGAY!")
            print("   💰 Chốt lời nếu đang lãi")
            print("   ✂️  Cắt lỗ nếu đang lỗ (không chờ sâu hơn)")
        elif 'BÁN (THẬN TRỌNG)' in signal:
            print("   🟠 CÂN NHẮC BÁN hoặc GIẢM BỚT")
            print("   💡 VNINDEX tốt nên có thể GIỮ thêm nếu chưa lãi nhiều")
            print("   📊 Nếu đã lãi tốt (>10%), cân nhắc chốt một phần")
            print("   🎯 Đặt stop-loss bảo vệ lợi nhuận")
        elif 'BÁN' in signal:
            print("   🟠 CÂN NHẮC BÁN hoặc GIẢM TỶ TRỌNG")
            print("   📉 Tín hiệu tiêu cực, nên giảm xuống 30-50% vị thế")
            if self.vnindex_status and self.vnindex_status['status'] == 'TỐT':
                print("   💡 VNINDEX tốt, có thể giữ lại 50% và theo dõi")
            else:
                print("   ⚠️  Nên giảm mạnh xuống 30% hoặc thoát hẳn")
            print("   🎯 Đặt stop-loss chặt để bảo vệ vốn")
            print("   ⏰ Theo dõi sát, sẵn sàng thoát hoàn toàn nếu xấu hơn")
            print("   📉 Tín hiệu tiêu cực, nên giảm xuống 30-50% vị thế")
            print("   🎯 Đặt stop-loss chặt để bảo vệ vốn")
            print("   ⏰ Theo dõi sát, sẵn sàng thoát hoàn toàn nếu xấu hơn")
        else:
            print("   🟡 GIỮ VÀ THEO DÕI")
            print("   📊 Chưa có tín hiệu rõ ràng")
            print("   🎯 Giữ stop-loss hiện tại")
            print("   👀 Chờ tín hiệu rõ ràng hơn để quyết định")
        
        print("\n" + "="*80)
        print("⚠️  LƯU Ý: Đây chỉ là công cụ hỗ trợ phân tích kỹ thuật.")
        print("Không phải lời khuyên đầu tư. Hãy tự nghiên cứu kỹ trước khi quyết định.")
        print("="*80 + "\n")
    
    def run(self):
        """
        Chạy toàn bộ quy trình phân tích
        """
        try:
            # Lấy dữ liệu
            if self.fetch_data() is None:
                print("Không thể lấy dữ liệu. Vui lòng thử lại sau.")
                return None
            
            # Tính toán chỉ báo
            self.calculate_indicators()
            
            # Phân tích tín hiệu
            result = self.analyze()
            
            # In báo cáo
            self.print_report(result)
            
            return result
            
        except Exception as e:
            print(f"\n✗ Lỗi: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Hàm chính"""
    print("🔍 CÔNG CỤ GỢI Ý MUA BÁN CỔ PHIẾU VIỆT NAM")
    print("="*80)
    
    # Nhập mã cổ phiếu
    symbol = input("\nNhập mã cổ phiếu (VD: VNM, VCB, HPG): ").strip().upper()
    
    if not symbol:
        print("Mã cổ phiếu không hợp lệ!")
        return
    
    # Tùy chọn thời gian (mặc định 6 tháng)
    use_default = input("Sử dụng dữ liệu 6 tháng gần nhất? (Y/n): ").strip().lower()
    
    if use_default == 'n':
        start_date = input("Nhập ngày bắt đầu (YYYY-MM-DD): ").strip()
        end_date = input("Nhập ngày kết thúc (YYYY-MM-DD): ").strip()
        analyzer = StockAnalyzer(symbol, start_date, end_date)
    else:
        analyzer = StockAnalyzer(symbol)
    
    # Chạy phân tích
    analyzer.run()


if __name__ == "__main__":
    main()
