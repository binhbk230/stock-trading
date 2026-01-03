"""
Giao diện web cho công cụ phân tích cổ phiếu Việt Nam
Chạy: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

from src.core.stock_analyzer import StockAnalyzer
from src.analyzers.batch_analyzer import BatchAnalyzer
from src.analyzers.vnindex_analyzer import VNIndexAnalyzer
from src.analyzers.sector_analyzer import SectorAnalyzer
from src.core.portfolio_manager import PortfolioManager, verify_login, get_user_info, load_users_config
from src.utils.top_stocks import (
    TOP_100_STOCKS, VN30_STOCKS, MIDCAP_STOCKS, SMALLCAP_STOCKS,
    get_sector, get_all_sectors, get_stocks_by_sector, SECTOR_MAPPING
)

# Cấu hình trang
st.set_page_config(
    page_title="Stock Trading Analyzer - Vietnam",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .buy-signal {
        color: #00ff00;
        font-weight: bold;
    }
    .sell-signal {
        color: #ff0000;
        font-weight: bold;
    }
    .neutral-signal {
        color: #808080;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar (phải đặt trước để định nghĩa vnindex_interval)
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/stock-share.png", width=150)
    st.title("⚙️ Cấu hình")
    
    # Chọn interval cho VNINDEX
    st.markdown("### 📊 Khung thời gian VNINDEX")
    vnindex_interval = st.selectbox(
        "Chọn interval:",
        options=["1D", "1H", "30m", "15m"],
        index=0,  # Mặc định là 1D
        help="""1D: Dữ liệu theo ngày (đầy đủ chỉ báo MA200, BB)
