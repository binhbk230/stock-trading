"""
Module phân tích hàng loạt nhiều cổ phiếu
"""
import pandas as pd
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from main import StockAnalyzer
from vnindex_analyzer import VNIndexAnalyzer
from top_stocks import TOP_100_STOCKS, get_sector


class BatchAnalyzer:
    """Lớp phân tích hàng loạt nhiều cổ phiếu"""
    
    def __init__(self, symbols=None, max_workers=5, check_vnindex=True):
        """
        Khởi tạo batch analyzer
        
        Args:
            symbols: List mã cổ phiếu cần phân tích (mặc định top 100)
            max_workers: Số luồng xử lý song song
            check_vnindex: Có kiểm tra VNINDEX hay không
        """
        self.symbols = symbols if symbols else TOP_100_STOCKS
        self.max_workers = max_workers
        self.results = []
        self.check_vnindex = check_vnindex
        self.vnindex_status = None
        
        # Lấy thông tin VNINDEX một lần (sử dụng interval 1D mặc định)
        if self.check_vnindex:
            try:
                vnindex = VNIndexAnalyzer(interval='1D')
                vnindex.fetch_data()
                self.vnindex_status = vnindex.get_summary()
            except:
                self.vnindex_status = None
    
    def analyze_single_stock(self, symbol, suppress_output=True):
        """
        Phân tích một mã cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu
            suppress_output: Ẩn output console
        
        Returns:
            Dictionary chứa kết quả phân tích
        """
        try:
            analyzer = StockAnalyzer(symbol, check_vnindex=False)  # Không check VNINDEX cho từng cổ phiếu
            
            # Lấy dữ liệu
            if analyzer.fetch_data() is None:
                return {
                    'symbol': symbol,
                    'status': 'error',
                    'error': 'Không lấy được dữ liệu'
                }
            
            # Tính toán chỉ báo
            analyzer.calculate_indicators()
            
            # Phân tích tín hiệu với VNINDEX status đã lấy sẵn
            from signal_generator import SignalGenerator
            analyzer.signal_gen = SignalGenerator(analyzer.indicators.df, self.vnindex_status, symbol=symbol)
            result = analyzer.signal_gen.get_overall_signal()
            
            if result is None:
                return {
                    'symbol': symbol,
                    'status': 'error',
                    'error': 'Lỗi phân tích'
                }
            
            # Lấy thông tin giá
            current_price = analyzer.data['close'].iloc[-1]
            prev_price = analyzer.data['close'].iloc[-2]
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100
            volume = analyzer.data['volume'].iloc[-1]
            
            # Lấy các chỉ số kỹ thuật
            latest = analyzer.indicators.get_latest_values()
            
            # Lấy điểm ngành nếu có
            sector_score = None
            sector_status = None
            if 'sector' in result:
                sector_score = result['sector'].get('score', None)
                sector_status = result['sector'].get('status', None)
            
            return {
                'symbol': symbol,
                'status': 'success',
                'sector': get_sector(symbol),
                'sector_score': sector_score,
                'sector_status': sector_status,
                'signal': result['signal'],
                'confidence': result['confidence'],
                'buy_score': result['buy_score'],
                'sell_score': result['sell_score'],
                'price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume': volume,
                'rsi': latest.get('rsi', None),
                'macd': latest.get('macd', None),
                'macd_signal': latest.get('macd_signal', None),
                'sma_20': latest.get('sma_20', None),
                'sma_50': latest.get('sma_50', None),
                'bb_upper': latest.get('bb_upper', None),
                'bb_lower': latest.get('bb_lower', None),
                'stoch_k': latest.get('stoch_k', None),
                'stoch_d': latest.get('stoch_d', None),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'vnindex_warning': result.get('vnindex_warning', None)
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_batch(self, progress_callback=None):
        """
        Phân tích hàng loạt với đa luồng
        
        Args:
            progress_callback: Hàm callback để cập nhật tiến độ
        
        Returns:
            List các kết quả phân tích
        """
        self.results = []
        total = len(self.symbols)
        completed = 0
        
        print(f"Bắt đầu phân tích {total} cổ phiếu...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tất cả các tasks
            future_to_symbol = {
                executor.submit(self.analyze_single_stock, symbol): symbol 
                for symbol in self.symbols
            }
            
            # Xử lý kết quả khi hoàn thành
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    completed += 1
                    
                    # Cập nhật tiến độ
                    if progress_callback:
                        progress_callback(completed, total, symbol)
                    else:
                        status = "✓" if result['status'] == 'success' else "✗"
                        print(f"{status} [{completed}/{total}] {symbol}")
                    
                except Exception as e:
                    print(f"✗ Lỗi khi phân tích {symbol}: {str(e)}")
                    self.results.append({
                        'symbol': symbol,
                        'status': 'error',
                        'error': str(e)
                    })
                    completed += 1
                
                # Delay nhỏ để tránh quá tải API
                time.sleep(0.1)
        
        print(f"\n✓ Hoàn thành phân tích {len(self.results)} cổ phiếu")
        return self.results
    
    def get_dataframe(self):
        """
        Chuyển kết quả thành DataFrame
        
        Returns:
            DataFrame chứa kết quả phân tích
        """
        if not self.results:
            return pd.DataFrame()
        
        # Lọc ra các kết quả thành công
        successful_results = [r for r in self.results if r['status'] == 'success']
        
        if not successful_results:
            return pd.DataFrame()
        
        df = pd.DataFrame(successful_results)
        
        # Sắp xếp theo confidence giảm dần
        if 'confidence' in df.columns:
            df = df.sort_values('confidence', ascending=False)
        
        return df
    
    def get_buy_signals(self, min_confidence=60):
        """
        Lọc các tín hiệu MUA
        
        Args:
            min_confidence: Độ tin cậy tối thiểu
        
        Returns:
            DataFrame các tín hiệu MUA
        """
        df = self.get_dataframe()
        
        if df.empty:
            return df
        
        # Lọc tín hiệu MUA với độ tin cậy >= min_confidence
        buy_signals = df[
            (df['signal'].str.contains('MUA', na=False)) & 
            (df['confidence'] >= min_confidence)
        ].copy()
        
        # Sắp xếp theo confidence giảm dần, nếu bằng nhau thì theo buy_score giảm dần
        return buy_signals.sort_values(['confidence', 'buy_score'], ascending=[False, False])
    
    def get_sell_signals(self, min_confidence=60):
        """
        Lọc các tín hiệu BÁN
        
        Args:
            min_confidence: Độ tin cậy tối thiểu
        
        Returns:
            DataFrame các tín hiệu BÁN
        """
        df = self.get_dataframe()
        
        if df.empty:
            return df
        
        # Lọc tín hiệu BÁN với độ tin cậy >= min_confidence
        sell_signals = df[
            (df['signal'].str.contains('BÁN', na=False)) & 
            (df['confidence'] >= min_confidence)
        ].copy()
        
        # Sắp xếp theo confidence giảm dần, nếu bằng nhau thì theo sell_score giảm dần
        return sell_signals.sort_values(['confidence', 'sell_score'], ascending=[False, False])
    
    def get_summary(self):
        """
        Tạo báo cáo tổng hợp
        
        Returns:
            Dictionary chứa thống kê tổng hợp
        """
        df = self.get_dataframe()
        
        if df.empty:
            return {
                'total': 0,
                'success': 0,
                'error': len([r for r in self.results if r['status'] == 'error'])
            }
        
        summary = {
            'total': len(self.results),
            'success': len(df),
            'error': len([r for r in self.results if r['status'] == 'error']),
            'buy_strong': len(df[df['signal'] == 'MUA MẠNH']),
            'buy': len(df[df['signal'] == 'MUA']),
            'sell_strong': len(df[df['signal'] == 'BÁN MẠNH']),
            'sell': len(df[df['signal'] == 'BÁN']),
            'neutral': len(df[df['signal'] == 'NEUTRAL']),
            'avg_confidence': df['confidence'].mean() if len(df) > 0 else 0,
            'top_buy': df[df['signal'].str.contains('MUA', na=False)].head(10)['symbol'].tolist() if len(df) > 0 else [],
            'top_sell': df[df['signal'].str.contains('BÁN', na=False)].head(10)['symbol'].tolist() if len(df) > 0 else []
        }
        
        return summary
    
    def save_to_excel(self, filename='stock_analysis_results.xlsx'):
        """
        Lưu kết quả ra file Excel
        
        Args:
            filename: Tên file Excel
        """
        df = self.get_dataframe()
        
        if df.empty:
            print("Không có dữ liệu để lưu")
            return
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet tất cả kết quả
            df.to_excel(writer, sheet_name='All Stocks', index=False)
            
            # Sheet tín hiệu MUA
            buy_signals = self.get_buy_signals()
            if not buy_signals.empty:
                buy_signals.to_excel(writer, sheet_name='Buy Signals', index=False)
            
            # Sheet tín hiệu BÁN
            sell_signals = self.get_sell_signals()
            if not sell_signals.empty:
                sell_signals.to_excel(writer, sheet_name='Sell Signals', index=False)
            
            # Sheet tóm tắt
            summary = self.get_summary()
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"✓ Đã lưu kết quả vào file: {filename}")


def quick_scan(symbols=None, min_confidence=60):
    """
    Quét nhanh và trả về các tín hiệu tốt
    
    Args:
        symbols: List mã cổ phiếu (mặc định top 100)
        min_confidence: Độ tin cậy tối thiểu
    
    Returns:
        Dictionary với tín hiệu MUA và BÁN
    """
    batch = BatchAnalyzer(symbols)
    batch.analyze_batch()
    
    return {
        'buy': batch.get_buy_signals(min_confidence),
        'sell': batch.get_sell_signals(min_confidence),
        'summary': batch.get_summary()
    }


if __name__ == "__main__":
    # Test với top 20 cổ phiếu
    test_symbols = TOP_100_STOCKS[:20]
    
    print("Test phân tích hàng loạt với 20 cổ phiếu đầu tiên...")
    batch = BatchAnalyzer(test_symbols, max_workers=3)
    batch.analyze_batch()
    
    # In tóm tắt
    summary = batch.get_summary()
    print("\n" + "="*80)
    print("TÓM TẮT KẾT QUẢ")
    print("="*80)
    print(f"Tổng số: {summary['total']}")
    print(f"Thành công: {summary['success']}")
    print(f"Lỗi: {summary['error']}")
    print(f"\nTín hiệu:")
    print(f"  MUA MẠNH: {summary['buy_strong']}")
    print(f"  MUA: {summary['buy']}")
    print(f"  BÁN MẠNH: {summary['sell_strong']}")
    print(f"  BÁN: {summary['sell']}")
    print(f"  NEUTRAL: {summary['neutral']}")
    print(f"\nĐộ tin cậy trung bình: {summary['avg_confidence']:.1f}%")
    
    # Lưu ra Excel
    batch.save_to_excel('test_results.xlsx')