1H: Dữ liệu theo giờ (realtime hơn)
30m/15m: Dữ liệu theo phút (realtime nhất, thiếu chỉ báo dài hạn)"""
    )
    
    interval_info = {
        "1D": "📅 Daily: Đầy đủ chỉ báo (MA200, BB)",
        "1H": "⏱️ Hourly: Cập nhật mỗi giờ",
        "30m": "⏰ 30 phút: Gần realtime",
        "15m": "⚡ 15 phút: Realtime nhất"
    }
    st.caption(interval_info[vnindex_interval])
    
    st.markdown("---")
    
    # Chọn chế độ
    mode = st.radio(
        "Chọn chế độ phân tích:",
        ["🎯 Phân tích đơn lẻ", "📊 Phân tích hàng loạt", "🔍 Quét thị trường", "🏭 Phân tích ngành", "💼 Danh mục của tôi"]
    )
    
    st.markdown("---")
    
    # Thông tin
    with st.expander("ℹ️ Giới thiệu"):
        st.write("""
        **Công cụ phân tích kỹ thuật** dựa trên:
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - Moving Averages (SMA/EMA)
        - Bollinger Bands
        - Stochastic Oscillator
        - Volume Analysis
        
        **Lưu ý:** Không phải lời khuyên đầu tư!
        """)
    
    with st.expander("📖 Hướng dẫn"):
        st.write("""
        **Phân tích đơn lẻ:** Phân tích chi tiết 1 mã cổ phiếu
        
        **Phân tích hàng loạt:** Phân tích nhiều mã cùng lúc
        
        **Quét thị trường:** Tìm cơ hội mua/bán trong top 100
        
        **Danh mục của tôi:** Quản lý cổ phiếu đã mua, theo dõi lãi/lỗ
        """)

# Header
st.markdown('<div class="main-header">📈 Công cụ Phân tích & Gợi ý Mua Bán Cổ Phiếu VN 📊</div>', unsafe_allow_html=True)

# Hiển thị VNINDEX ở header
try:
    vnindex_col1, vnindex_col2, vnindex_col3 = st.columns([1, 2, 1])
    with vnindex_col2:
        with st.spinner(f"Đang tải VNINDEX ({vnindex_interval})..."):
            vnindex = VNIndexAnalyzer(interval=vnindex_interval)
            vnindex.fetch_data()
            vnindex_summary = vnindex.get_summary()
            
            status_color = "🟢" if vnindex_summary['status'] == "TỐT" else "🟡" if vnindex_summary['status'] == "TRUNG BÌNH" else "🔴"
            
            # Thêm cảnh báo thời gian nếu có
            time_warning = ""
            interval_badge = f"<span style='background: #4CAF50; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;'>{vnindex_summary.get('interval', '1D')}</span>"
            if vnindex_summary.get('data_age_warning'):
                time_warning = f"<p style='font-size: 0.85rem; color: #ff6b6b;'>{vnindex_summary['data_age_warning']}</p>"
            elif vnindex_summary.get('data_date'):
                time_warning = f"<p style='font-size: 0.85rem; color: #666;'>📅 Dữ liệu: {vnindex_summary['data_date']}</p>"
            
            # Tạo khuyến nghị đầu tư chi tiết
            score = vnindex_summary['score']
            if score >= 70:
                invest_advice = "<div style='background: #d4edda; padding: 0.75rem; border-radius: 0.25rem; margin-top: 0.5rem;'><strong>🟢 MUA MẠNH</strong><br/><small>• Tỷ lệ vốn: 70-100% | Stop loss: -7%<br/>• Thị trường tốt, có thể tích cực đầu tư</small></div>"
            elif score >= 50:
                invest_advice = "<div style='background: #d1ecf1; padding: 0.75rem; border-radius: 0.25rem; margin-top: 0.5rem;'><strong>🟡 MUA THẬN TRỌNG</strong><br/><small>• Tỷ lệ vốn: 30-50% | Stop loss: -5%<br/>• Chỉ mua bluechip có tín hiệu tốt</small></div>"
            elif score >= 30:
                invest_advice = "<div style='background: #fff3cd; padding: 0.75rem; border-radius: 0.25rem; margin-top: 0.5rem;'><strong>🟠 CHỜ ĐỢI</strong><br/><small>• Tỷ lệ vốn: 10-30% | Stop loss: -3%<br/>• Ưu tiên giữ tiền mặt, quan sát thị trường</small></div>"
            else:
                invest_advice = "<div style='background: #f8d7da; padding: 0.75rem; border-radius: 0.25rem; margin-top: 0.5rem;'><strong>🔴 KHÔNG MUA / BÁN</strong><br/><small>• Tỷ lệ vốn: 0-10% | Stop loss: -2%<br/>• Bảo toàn vốn là ưu tiên, chốt lời/cắt lỗ</small></div>"
            
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; text-align: center; margin: 1rem 0;">
                <h4>📊 VNINDEX: {status_color} {vnindex_summary['status']} {interval_badge}</h4>
                <p>Giá: {vnindex_summary['current_price']:.2f} | Điểm: {vnindex_summary['percentage']:.0f}%</p>
                {time_warning}
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">{vnindex_summary['recommendation']}</p>
                {invest_advice}
            </div>
            """, unsafe_allow_html=True)
            
            # Thêm expander để xem chi tiết
            with st.expander("🔍 Xem chi tiết phân tích VNINDEX"):
                st.markdown("### 📊 Phân tích chi tiết các chỉ báo kỹ thuật")
                
                # Lấy dữ liệu chi tiết
                df = vnindex.indicators.df if vnindex.indicators else vnindex.calculate_indicators()
                latest = df.iloc[-1]
                
                # Tab cho các chỉ báo
                tab1, tab2, tab3, tab4 = st.tabs(["📈 RSI & MACD", "📊 Moving Averages", "🎯 Bollinger Bands", "📋 Tổng quan"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📈 RSI (Relative Strength Index)")
                        if 'rsi' in df.columns and not pd.isna(latest['rsi']):
                            rsi = latest['rsi']
                            st.metric("RSI", f"{rsi:.2f}")
                            
                            if rsi > 70:
                                st.error(f"⚠️ QUÁ MUA: RSI {rsi:.1f} > 70\n\nThị trường quá nóng, rủi ro điều chỉnh cao")
                            elif rsi > 65:
                                st.warning(f"⚠️ GẦN QUÁ MUA: RSI {rsi:.1f}\n\nCần thận trọng")
                            elif rsi > 35:
                                st.success(f"✅ TỐT: RSI {rsi:.1f}\n\nThị trường cân bằng")
                            elif rsi > 30:
                                st.info(f"⚠️ GẦN QUÁ BÁN: RSI {rsi:.1f}")
                            else:
                                st.info(f"💡 QUÁ BÁN: RSI {rsi:.1f} < 30\n\nCó thể là cơ hội")
                        else:
                            st.info("Không có dữ liệu RSI")
                    
                    with col2:
                        st.markdown("#### 📉 MACD")
                        if 'macd' in df.columns and not pd.isna(latest['macd']):
                            macd = latest['macd']
                            macd_signal = latest.get('macd_signal', 0)
                            macd_hist = latest.get('macd_hist', 0)
                            
                            col_a, col_b = st.columns(2)
                            col_a.metric("MACD", f"{macd:.2f}")
                            col_b.metric("Signal", f"{macd_signal:.2f}")
                            st.metric("Histogram", f"{macd_hist:.2f}")
                            
                            if macd > macd_signal and macd > 0:
                                st.success("🟢 XU HƯỚNG TĂNG MẠNH\n\nMACD > 0 và > Signal")
                            elif macd > macd_signal:
                                st.info("🟢 XU HƯỚNG TĂNG\n\nMACD > Signal nhưng < 0")
                            elif macd < macd_signal and macd < 0:
                                st.error("🔴 XU HƯỚNG GIẢM MẠNH\n\nMACD < 0 và < Signal")
                            else:
                                st.warning("🟡 XU HƯỚNG GIẢM\n\nMACD < Signal")
                        else:
                            st.info("Không có dữ liệu MACD")
                
                with tab2:
                    st.markdown("#### 📊 Moving Averages")
                    
                    current_price = latest['close']
                    ma_data = []
                    
                    for ma_name, period in [('sma_20', 20), ('sma_50', 50), ('sma_200', 200)]:
                        if ma_name in df.columns and not pd.isna(latest[ma_name]):
                            ma_value = latest[ma_name]
                            diff = current_price - ma_value
                            diff_pct = (diff / ma_value) * 100
                            position = "TRÊN" if diff > 0 else "DƯỚI"
                            
                            ma_data.append({
                                'MA': f'MA{period}',
                                'Giá trị': f'{ma_value:.2f}',
                                'Vị trí': position,
                                'Chênh lệch': f'{diff:+.2f}',
                                'Tỷ lệ': f'{diff_pct:+.2f}%'
                            })
                    
                    if ma_data:
                        st.dataframe(pd.DataFrame(ma_data), use_container_width=True, hide_index=True)
                        
                        above_count = sum(1 for ma in ma_data if ma['Vị trí'] == 'TRÊN')
                        total_count = len(ma_data)
                        
                        if above_count == total_count:
                            st.success(f"✅ XU HƯỚNG TĂNG MẠNH\n\nGiá trên tất cả {total_count} đường MA")
                        elif above_count >= total_count / 2:
                            st.info(f"⚠️ XU HƯỚNG TĂNG YẾU\n\nGiá trên {above_count}/{total_count} đường MA")
                        else:
                            st.error(f"❌ XU HƯỚNG GIẢM\n\nGiá dưới {total_count - above_count}/{total_count} đường MA")
                    else:
                        st.warning("⚠️ Không đủ dữ liệu để tính MA\n\nInterval ngắn (15m, 30m) có thể thiếu MA200")
                
                with tab3:
                    st.markdown("#### 🎯 Bollinger Bands")
                    
                    if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
                        bb_upper = latest['bb_upper']
                        bb_lower = latest['bb_lower']
                        bb_middle = latest['bb_middle']
                        
                        if not pd.isna(bb_upper) and not pd.isna(bb_lower):
                            bb_width = bb_upper - bb_lower
                            bb_position = (current_price - bb_lower) / bb_width if bb_width > 0 else 0.5
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("BB Upper", f"{bb_upper:.2f}")
                                st.metric("BB Middle", f"{bb_middle:.2f}")
                                st.metric("BB Lower", f"{bb_lower:.2f}")
                            
                            with col2:
                                st.metric("Giá hiện tại", f"{current_price:.2f}")
                                st.metric("Vị trí trong band", f"{bb_position*100:.1f}%")
                                st.metric("Độ rộng band", f"{bb_width:.2f}")
                            
                            # Progress bar hiển thị vị trí
                            st.progress(bb_position)
                            
                            if bb_position > 0.8:
                                st.error("🔴 GẦN BB UPPER\n\nGiá có thể quá mua, cần thận trọng")
                            elif bb_position > 0.5:
                                st.success("🟢 TRÊN BB MIDDLE\n\nXu hướng tích cực")
                            elif bb_position > 0.2:
                                st.warning("🟡 DƯỚI BB MIDDLE\n\nXu hướng yếu")
                            else:
                                st.info("💡 GẦN BB LOWER\n\nCó thể quá bán, cơ hội mua")
                        else:
                            st.info("Dữ liệu BB không hợp lệ")
                    else:
                        st.warning("⚠️ Không có dữ liệu Bollinger Bands\n\nInterval ngắn có thể thiếu chỉ báo này")
                
                with tab4:
                    st.markdown("#### 📋 Chi tiết đánh giá")
                    
                    # Hiển thị tất cả các điều kiện
                    for i, condition in enumerate(vnindex_summary['conditions'], 1):
                        if "✅" in condition:
                            st.success(f"{i}. {condition}")
                        elif "❌" in condition:
                            st.error(f"{i}. {condition}")
                        else:
                            st.warning(f"{i}. {condition}")
                    
                    st.markdown("---")
                    
                    # Thông tin thêm
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tổng điểm", f"{vnindex_summary['score']}/100")
                    with col2:
                        st.metric("Phần trăm", f"{vnindex_summary['percentage']:.1f}%")
                    with col3:
                        st.metric("Số điểm dữ liệu", f"{len(df)}")
                    
                    # Khuyến nghị đầu tư
                    st.markdown("### 💡 Khuyến nghị đầu tư")
                    score = vnindex_summary['score']
                    
                    if score >= 70:
                        st.success("""
                        **🟢 MUA MẠNH**
                        - Tỷ lệ vốn: 70-100%
                        - Stop loss: -7%
                        - Thị trường tốt, có thể tích cực đầu tư
                        """)
                    elif score >= 50:
                        st.info("""
                        **🟡 MUA THẬN TRỌNG**
                        - Tỷ lệ vốn: 30-50%
                        - Stop loss: -5%
                        - Chỉ mua bluechip có tín hiệu tốt
                        """)
                    elif score >= 30:
                        st.warning("""
                        **🟠 CHỜ ĐỢI**
                        - Tỷ lệ vốn: 10-30%
                        - Stop loss: -3%
                        - Ưu tiên giữ tiền mặt, quan sát thị trường
                        """)
                    else:
                        st.error("""
                        **🔴 KHÔNG MUA / BÁN**
                        - Tỷ lệ vốn: 0-10%
                        - Stop loss: -2%
                        - Bảo toàn vốn là ưu tiên, chốt lời/cắt lỗ
                        """)
                    
                    st.markdown("---")
                    st.caption("💡 Xem thêm: File VNINDEX_INVESTMENT_STRATEGY.md để biết chi tiết chiến lược đầu tư")
                    
except Exception as e:
    st.warning(f"⚠️ Không thể tải VNINDEX: {str(e)}")

# Nội dung chính
if mode == "🎯 Phân tích đơn lẻ":
    st.header("🎯 Phân tích Đơn Lẻ")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        symbol = st.text_input(
            "Nhập mã cổ phiếu:",
            value="VNM",
            max_chars=10,
            help="VD: VNM, VCB, HPG, FPT"
        ).upper()
    
    with col2:
        days = st.selectbox(
            "Khoảng thời gian:",
            [30, 90, 180, 365],
            index=2,
            help="Số ngày lịch sử để phân tích"
        )
    
    with col3:
        st.write("")
        st.write("")
        analyze_btn = st.button("🚀 Phân tích", type="primary", use_container_width=True)
    
    if analyze_btn and symbol:
        with st.spinner(f"Đang phân tích {symbol}..."):
            try:
                # Tính ngày bắt đầu
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                
                # Tạo analyzer
                analyzer = StockAnalyzer(symbol, start_date, end_date)
                
                # Lấy dữ liệu
                if analyzer.fetch_data() is None:
                    st.error(f"❌ Không thể lấy dữ liệu cho mã {symbol}")
                else:
                    # Tính toán chỉ báo
                    analyzer.calculate_indicators()
                    
                    # Phân tích
                    result = analyzer.analyze()
                    
                    if result:
                        # Hiển thị thông tin VNINDEX nếu có
                        if analyzer.vnindex_status:
                            st.markdown("### 📊 Tình trạng VNINDEX")
                            vnindex_status = analyzer.vnindex_status
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                status_color = "🟢" if vnindex_status['status'] == "TỐT" else "🟡" if vnindex_status['status'] == "TRUNG BÌNH" else "🔴"
                                st.metric("Trạng thái", f"{status_color} {vnindex_status['status']}")
                            with col2:
                                st.metric("Điểm", f"{vnindex_status['percentage']:.0f}%")
                            with col3:
                                st.metric("Giá VNINDEX", f"{vnindex_status['current_price']:.2f}")
                            with col4:
                                if vnindex_status.get('data_date'):
                                    date_label = "Hôm nay ✅" if vnindex_status.get('is_today') else "Ngày"
                                    st.metric(date_label, vnindex_status['data_date'])
                            
                            # Cảnh báo thời gian dữ liệu
                            if vnindex_status.get('data_age_warning'):
                                st.warning(vnindex_status['data_age_warning'])
                            
                            if vnindex_status.get('conditions'):
                                with st.expander("🔍 Chi tiết điều kiện VNINDEX"):
                                    for condition in vnindex_status['conditions']:
                                        st.write(condition)
                            
                            # Hiển thị recommendation cũ
                            st.info(vnindex_status['recommendation'])
                            
                            # Hiển thị khuyến nghị đầu tư chi tiết
                            score = vnindex_status.get('score', 50)
                            if score >= 70:
                                st.success("""
                                **🟢 MUA MẠNH**
                                - Tỷ lệ vốn: 70-100% | Stop loss: -7%
                                - Thị trường tốt, có thể tích cực đầu tư
                                """)
                            elif score >= 50:
                                st.info("""
                                **🟡 MUA THẬN TRỌNG**
                                - Tỷ lệ vốn: 30-50% | Stop loss: -5%
                                - Chỉ mua bluechip có tín hiệu tốt
                                """)
                            elif score >= 30:
                                st.warning("""
                                **🟠 CHỜ ĐỢI**
                                - Tỷ lệ vốn: 10-30% | Stop loss: -3%
                                - Ưu tiên giữ tiền mặt, quan sát thị trường
                                """)
                            else:
                                st.error("""
                                **🔴 KHÔNG MUA / BÁN**
                                - Tỷ lệ vốn: 0-10% | Stop loss: -2%
                                - Bảo toàn vốn là ưu tiên, chốt lời/cắt lỗ
                                """)
                            
                            st.markdown("---")
                        
                        # Hiển thị thông tin ngành nếu có
                        if analyzer.sector_info:
                            st.markdown("### 🏭 Tình trạng Ngành")
                            sector_info = analyzer.sector_info
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Ngành", sector_info['name'])
                            with col2:
                                status_color = "🟢" if sector_info['status'] == "MẠNH" else "🟡" if sector_info['status'] == "TRUNG BÌNH" else "🔴"
                                st.metric("Trạng thái", f"{status_color} {sector_info['status']}")
                            with col3:
                                st.metric("Điểm ngành", f"{sector_info['score']:.0f}")
                            
                            # Hiển thị cảnh báo nếu ngành yếu
                            if sector_info['status'] == 'YẾU':
                                st.error(f"⚠️ CẢNH BÁO: Ngành {sector_info['name']} đang yếu. {sector_info['recommendation']}")
                            elif sector_info['status'] == 'MẠNH':
                                st.success(f"✅ Ngành {sector_info['name']} đang mạnh. {sector_info['recommendation']}")
                            else:
                                st.info(f"📊 Ngành {sector_info['name']}: {sector_info['recommendation']}")
                            
                            st.markdown("---")
                        
                        # Thông tin giá
                        current_price = analyzer.data['close'].iloc[-1]
                        prev_price = analyzer.data['close'].iloc[-2]
                        price_change = current_price - prev_price
                        price_change_pct = (price_change / prev_price) * 100
                        volume = analyzer.data['volume'].iloc[-1]
                        
                        # Format giá theo bước giá sàn
                        def format_price_display(price):
                            """Format giá hiển thị theo bước giá sàn"""
                            if price < 10:
                                return f"{price:,.2f}"  # 2 chữ số thập phân
                            elif price < 50:
                                return f"{price:,.2f}"  # 2 chữ số thập phân
                            else:
                                return f"{price:,.1f}"  # 1 chữ số thập phân
                        
                        # Hiển thị metrics
                        st.markdown("### 📊 Thông tin hiện tại")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Giá",
                                format_price_display(current_price),
                                f"{price_change_pct:+.2f}%"
                            )
                        
                        with col2:
                            signal = result['signal']
                            signal_color = "🟢" if "MUA" in signal else "🔴" if "BÁN" in signal else "🟡" if "CHỜ" in signal else "⚪"
                            st.metric("Tín hiệu", f"{signal_color} {signal}")
                            
                            # Hiển thị cảnh báo VNINDEX nếu có
                            if result.get('vnindex_warning'):
                                st.caption(result['vnindex_warning'])
                        
                        with col3:
                            st.metric(
                                "Độ tin cậy",
                                f"{result['confidence']:.1f}%"
                            )
                        
                        with col4:
                            st.metric(
                                "Khối lượng",
                                f"{volume:,.0f}"
                            )
                        
                        # Hiển thị điểm ngành nếu có
                        if 'sector' in result:
                            sector_info = result['sector']
                            st.markdown("### 🏭 Đánh giá Ngành")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Ngành", sector_info['sector'])
                            with col2:
                                st.metric("Điểm ngành", f"{sector_info['score']:.1f}/100")
                            with col3:
                                status = sector_info['status']
                                status_icon = "🟢" if status == "MẠNH" else "🟡" if "TRUNG" in status else "🔴"
                                st.metric("Trạng thái", f"{status_icon} {status}")
                            
                            st.caption(f"💡 {sector_info['reason']}")
                        
                        # Hiển thị các mức giá khuyến nghị
                        if result.get('stop_loss'):
                            st.markdown("### 💰 Các mức giá khuyến nghị (từ giá hiện tại)")
                            
                            # Hàm format giá cho các mức khuyến nghị
                            def format_price(price):
                                """Format giá theo bước giá sàn"""
                                if price < 10:
                                    return f"{price:,.2f}"  # 2 chữ số thập phân cho giá < 10
                                elif price < 50:
                                    return f"{price:,.2f}"  # 2 chữ số thập phân cho giá 10-50
                                else:
                                    return f"{price:,.1f}"  # 1 chữ số thập phân cho giá >= 50
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                if result.get('stop_loss'):
                                    loss_pct = ((result['stop_loss'] - current_price) / current_price) * 100
                                    st.metric(
                                        "🛑 Cắt lỗ",
                                        format_price(result['stop_loss']),
                                        f"{loss_pct:.1f}%",
                                        delta_color="inverse",
                                        help="Mức giá nên bán để hạn chế lỗ"
                                    )
                            
                            with col2:
                                if result.get('take_profit_1'):
                                    tp1_pct = ((result['take_profit_1'] - current_price) / current_price) * 100
                                    st.metric(
                                        "✅ Chốt lời T1",
                                        format_price(result['take_profit_1']),
                                        f"+{tp1_pct:.1f}%",
                                        help="Mục tiêu chốt lời 30-50% vốn"
                                    )
                            
                            with col3:
                                if result.get('take_profit_2'):
                                    tp2_pct = ((result['take_profit_2'] - current_price) / current_price) * 100
                                    st.metric(
                                        "✅ Chốt lời T2",
                                        format_price(result['take_profit_2']),
                                        f"+{tp2_pct:.1f}%",
                                        help="Mục tiêu chốt lời 30-40% vốn"
                                    )
                            
                            with col4:
                                if result.get('take_profit_3'):
                                    tp3_pct = ((result['take_profit_3'] - current_price) / current_price) * 100
                                    st.metric(
                                        "✅ Chốt lời T3",
                                        format_price(result['take_profit_3']),
                                        f"+{tp3_pct:.1f}%",
                                        help="Mục tiêu chốt lời phần còn lại"
                                    )
                            
                            # Risk/Reward ratio
                            if result.get('risk_reward_ratio'):
                                st.info(f"⚖️ **Tỷ lệ Risk/Reward:** 1:{result['risk_reward_ratio']:.2f} - "
                                       f"{'Tốt' if result['risk_reward_ratio'] >= 2 else 'Chấp nhận được' if result['risk_reward_ratio'] >= 1.5 else 'Thận trọng'}")
                            
                            st.markdown("---")
                        
                        # Biểu đồ giá
                        st.markdown("### 📈 Biểu đồ Giá & Chỉ báo")
                        
                        # Tạo biểu đồ với Plotly
                        fig = go.Figure()
                        
                        # Giá đóng cửa
                        fig.add_trace(go.Scatter(
                            x=analyzer.data.index,
                            y=analyzer.data['close'],
                            name='Giá đóng cửa',
                            line=dict(color='blue', width=2)
                        ))
                        
                        # SMA
                        if 'sma_20' in analyzer.data.columns:
                            fig.add_trace(go.Scatter(
                                x=analyzer.data.index,
                                y=analyzer.data['sma_20'],
                                name='SMA(20)',
                                line=dict(color='orange', width=1, dash='dash')
                            ))
                        
                        if 'sma_50' in analyzer.data.columns:
                            fig.add_trace(go.Scatter(
                                x=analyzer.data.index,
                                y=analyzer.data['sma_50'],
                                name='SMA(50)',
                                line=dict(color='red', width=1, dash='dash')
                            ))
                        
                        # Bollinger Bands
                        if 'bb_upper' in analyzer.data.columns:
                            fig.add_trace(go.Scatter(
                                x=analyzer.data.index,
                                y=analyzer.data['bb_upper'],
                                name='BB Upper',
                                line=dict(color='gray', width=1),
                                opacity=0.5
                            ))
                            fig.add_trace(go.Scatter(
                                x=analyzer.data.index,
                                y=analyzer.data['bb_lower'],
                                name='BB Lower',
                                line=dict(color='gray', width=1),
                                fill='tonexty',
                                opacity=0.3
                            ))
                        
                        fig.update_layout(
                            title=f"Biểu đồ giá {symbol}",
                            xaxis_title="Ngày",
                            yaxis_title="Giá (VNĐ)",
                            hovermode='x unified',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Chi tiết chỉ báo
                        st.markdown("### 📋 Chi tiết Các Chỉ Báo")
                        
                        details = result['details']
                        
                        cols = st.columns(2)
                        
                        for idx, (indicator_name, indicator_data) in enumerate(details.items()):
                            with cols[idx % 2]:
                                signal_text = indicator_data['signal']
                                score = indicator_data['score']
                                reason = indicator_data['reason']
                                
                                if signal_text == 'MUA':
                                    icon = "✅"
                                    color = "#00ff00"
                                elif signal_text == 'BÁN':
                                    icon = "❌"
                                    color = "#ff0000"
                                else:
                                    icon = "➖"
                                    color = "#808080"
                                
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>{icon} {indicator_name.upper()}</h4>
                                    <p style="color: {color}; font-size: 1.2rem;">
                                        <strong>{signal_text}</strong> (Điểm: {score:.0f})
                                    </p>
                                    <p style="font-size: 0.9rem;">{reason}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Khuyến nghị
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 💡 Chưa mua - Nên làm gì?")
                            
                            if 'CHỜ - VNINDEX YẾU' in result['signal']:
                                st.error("""
                                ⛔ **KHÔNG NÊN MUA**
                                
                                🔒 VNINDEX đang yếu
                                
                                👀 Chờ thị trường phục hồi
                                """)
                            elif 'MUA MẠNH' in result['signal']:
                                st.success("""
                                ✅ **CÓ THỂ MUA**
                                
                                📊 Tín hiệu tích cực
                                
                                🎯 Đặt stop-loss ~3-5%
                                """)
                            elif 'MUA (THẬN TRỌNG)' in result['signal'] or 'MUA' in result['signal']:
                                st.info("""
                                ⚠️ **CÂN NHẮC MUA**
                                
                                📊 Cần thận trọng
                                
                                💰 Giảm tỷ lệ vốn
                                """)
                                if analyzer.vnindex_status and analyzer.vnindex_status['status'] != 'TỐT':
                                    st.caption("📊 Thị trường chung chưa tốt")
                            elif 'BÁN MẠNH' in result['signal'] or 'BÁN' in result['signal']:
                                st.error("""
                                ❌ **KHÔNG NÊN MUA**
                                
                                📉 Tín hiệu tiêu cực
                                
                                ⏰ Chờ cơ hội tốt hơn
                                """)
                            elif 'CÂN NHẮC BÁN' in result['signal']:
                                st.error("""
                                ⛔ **KHÔNG NÊN MUA**
                                
                                🟠 Thị trường yếu
                                
                                ⏰ Chờ ổn định
                                """)
                            else:
                                st.info("""
                                ⏸️ **NÊN CHỜ**
                                
                                📊 Chưa có tín hiệu rõ
                                
                                👀 Theo dõi thêm
                                """)
                        
                        with col2:
                            st.markdown("### 💼 Đang nắm giữ - Nên làm gì?")
                            
                            if 'CHỜ - VNINDEX YẾU' in result['signal'] or 'CÂN NHẮC BÁN' in result['signal']:
                                st.error("""
                                🔴 **CẦN XEM XÉT BÁN**
                                
                                ⚠️ VNINDEX yếu → giá có thể giảm
                                
                                💰 Chốt lời nếu lãi
                                
                                ✂️ Cắt lỗ nếu lỗ >5-7%
                                
                                📉 Giảm 50% tỷ trọng
                                """)
                                if 'CÂN NHẮC BÁN' in result['signal']:
                                    st.caption("⏰ Theo dõi sát, nếu xấu hơn thì bán ngay")
                            elif 'MUA MẠNH' in result['signal']:
                                st.success("""
                                🟢 **GIỮ TIẾP/MUA THÊM**
                                
                                📈 Tín hiệu tích cực
                                
                                🎯 Di chuyển stop-loss lên
                                
                                💡 Có thể tăng tỷ trọng
                                """)
                            elif 'MUA (THẬN TRỌNG)' in result['signal'] or 'MUA' in result['signal']:
                                st.warning("""
                                🟡 **GIỮ - KHÔNG MUA THÊM**
                                
                                📊 Chưa thực sự tốt
                                
                                🎯 Giữ stop-loss chặt
                                
                                ⚠️ Sẵn sàng bán nếu xấu
                                """)
                            elif 'BÁN MẠNH' in result['signal']:
                                vnindex_weak = analyzer.vnindex_status and analyzer.vnindex_status['status'] == 'YẾU'
                                if vnindex_weak:
                                    st.error("""
                                    🔴 **BÁN NGAY - NGUY CƠ CAO**
                                    
                                    ❗ VNINDEX yếu + Tín hiệu bán mạnh
                                    
                                    ⚠️ Nguy cơ giảm sâu rất cao
                                    
                                    💰 Chốt lời ngay nếu lãi
                                    
                                    ✂️ Cắt lỗ không chờ sâu
                                    """)
                                else:
                                    st.error("""
                                    🔴 **NÊN BÁN NGAY**
                                    
                                    ⚠️ Rủi ro giảm giá cao
                                    
                                    💰 Chốt lời nếu đang lãi
                                    
                                    ✂️ Cắt lỗ không chờ sâu
                                    """)
                            elif 'BÁN (THẬN TRỌNG)' in result['signal']:
                                st.warning("""
                                🟠 **CÂN NHẮC GIỮ THÊM**
                                
                                💡 VNINDEX tốt, có thể giữ
                                
                                📊 Nếu lãi >10% thì chốt bớt
                                
                                🎯 Stop-loss bảo vệ lợi nhuận
                                """)
                            elif 'BÁN' in result['signal']:
                                vnindex_good = analyzer.vnindex_status and analyzer.vnindex_status['status'] == 'TỐT'
                                if vnindex_good:
                                    st.warning("""
                                    🟠 **GIẢM BỚT - GIỮ 50%**
                                    
                                    📉 Bán 50% vị thế
                                    
                                    💡 VNINDEX tốt nên giữ 50%
                                    
                                    🎯 Stop-loss chặt
                                    
                                    ⏰ Theo dõi tiếp
                                    """)
                                else:
                                    st.warning("""
                                    🟠 **GIẢM MẠNH - GIỮ 30%**
                                    
                                    📉 Bán 70% vị thế
                                    
                                    ⚠️ VNINDEX chưa tốt
                                    
                                    🎯 Stop-loss chặt
                                    
                                    ⏰ Sẵn sàng thoát hẳn
                                    """)
                            else:
                                st.info("""
                                🟡 **GIỮ VÀ THEO DÕI**
                                
                                📊 Chưa có tín hiệu rõ
                                
                                🎯 Giữ stop-loss
                                
                                👀 Chờ tín hiệu tiếp theo
                                """)
                        
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

elif mode == "📊 Phân tích hàng loạt":
    st.header("📊 Phân tích Hàng Loạt")
    
    # Chọn phương thức nhập
    input_method = st.radio(
        "Phương thức nhập mã:",
        ["📝 Nhập tự do", "📋 Chọn nhóm có sẵn"],
        horizontal=True
    )
    
    selected_symbols = []
    
    if input_method == "📝 Nhập tự do":
        st.markdown("### ✍️ Nhập danh sách mã cổ phiếu")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Text area để nhập nhiều mã
            stock_input = st.text_area(
                "Nhập mã cổ phiếu (mỗi mã 1 dòng hoặc cách nhau bởi dấu phấy):",
                height=150,
                placeholder="VNM\nVCB\nHPG\n\nhoặc: VNM, VCB, HPG",
                help="Hỗ trợ nhập theo dòng hoặc phân cách bằng dấu phấy (,)"
            )
            
            # Parse input
            if stock_input:
                # Tách theo dòng mới và dấu phấy
                raw_symbols = stock_input.replace(',', '\n').split('\n')
                # Loại bỏ khoảng trắng và chuyển về chữ hoa
                selected_symbols = [s.strip().upper() for s in raw_symbols if s.strip()]
                # Loại bỏ trùng lặp
                selected_symbols = list(dict.fromkeys(selected_symbols))
        
        with col2:
            st.markdown("##### 💡 Gợi ý mã phổ biến:")
            if st.button("VN30", use_container_width=True):
                st.session_state['stock_input'] = ', '.join(VN30_STOCKS[:10])
            if st.button("Ngân hàng", use_container_width=True):
                banks = [s for s in TOP_100_STOCKS if s in ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'ACB', 'STB']]
                st.session_state['stock_input'] = ', '.join(banks)
            if st.button("Bluechip", use_container_width=True):
                bluechips = ['VNM', 'VCB', 'HPG', 'VHM', 'GAS', 'MSN', 'VIC', 'FPT']
                st.session_state['stock_input'] = ', '.join(bluechips)
    
    else:  # Chọn nhóm có sẵn
        col1, col2 = st.columns([3, 1])
        
        with col1:
            stock_group = st.selectbox(
                "Chọn nhóm cổ phiếu:",
                ["VN30 (Top 30)", "Midcap", "Smallcap", "Top 100", "Tùy chỉnh theo ngành"]
            )
        
        if stock_group == "VN30 (Top 30)":
            selected_symbols = VN30_STOCKS
        elif stock_group == "Midcap":
            selected_symbols = MIDCAP_STOCKS
        elif stock_group == "Smallcap":
            selected_symbols = SMALLCAP_STOCKS
        elif stock_group == "Top 100":
            selected_symbols = TOP_100_STOCKS
        else:  # Tùy chỉnh theo ngành
            selected_sector = st.selectbox("Chọn ngành:", get_all_sectors())
            selected_symbols = get_stocks_by_sector(selected_sector)
    
    # Hiển thị thông tin số lượng cổ phiếu
    if selected_symbols:
        st.info(f"📌 Sẽ phân tích **{len(selected_symbols)}** cổ phiếu: {', '.join(selected_symbols[:10])}{'...' if len(selected_symbols) > 10 else ''}")
    else:
        st.warning("⚠️ Vui lòng nhập ít nhất 1 mã cổ phiếu")
    
    # Nút phân tích
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        batch_btn = st.button("🚀 Bắt đầu phân tích", type="primary", use_container_width=True, disabled=not selected_symbols)
    
    if batch_btn and selected_symbols:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Tạo batch analyzer
        batch = BatchAnalyzer(selected_symbols, max_workers=5)
        
        # Callback để cập nhật tiến độ
        def update_progress(completed, total, symbol):
            progress = completed / total
            progress_bar.progress(progress)
            status_text.text(f"Đang phân tích: {symbol} ({completed}/{total})")
        
        # Chạy phân tích
        with st.spinner("Đang phân tích..."):
            batch.analyze_batch(progress_callback=update_progress)
        
        progress_bar.empty()
        status_text.text("✅ Hoàn thành!")
        
        # Lấy kết quả
        df = batch.get_dataframe()
        summary = batch.get_summary()
        
        if df is not None and not df.empty:
            # Tóm tắt
            st.markdown("### 📊 Tóm tắt Kết quả")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Tổng số", summary['total'])
            with col2:
                st.metric("🟢 MUA MẠNH", summary['buy_strong'])
            with col3:
                st.metric("🟢 MUA", summary['buy'])
            with col4:
                st.metric("🔴 BÁN MẠNH", summary['sell_strong'])
            with col5:
                st.metric("🔴 BÁN", summary['sell'])
            
            # Biểu đồ phân bố tín hiệu
            st.markdown("### 📈 Phân bố Tín hiệu")
            
            signal_counts = df['signal'].value_counts()
            fig = px.pie(
                values=signal_counts.values,
                names=signal_counts.index,
                title="Phân bố các tín hiệu giao dịch",
                color_discrete_map={
                    'MUA MẠNH': '#00cc00',
                    'MUA': '#66ff66',
                    'BÁN MẠNH': '#cc0000',
                    'BÁN': '#ff6666',
                    'NEUTRAL': '#999999'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📊 Chi tiết từng cổ phiếu")
            st.caption("💡 Click vào từng cổ phiếu để xem phân tích chi tiết (Sắp xếp theo điểm tổng mạnh nhất → yếu nhất)")
            
            # Tính tổng điểm = buy_score - sell_score và sắp xếp theo giá trị tuyệt đối giảm dần
            df['total_score'] = df['buy_score'] - df['sell_score']
            df['abs_score'] = df['total_score'].abs()
            df_sorted = df.sort_values('abs_score', ascending=False)
            
            # Hiển thị từng cổ phiếu trong expander
            for idx, row in df_sorted.iterrows():
                # Xác định màu icon theo tín hiệu
                signal = row['signal']
                if 'MUA MẠNH' in signal:
                    icon = "🟢"
                    color = "#d4edda"
                elif 'MUA' in signal:
                    icon = "🟢"
                    color = "#e7f5e7"
                elif 'BÁN MẠNH' in signal:
                    icon = "🔴"
                    color = "#f8d7da"
                elif 'BÁN' in signal:
                    icon = "🔴"
                    color = "#ffe0e0"
                else:
                    icon = "⚪"
                    color = "#f0f0f0"
                
                # Format giá
                def format_price_display(price):
                    if price < 10:
                        return f"{price:,.2f}"
                    elif price < 50:
                        return f"{price:,.2f}"
                    else:
                        return f"{price:,.1f}"
                
                with st.expander(f"{icon} **{row['symbol']}** - {signal} ({row['confidence']:.1f}%) | Giá: {format_price_display(row['price'])} | {row['price_change_pct']:+.2f}%"):
                    
                    # Metrics hàng 1
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Giá", format_price_display(row['price']), f"{row['price_change_pct']:+.2f}%")
                    with col2:
                        st.metric("Tín hiệu", f"{icon} {signal}")
                    with col3:
                        st.metric("Độ tin cậy", f"{row['confidence']:.1f}%")
                    with col4:
                        st.metric("Volume", f"{row['volume']:,.0f}")
                    
                    # Điểm ngành (nếu có)
                    if 'sector_score' in row and pd.notna(row['sector_score']):
                        st.markdown("#### 🏭 Đánh giá Ngành")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Ngành", row['sector'])
                        with col2:
                            st.metric("Điểm ngành", f"{row['sector_score']:.1f}/100")
                        with col3:
                            status = row['sector_status']
                            status_icon = "🟢" if status == "MẠNH" else "🟡" if "TRUNG" in status else "🔴"
                            st.metric("Trạng thái", f"{status_icon} {status}")
                    
                    # Chỉ báo kỹ thuật
                    st.markdown("#### 📊 Chỉ báo Kỹ thuật")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if pd.notna(row.get('rsi')):
                            rsi_color = "🟢" if 30 <= row['rsi'] <= 70 else "🔴"
                            st.metric("RSI", f"{rsi_color} {row['rsi']:.1f}")
                    with col2:
                        if pd.notna(row.get('macd')):
                            macd_signal = "🟢 Tăng" if row['macd'] > row.get('macd_signal', 0) else "🔴 Giảm"
                            st.metric("MACD", macd_signal)
                    with col3:
                        if pd.notna(row.get('sma_20')):
                            ma_status = "🟢 Trên MA20" if row['price'] > row['sma_20'] else "🔴 Dưới MA20"
                            st.metric("MA20", ma_status)
                    with col4:
                        if pd.notna(row.get('sma_50')):
                            ma_status = "🟢 Trên MA50" if row['price'] > row['sma_50'] else "🔴 Dưới MA50"
                            st.metric("MA50", ma_status)
                    
                    # Điểm mua/bán
                    st.markdown("#### 📈 Điểm số Chi tiết")
                    st.caption("💡 Điểm MUA: Tổng điểm từ các chỉ báo cho tín hiệu MUA | Điểm BÁN: Tổng điểm từ các chỉ báo cho tín hiệu BÁN")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Điểm MUA", 
                            f"{row['buy_score']:.0f}",
                            help="Tổng điểm từ RSI, MACD, MA, BB, Stochastic, Volume đang cho tín hiệu MUA"
                        )
                    with col2:
                        st.metric(
                            "Điểm BÁN", 
                            f"{row['sell_score']:.0f}",
                            help="Tổng điểm từ RSI, MACD, MA, BB, Stochastic, Volume đang cho tín hiệu BÁN"
                        )
                    with col3:
                        total_score = row['buy_score'] - row['sell_score']
                        score_color = "🟢" if total_score > 0 else "🔴" if total_score < 0 else "⚪"
                        st.metric(
                            "Tổng điểm", 
                            f"{score_color} {total_score:+.0f}",
                            help="Điểm MUA - Điểm BÁN. Dương (+) = xu hướng MUA, Âm (-) = xu hướng BÁN. Giá trị tuyệt đối càng lớn = tín hiệu càng mạnh"
                        )
                    
                    # Chi tiết từng chỉ báo
                    with st.expander("🔍 Chi tiết từng chỉ báo"):
                        if 'details' in row and pd.notna(row['details']):
                            details = row['details']
                            
                            st.markdown("##### Điểm số từng chỉ báo:")
                            
                            for indicator, data in details.items():
                                if isinstance(data, dict) and 'signal' in data:
                                    signal = data['signal']
                                    score = data.get('score', 0)
                                    reason = data.get('reason', '')
                                    
                                    # Icon theo tín hiệu
                                    if signal == 'MUA':
                                        icon = "🟢"
                                        score_text = f"+{score:.1f}"
                                    elif signal == 'BÁN':
                                        icon = "🔴"
                                        score_text = f"+{score:.1f}"
                                    else:
                                        icon = "⚪"
                                        score_text = "0.0"
                                    
                                    st.markdown(f"**{icon} {indicator.upper()}**: {signal} ({score_text} điểm)")
                                    if reason:
                                        st.caption(f"  ↳ {reason}")
                        else:
                            st.info("Không có dữ liệu chi tiết")
                    
                    # VNINDEX warning
                    if pd.notna(row.get('vnindex_warning')):
                        st.info(f"💡 {row['vnindex_warning']}")
            
            # Download Excel
            st.markdown("---")
            st.markdown("### 💾 Tải về Kết quả")
            
            if st.button("📥 Lưu ra file Excel"):
                filename = f"stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                batch.save_to_excel(filename)
                st.success(f"✅ Đã lưu vào file: {filename}")
        else:
            st.error("❌ Không có kết quả phân tích. Có thể do lỗi kết nối hoặc mã cổ phiếu không hợp lệ.")
            st.info("💡 Hãy thử lại với các mã cổ phiếu khác hoặc kiểm tra kết nối internet.")

elif mode == "🔍 Quét thị trường":
    st.header("🔍 Quét Thị Trường - Tìm Cơ Hội")
    
    # Chọn phạm vi quét
    st.markdown("### 📋 Chọn phạm vi quét")
    
    scan_scope = st.radio(
        "Chọn danh sách cổ phiếu:",
        ["📋 Nhóm có sẵn", "✍️ Tùy chỉnh"],
        horizontal=True
    )
    
    selected_symbols = []
    
    if scan_scope == "✍️ Tùy chỉnh":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            stock_input = st.text_area(
                "Nhập mã cổ phiếu (mỗi mã 1 dòng hoặc cách nhau bởi dấu phấy):",
                height=120,
                placeholder="VNM, VCB, HPG\nhoặc:\nVNM\nVCB\nHPG",
                help="Nhập danh sách mã cổ phiếu bạn muốn quét"
            )
            
            if stock_input:
                raw_symbols = stock_input.replace(',', '\n').split('\n')
                selected_symbols = [s.strip().upper() for s in raw_symbols if s.strip()]
                selected_symbols = list(dict.fromkeys(selected_symbols))
        
        with col2:
            st.markdown("##### 💡 Gợi ý:")
            if st.button("Top 10 VN30", use_container_width=True):
                st.session_state['scan_input'] = ', '.join(VN30_STOCKS[:10])
            if st.button("Ngân hàng", use_container_width=True):
                banks = [s for s in TOP_100_STOCKS if s in ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'ACB', 'STB']]
                st.session_state['scan_input'] = ', '.join(banks)
            if st.button("Top 20", use_container_width=True):
                st.session_state['scan_input'] = ', '.join(TOP_100_STOCKS[:20])
    
    else:  # Nhóm có sẵn
        col1, col2 = st.columns(2)
        
        with col1:
            stock_group = st.selectbox(
                "Chọn nhóm:",
                ["Top 50 (Nhanh)", "VN30", "Top 100 (Đầy đủ)", "Midcap", "Theo ngành"]
            )
        
        with col2:
            if stock_group == "Theo ngành":
                selected_sector = st.selectbox("Chọn ngành:", get_all_sectors())
                selected_symbols = get_stocks_by_sector(selected_sector)
            elif stock_group == "VN30":
                selected_symbols = VN30_STOCKS
            elif stock_group == "Midcap":
                selected_symbols = MIDCAP_STOCKS
            elif stock_group == "Top 100 (Đầy đủ)":
                selected_symbols = TOP_100_STOCKS
            else:  # Top 50
                selected_symbols = TOP_100_STOCKS[:50]
    
    # Hiển thị thông tin phạm vi quét
    if selected_symbols:
        st.info(f"📌 Sẽ quét **{len(selected_symbols)}** cổ phiếu: {', '.join(selected_symbols[:8])}{'...' if len(selected_symbols) > 8 else ''}")
    else:
        st.warning("⚠️ Vui lòng chọn hoặc nhập danh sách cổ phiếu để quét")
    
    st.markdown("---")
    st.markdown("### ⚙️ Tùy chọn lọc")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_confidence = st.slider(
            "Độ tin cậy tối thiểu (%):",
            min_value=50,
            max_value=100,
            value=70,
            step=5
        )
    
    with col2:
        signal_type = st.selectbox(
            "Loại tín hiệu:",
            ["Tín hiệu MUA", "Tín hiệu BÁN", "Cả hai"]
        )
    
    scan_btn = st.button("🔍 Quét ngay", type="primary", use_container_width=True, disabled=not selected_symbols)
    
    if scan_btn and selected_symbols:
        with st.spinner(f"Đang quét {len(selected_symbols)} cổ phiếu..."):
            # Sử dụng danh sách đã chọn
            batch = BatchAnalyzer(selected_symbols, max_workers=10)
            batch.analyze_batch()
            
            st.success("✅ Hoàn thành quét thị trường!")
            
            # Thu thập danh sách mã cổ phiếu theo tín hiệu
            buy_symbols = []
            sell_symbols = []
            all_symbols = []
            
            if signal_type in ["Tín hiệu MUA", "Cả hai"]:
                buy_signals = batch.get_buy_signals(min_confidence=min_confidence)
                if not buy_signals.empty:
                    buy_symbols = buy_signals['symbol'].tolist()
                    all_symbols.extend(buy_symbols)
            
            if signal_type in ["Tín hiệu BÁN", "Cả hai"]:
                sell_signals = batch.get_sell_signals(min_confidence=min_confidence)
                if not sell_signals.empty:
                    sell_symbols = sell_signals['symbol'].tolist()
                    all_symbols.extend(sell_symbols)
            
            # Hiển thị box copy danh sách
            if all_symbols:
                st.markdown("### 📋 Danh sách cổ phiếu phát hiện")
                st.caption("💡 Copy danh sách bên dưới để dán vào phần **Phân tích hàng loạt**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if buy_symbols:
                        st.markdown("**🟢 Tín hiệu MUA:**")
                        buy_list = ', '.join(buy_symbols)
                        st.code(buy_list, language=None)
                        st.caption(f"{len(buy_symbols)} cổ phiếu")
                
                with col2:
                    if sell_symbols:
                        st.markdown("**🔴 Tín hiệu BÁN:**")
                        sell_list = ', '.join(sell_symbols)
                        st.code(sell_list, language=None)
                        st.caption(f"{len(sell_symbols)} cổ phiếu")
                
                with col3:
                    if signal_type == "Cả hai" and buy_symbols and sell_symbols:
                        st.markdown("**📊 Tất cả:**")
                        all_list = ', '.join(buy_symbols + sell_symbols)
                        st.code(all_list, language=None)
                        st.caption(f"{len(buy_symbols) + len(sell_symbols)} cổ phiếu")
                
                st.markdown("---")
            
            # Chi tiết các tín hiệu MUA
            if signal_type in ["Tín hiệu MUA", "Cả hai"]:
                buy_signals = batch.get_buy_signals(min_confidence=min_confidence)
                
                if not buy_signals.empty:
                    st.markdown("### 🟢 Cơ hội MUA phát hiện:")
                    
                    for idx, row in buy_signals.head(20).iterrows():
                        with st.expander(f"✅ {row['symbol']} - {row['signal']} ({row['confidence']:.1f}%)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Giá", f"{row['price']:,.0f}")
                                st.metric("RSI", f"{row['rsi']:.2f}" if pd.notna(row['rsi']) else "N/A")
                            
                            with col2:
                                st.metric("Thay đổi", f"{row['price_change_pct']:+.2f}%")
                                st.metric("Độ tin cậy", f"{row['confidence']:.1f}%")
                            
                            with col3:
                                st.metric("Ngành", row['sector'])
                                st.metric("Điểm mua", f"{row['buy_score']:.0f}")
                else:
                    st.info(f"Không tìm thấy tín hiệu MUA với độ tin cậy >= {min_confidence}%")
            
            if signal_type in ["Tín hiệu BÁN", "Cả hai"]:
                sell_signals = batch.get_sell_signals(min_confidence=min_confidence)
                
                if not sell_signals.empty:
                    st.markdown("### 🔴 Cơ hội BÁN phát hiện:")
                    
                    for idx, row in sell_signals.head(20).iterrows():
                        with st.expander(f"❌ {row['symbol']} - {row['signal']} ({row['confidence']:.1f}%)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Giá", f"{row['price']:,.0f}")
                                st.metric("RSI", f"{row['rsi']:.2f}" if pd.notna(row['rsi']) else "N/A")
                            
                            with col2:
                                st.metric("Thay đổi", f"{row['price_change_pct']:+.2f}%")
                                st.metric("Độ tin cậy", f"{row['confidence']:.1f}%")
                            
                            with col3:
                                st.metric("Ngành", row['sector'])
                                st.metric("Điểm bán", f"{row['sell_score']:.0f}")
                else:
                    st.info(f"Không tìm thấy tín hiệu BÁN với độ tin cậy >= {min_confidence}%")

# Chế độ phân tích ngành
elif mode == "🏭 Phân tích ngành":
    st.header("🏭 Phân tích Các Nhóm Ngành")
    
    st.info("""
    📊 Phân tích khả năng mua/bán của 12 nhóm ngành chính trên thị trường Việt Nam.
    Giúp bạn xác định ngành nào đang mạnh, ngành nào đang yếu để đưa ra quyết định đầu tư phù hợp.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        days_back = st.slider("Số ngày phân tích", 30, 180, 90, 30)
    
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("📊 Phân tích ngành", type="primary", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("Đang phân tích các ngành... Vui lòng đợi trong giây lát..."):
            analyzer = SectorAnalyzer(days_back=days_back)
            results = analyzer.analyze_all_sectors()
            summary = analyzer.get_summary()
            ranked = analyzer.get_ranked_sectors()
            
            st.success("✅ Hoàn thành phân tích các ngành!")
            
            # Tổng quan
            st.markdown("### 📊 Tổng quan các ngành")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Tổng số ngành", summary['total_sectors'])
            with col2:
                st.metric("🟢 Ngành mạnh", summary['strong_count'])
            with col3:
                st.metric("🟡 Ngành trung bình", summary['medium_count'])
            with col4:
                st.metric("🔴 Ngành yếu", summary['weak_count'])
            
            # Hiển thị ngành tốt nhất và tệ nhất
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🏆 Ngành mạnh nhất: **{summary['best_sector']}**")
            with col2:
                st.error(f"⚠️ Ngành yếu nhất: **{summary['worst_sector']}**")
            
            st.markdown("---")
            
            # Bảng xếp hạng các ngành
            st.markdown("### 📈 Bảng xếp hạng các ngành")
            
            # Tạo DataFrame để hiển thị
            df_display = []
            for idx, (sector_name, data) in enumerate(ranked, 1):
                icon = '🟢' if data['status'] == 'MẠNH' else ('🟡' if data['status'] == 'TRUNG BÌNH' else '🔴')
                df_display.append({
                    'Hạng': idx,
                    'Icon': icon,
                    'Ngành': sector_name,
                    'Điểm': f"{data['score']:.1f}",
                    'Trạng thái': data['status'],
                    'Khuyến nghị': data['recommendation'],
                    'Số mã': data['stocks_analyzed']
                })
            
            df_ranked = pd.DataFrame(df_display)
            
            # Hiển thị bảng với màu sắc
            st.dataframe(
                df_ranked,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Hạng": st.column_config.NumberColumn("Hạng", width="content"),
                    "Icon": st.column_config.TextColumn("", width="content"),
                    "Ngành": st.column_config.TextColumn("Ngành", width="content"),
                    "Điểm": st.column_config.TextColumn("Điểm", width="content"),
                    "Trạng thái": st.column_config.TextColumn("Trạng thái", width="content"),
                    "Khuyến nghị": st.column_config.TextColumn("Khuyến nghị", width="content"),
                    "Số mã": st.column_config.NumberColumn("Số mã", width="content")
                }
            )
            
            st.markdown("---")
            
            # Chi tiết TOP 3 ngành mạnh nhất
            st.markdown("### 🎯 Chi tiết TOP 3 ngành mạnh nhất")
            
            for idx, (sector_name, data) in enumerate(ranked[:3], 1):
                with st.expander(f"#{idx} {sector_name} - Điểm: {data['score']:.1f} ({data['status']})", expanded=(idx==1)):
                    st.markdown(f"**Khuyến nghị:** {data['recommendation']}")
                    st.markdown(f"**Số mã phân tích:** {data['stocks_analyzed']}")
                    
                    # Hiển thị top 5 mã trong ngành
                    st.markdown("##### 📊 Top 5 mã cổ phiếu trong ngành:")
                    
                    stock_data = []
                    for stock in data['stock_details'][:5]:
                        stock_data.append({
                            'Mã': stock['symbol'],
                            'Điểm': f"{stock['score']:.0f}",
                            'Chi tiết': stock['details']
                        })
                    
                    df_stocks = pd.DataFrame(stock_data)
                    st.dataframe(df_stocks, use_container_width=True, hide_index=True)
            
            # Kết luận
            st.markdown("---")
            st.markdown("### 💡 Kết luận và khuyến nghị")
            
            if summary['strong_count'] >= 3:
                st.success(f"""
                ✅ **Thị trường tích cực:** Có {summary['strong_count']} ngành đang mạnh.
                
                **Khuyến nghị:** Đây là thời điểm tốt để tìm kiếm cơ hội đầu tư.
                
                **Ngành nên quan tâm:** {', '.join(summary['strong_sectors'][:3])}
                """)
            elif summary['weak_count'] >= summary['total_sectors'] * 0.6:
                st.error(f"""
                ⚠️ **Thị trường yếu:** Có {summary['weak_count']}/{summary['total_sectors']} ngành đang yếu.
                
                **Khuyến nghị:** Nên thận trọng khi đầu tư, ưu tiên bảo toàn vốn.
                
                **Ngành nên tránh:** {', '.join(summary['weak_sectors'][:3])}
                """)
            else:
                st.info(f"""
                📊 **Thị trường hỗn hợp:** Các ngành có xu hướng khác nhau.
                
                **Khuyến nghị:** Cần lựa chọn ngành cẩn thận, tập trung vào các ngành mạnh.
                
                **Ngành ưu tiên:** {', '.join(summary['strong_sectors'] if summary['strong_sectors'] else ['Chưa có ngành nổi bật'])}
                """)

# Chế độ Danh mục của tôi (Portfolio)
elif mode == "💼 Danh mục của tôi":
    st.header("💼 Danh Mục Đầu Tư Của Tôi")
    
    # Khởi tạo session state cho login
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None
    
    # Kiểm tra đăng nhập
    if st.session_state.logged_in_user is None:
        # Form đăng nhập
        st.markdown("### 🔐 Đăng nhập để truy cập danh mục")
        
        st.info("💡 Để bảo mật thông tin đầu tư của bạn, vui lòng đăng nhập trước khi truy cập danh mục.")
        
        # Load danh sách users
        users_config = load_users_config()
        users = users_config.get("users", {})
        
        # Kiểm tra nếu không có users
        if not users:
            st.error("⚠️ Không tìm thấy cấu hình users. Vui lòng tạo file users_config.json từ users_config.example.json")
            st.stop()
        
        # Tạo mapping: full_name -> username
        user_display = {user_data["full_name"]: username for username, user_data in users.items()}
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form"):
                st.markdown("#### 👤 Thông tin đăng nhập")
                
                # Dropdown chọn user theo full_name
                selected_display = st.selectbox(
                    "Tài khoản",
                    options=list(user_display.keys()),
                    index=0 if user_display else None,
                    help="Chọn tài khoản của bạn"
                )
                
                # Lấy username từ full_name
                username = user_display.get(selected_display) if selected_display else None
                
                password = st.text_input(
                    "Mật khẩu",
                    type="password",
                    placeholder="Nhập mật khẩu",
                    help="Nhập mật khẩu của bạn"
                )
                
                login_btn = st.form_submit_button("🔓 Đăng nhập", type="primary", use_container_width=True)
                
                if login_btn:
                    if not password:
                        st.error("⚠️ Vui lòng nhập mật khẩu!")
                    elif verify_login(username, password):
                        st.session_state.logged_in_user = username
                        st.success(f"✅ Đăng nhập thành công! Chào mừng {selected_display}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Mật khẩu không đúng!")
    
    else:
        # Đã đăng nhập - hiển thị portfolio
        current_user = st.session_state.logged_in_user
        user_info = get_user_info(current_user)
        
        # Header với nút logout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### 👤 Xin chào, **{user_info.get('full_name', current_user)}**!")
        
        with col2:
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state.logged_in_user = None
                st.success("✅ Đã đăng xuất!")
                time.sleep(0.5)
                st.rerun()
        
        st.markdown("---")
        
        # Khởi tạo Portfolio Manager
        pm = PortfolioManager(current_user)
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Tổng quan", "➕ Mua cổ phiếu", "💰 Bán cổ phiếu", "📋 Lịch sử", "⚠️ Cảnh báo bán"])
        
        # Tab 1: Tổng quan
        with tab1:
            st.markdown("### 📈 Tổng quan danh mục")
            
            summary = pm.get_portfolio_summary()
            
            if summary["total_stocks"] == 0:
                st.info("📭 Danh mục của bạn đang trống. Hãy thêm cổ phiếu ở tab **➕ Thêm cổ phiếu**")
            else:
                # Metrics tổng quan
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Tổng vốn đầu tư",
                        f"{summary['total_investment']:,.0f} VND",
                        help="Tổng số tiền đã đầu tư"
                    )
                
                with col2:
                    st.metric(
                        "Giá trị hiện tại",
                        f"{summary['total_current_value']:,.0f} VND",
                        help="Tổng giá trị danh mục hiện tại"
                    )
                
                with col3:
                    pnl_delta = f"{summary['total_pnl']:+,.0f} VND"
                    st.metric(
                        "Lãi/Lỗ",
                        pnl_delta,
                        delta=f"{summary['total_pnl_pct']:+.2f}%",
                        delta_color="normal"
                    )
                
                with col4:
                    st.metric(
                        "Số mã đang nắm",
                        f"{summary['total_stocks']} mã",
                        help="Tổng số mã cổ phiếu trong danh mục"
                    )
                
                st.markdown("---")
                
                # Bảng chi tiết P&L
                st.markdown("### 📊 Chi tiết từng mã")
                
                pnl_df = pm.calculate_pnl()
                
                if not pnl_df.empty:
                    # Format hiển thị
                    display_df = pnl_df.copy()
                    display_df = display_df[[
                        'symbol', 'quantity', 'buy_price', 'current_price', 
                        'investment', 'current_value', 'pnl', 'pnl_pct', 'buy_date'
                    ]]
                    
                    # Đổi tên cột
                    display_df.columns = [
                        'Mã CP', 'SL', 'Giá mua', 'Giá hiện tại',
                        'Vốn đầu tư', 'Giá trị HT', 'Lãi/Lỗ', 'ROI (%)', 'Ngày mua'
                    ]
                    
                    # Format số
                    display_df['Giá mua'] = display_df['Giá mua'].apply(lambda x: f"{x:,.1f}")
                    display_df['Giá hiện tại'] = display_df['Giá hiện tại'].apply(lambda x: f"{x:,.1f}")
                    display_df['Vốn đầu tư'] = display_df['Vốn đầu tư'].apply(lambda x: f"{x:,.0f}")
                    display_df['Giá trị HT'] = display_df['Giá trị HT'].apply(lambda x: f"{x:,.0f}")
                    display_df['Lãi/Lỗ'] = display_df['Lãi/Lỗ'].apply(lambda x: f"{x:+,.0f}")
                    display_df['ROI (%)'] = display_df['ROI (%)'].apply(lambda x: f"{x:+.2f}")
                    
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                    # Biểu đồ phân bổ
                    st.markdown("### 📊 Phân bổ danh mục")
                    
                    dist_df = pm.get_portfolio_distribution()
                    
                    if not dist_df.empty:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pie chart
                            fig = px.pie(
                                dist_df,
                                values='current_value',
                                names='symbol',
                                title='Phân bổ theo giá trị',
                                hole=0.4
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Bar chart P&L
                            fig = px.bar(
                                pnl_df.sort_values('pnl_pct', ascending=False),
                                x='symbol',
                                y='pnl_pct',
                                title='Lãi/Lỗ theo mã (%)',
                                color='pnl_pct',
                                color_continuous_scale=['red', 'yellow', 'green'],
                                labels={'pnl_pct': 'ROI (%)', 'symbol': 'Mã CP'}
                            )
                            fig.update_layout(showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Best/Worst performers
                    st.markdown("### 🏆 Hiệu suất nổi bật")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if summary['best_performer']:
                            best = summary['best_performer']
                            st.success(f"""
                            **🥇 Tốt nhất: {best['symbol']}**
                            - ROI: **{best['pnl_pct']:+.2f}%**
                            - Lãi: {best['pnl']:+,.0f} VND
                            - Giá mua: {best['buy_price']:,.1f} → Hiện tại: {best['current_price']:,.1f}
                            """)
                    
                    with col2:
                        if summary['worst_performer']:
                            worst = summary['worst_performer']
                            st.error(f"""
                            **📉 Kém nhất: {worst['symbol']}**
                            - ROI: **{worst['pnl_pct']:+.2f}%**
                            - Lỗ: {worst['pnl']:+,.0f} VND
                            - Giá mua: {worst['buy_price']:,.1f} → Hiện tại: {worst['current_price']:,.1f}
                            """)
        
        # Tab 2: Thêm cổ phiếu
        with tab2:
            st.markdown("### ➕ Thêm cổ phiếu vào danh mục")
            
            with st.form("add_stock_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    symbol = st.text_input(
                        "Mã cổ phiếu *",
                        placeholder="VD: VCB, VHM, HPG...",
                        help="Nhập mã cổ phiếu (viết hoa)"
                    ).upper()
                    
                    buy_price = st.number_input(
                        "Giá mua * (VND)",
                        min_value=0.0,
                        value=50000.0,
                        step=100.0,
                        help="Giá mua trung bình"
                    )
                
                with col2:
                    quantity = st.number_input(
                        "Số lượng *",
                        min_value=1,
                        value=100,
                        step=10,
                        help="Số lượng cổ phiếu"
                    )
                    
                    buy_date = st.date_input(
                        "Ngày mua *",
                        value=datetime.now(),
                        help="Ngày thực hiện giao dịch"
                    )
                
                notes = st.text_area(
                    "Ghi chú",
                    placeholder="VD: Mua khi RSI xuống 30, dự đoán tăng...",
                    help="Lý do mua hoặc ghi chú cá nhân"
                )
                
                submitted = st.form_submit_button("➕ Thêm vào danh mục", type="primary", use_container_width=True)
                
                if submitted:
                    if not symbol:
                        st.error("⚠️ Vui lòng nhập mã cổ phiếu!")
                    else:
                        try:
                            pm.add_stock(
                                symbol=symbol,
                                quantity=quantity,
                                buy_price=buy_price,
                                buy_date=buy_date.strftime("%Y-%m-%d"),
                                notes=notes
                            )
                            st.success(f"✅ Đã thêm **{quantity}** cổ phiếu **{symbol}** vào danh mục!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Lỗi: {e}")
        
        # Tab 3: Bán cổ phiếu
        with tab3:
            st.markdown("### 💰 Bán cổ phiếu")
            
            holdings_dict = pm._get_current_holdings()
            
            if not holdings_dict:
                st.info("📭 Bạn chưa có cổ phiếu nào để bán. Hãy mua ở tab **➕ Mua cổ phiếu**")
            else:
                st.markdown(f"Bạn đang nắm giữ **{len(holdings_dict)}** mã cổ phiếu")
                
                with st.form("sell_stock_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Dropdown chọn mã cổ phiếu từ holdings
                        symbol_options = list(holdings_dict.keys())
                        selected_symbol = st.selectbox(
                            "Chọn mã cổ phiếu cần bán *",
                            options=symbol_options,
                            help="Chọn mã cổ phiếu bạn đang nắm giữ"
                        )
                        
                        # Hiển thị thông tin hiện tại
                        if selected_symbol:
                            holding_info = holdings_dict[selected_symbol]
                            st.info(f"""
                            **Thông tin nắm giữ:**
                            - Số lượng: {holding_info['quantity']} cổ
                            - Giá mua TB: {holding_info['avg_price']:,.0f} VND
                            - Tổng vốn: {holding_info['total_cost']:,.0f} VND
                            """)
                        
                        quantity_sell = st.number_input(
                            "Số lượng bán *",
                            min_value=1,
                            max_value=holding_info['quantity'] if selected_symbol else 1,
                            value=min(100, holding_info['quantity'] if selected_symbol else 1),
                            step=10,
                            help=f"Tối đa: {holding_info['quantity'] if selected_symbol else 0} cổ"
                        )
                    
                    with col2:
                        sell_price = st.number_input(
                            "Giá bán * (VND)",
                            min_value=0.0,
                            value=holding_info['avg_price'] if selected_symbol else 50000.0,
                            step=100.0,
                            help="Giá bán thực tế"
                        )
                        
                        sell_date = st.date_input(
                            "Ngày bán *",
                            value=datetime.now(),
                            help="Ngày thực hiện giao dịch"
                        )
                        
                        # Tính P&L dự kiến
                        if selected_symbol:
                            estimated_pnl = (sell_price - holding_info['avg_price']) * quantity_sell
                            estimated_pnl_pct = (estimated_pnl / (holding_info['avg_price'] * quantity_sell)) * 100
                            
                            if estimated_pnl >= 0:
                                st.success(f"""
                                **💰 Lãi dự kiến:**
                                - {estimated_pnl:+,.0f} VND
                                - {estimated_pnl_pct:+.2f}%
                                """)
                            else:
                                st.error(f"""
                                **📉 Lỗ dự kiến:**
                                - {estimated_pnl:+,.0f} VND
                                - {estimated_pnl_pct:+.2f}%
                                """)
                    
                    notes_sell = st.text_area(
                        "Lý do bán (tùy chọn)",
                        placeholder="VD: Chốt lời, cắt lỗ, cần tiền...",
                        help="Ghi chú lý do bán"
                    )
                    
                    submitted_sell = st.form_submit_button("💰 Xác nhận bán", type="primary", use_container_width=True)
                    
                    if submitted_sell:
                        result = pm.sell_stock(
                            symbol=selected_symbol,
                            quantity=quantity_sell,
                            sell_price=sell_price,
                            sell_date=sell_date.strftime("%Y-%m-%d"),
                            notes=notes_sell
                        )
                        
                        if result["success"]:
                            if result["realized_pnl"] >= 0:
                                st.success(f"""
                                ✅ {result['message']}
                                
                                **💰 Kết quả:**
                                - Giá mua TB: {result['avg_buy_price']:,.0f} VND
                                - Lãi thực tế: **{result['realized_pnl']:+,.0f} VND**
                                """)
                            else:
                                st.warning(f"""
                                ✅ {result['message']}
                                
                                **📉 Kết quả:**
                                - Giá mua TB: {result['avg_buy_price']:,.0f} VND
                                - Lỗ thực tế: **{result['realized_pnl']:+,.0f} VND**
                                """)
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
        
        # Tab 4: Lịch sử giao dịch
        with tab4:
            st.markdown("### 📋 Lịch sử giao dịch")
            
            transactions = pm.get_transactions()
            
            if not transactions:
                st.info("📭 Chưa có giao dịch nào")
            else:
                st.markdown(f"Tổng số **{len(transactions)}** giao dịch")
                
                # Tạo DataFrame
                txn_df = pd.DataFrame(transactions)
                
                # Format hiển thị
                display_txn = txn_df[['timestamp', 'type', 'symbol', 'quantity', 'price', 'date', 'notes']].copy()
                display_txn.columns = ['Thời gian', 'Loại', 'Mã', 'SL', 'Giá', 'Ngày GD', 'Ghi chú']
                
                # Format giá
                display_txn['Giá'] = display_txn['Giá'].apply(lambda x: f"{x:,.0f}")
                
                # Màu sắc cho loại giao dịch
                display_txn['Loại'] = display_txn['Loại'].apply(
                    lambda x: '🟢 MUA' if x == 'buy' else '🔴 BÁN'
                )
                
                st.dataframe(display_txn, use_container_width=True, hide_index=True)
                
                # Thống kê tổng hợp
                st.markdown("### 📊 Thống kê")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_buy = len([t for t in transactions if t['type'] == 'buy'])
                    st.metric("Tổng số lần mua", total_buy)
                
                with col2:
                    total_sell = len([t for t in transactions if t['type'] == 'sell'])
                    st.metric("Tổng số lần bán", total_sell)
                
                with col3:
                    realized_pnl = pm.data.get("realized_pnl", 0)
                    st.metric(
                        "Lãi/Lỗ đã chốt",
                        f"{realized_pnl:+,.0f} VND",
                        delta=f"{(realized_pnl/1000000):.2f}M" if abs(realized_pnl) > 1000000 else None
                    )
        
        # Tab 5: Cảnh báo bán
        with tab5:
            st.markdown("### ⚠️ Cảnh báo tín hiệu bán")
            
            holdings = pm.get_holdings()
            
            if not holdings:
                st.info("📭 Danh mục trống. Hãy thêm cổ phiếu để nhận cảnh báo.")
            else:
                st.info("🔍 Đang kiểm tra tín hiệu bán cho các cổ phiếu trong danh mục...")
                
                with st.spinner("Đang phân tích..."):
                    sell_signals = pm.check_sell_signals()
                
                if sell_signals.empty:
                    st.success("✅ Hiện tại không có tín hiệu BÁN nào cho các cổ phiếu trong danh mục của bạn!")
                else:
                    st.warning(f"⚠️ Phát hiện **{len(sell_signals)}** tín hiệu BÁN trong danh mục!")
                    
                    st.markdown("---")
                    
                    for idx, row in sell_signals.iterrows():
                        pnl = (row['current_price'] - row['buy_price']) * row['quantity']
                        pnl_pct = (row['current_price'] - row['buy_price']) / row['buy_price'] * 100
                        
                        with st.expander(f"🔴 {row['symbol']} - {row['signal']} (Độ tin cậy: {row['confidence']:.1f}%)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Giá mua", f"{row['buy_price']:,.1f}")
                                st.metric("Số lượng", f"{row['quantity']}")
                            
                            with col2:
                                st.metric("Giá hiện tại", f"{row['current_price']:,.1f}")
                                st.metric("Độ tin cậy", f"{row['confidence']:.1f}%")
                            
                            with col3:
                                st.metric(
                                    "Lãi/Lỗ nếu bán", 
                                    f"{pnl:+,.0f} VND",
                                    delta=f"{pnl_pct:+.2f}%"
                                )
                                st.metric("Điểm bán", f"{row['sell_score']:.0f}")
                            
                            st.markdown("**💡 Khuyến nghị:**")
                            st.write(row.get('recommendation', 'Cân nhắc bán'))
                            
                            if st.button(f"📊 Xem chi tiết phân tích {row['symbol']}", key=f"detail_{row['symbol']}_{idx}"):
                                st.info(f"💡 Chuyển sang tab **🎯 Phân tích đơn lẻ** để xem chi tiết {row['symbol']}")
                    
                    st.markdown("---")
                    st.warning("""
                    ⚠️ **Lưu ý quan trọng:**
                    - Đây chỉ là tín hiệu kỹ thuật, không phải lời khuyên đầu tư
                    - Cân nhắc mục tiêu đầu tư, khẩu vị rủi ro và tình hình thị trường tổng thể
                    - Có thể giữ nếu còn tin tưởng vào triển vọng dài hạn của doanh nghiệp
                    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>⚠️ <strong>LƯU Ý QUAN TRỌNG:</strong> Đây chỉ là công cụ hỗ trợ phân tích kỹ thuật, không phải lời khuyên đầu tư.</p>
    <p>Hãy tự nghiên cứu kỹ và cân nhắc rủi ro trước khi đưa ra quyết định đầu tư.</p>
    <p style="margin-top: 1rem; font-size: 0.9rem;">Made with ❤️ for Vietnamese Stock Market</p>
</div>
""", unsafe_allow_html=True)
