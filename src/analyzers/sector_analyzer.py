"""
Phân tích khả năng mua/bán của từng nhóm ngành trên thị trường chứng khoán Việt Nam
"""

from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.technical_indicators import TechnicalIndicators
from typing import Dict, List, Tuple
import warnings
import logging
warnings.filterwarnings('ignore')

# Giảm mức độ logging của vnstock
logging.getLogger('vnstock').setLevel(logging.WARNING)


class SectorAnalyzer:
    """
    Phân tích xu hướng và sức mạnh của các nhóm ngành
    """
    
    # Danh sách các nhóm ngành chính trên thị trường Việt Nam
    SECTORS = {
        'Ngân hàng': ['ACB', 'MBB', 'TCB', 'VCB', 'VPB', 'CTG', 'BID', 'STB', 'HDB'],
        'Chứng khoán': ['SSI', 'VCI', 'VND', 'HCM', 'FTS', 'SHS'],
        'Bất động sản': ['VHM', 'VIC', 'NVL', 'DXG', 'KDH', 'DIG', 'PDR'],
        'Bán lẻ': ['MWG', 'FRT', 'PNJ', 'DGW'],
        'Thép': ['HPG', 'HSG', 'NKG', 'TLH'],
        'Dầu khí': ['PVD', 'PVS', 'PVT', 'BSR', 'PLX'],
        'Điện': ['POW', 'NT2', 'PC1', 'REE'],
        'Vận tải & Logistics': ['GMD', 'HVN', 'VJC', 'VTP'],
        'Thực phẩm & Đồ uống': ['VNM', 'SAB', 'MSN', 'MCH', 'VHC'],
        'Dược phẩm': ['DHG', 'DMC', 'DVN', 'IMP'],
        'Công nghệ': ['FPT', 'CMG', 'VGI'],
        'Xây dựng': ['CTD', 'HBC', 'VCG', 'LCG'],
    }
    
    def __init__(self, days_back=90):
        """
        Khởi tạo SectorAnalyzer
        
        Args:
            days_back: Số ngày lịch sử để phân tích (mặc định 90 ngày)
        """
        self.days_back = days_back
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=days_back)
        self.sector_results = {}
        
    def _fetch_stock_data(self, symbol: str) -> pd.DataFrame:
        """Lấy dữ liệu lịch sử của một mã cổ phiếu"""
        try:
            # Sử dụng Vnstock nhưng tắt company check
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            
            # Chỉ lấy dữ liệu quote, không cần company info
            df = stock.quote.history(
                start=self.start_date.strftime('%Y-%m-%d'),
                end=self.end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )
            
            if df is not None and len(df) > 0:
                # Chuẩn hóa tên cột về lowercase
                df.columns = df.columns.str.lower()
                print(f"  ✓ {symbol}: {len(df)} ngày")
                return df
            print(f"  ✗ {symbol}: Rỗng")
            return None
        except Exception as e:
            error_msg = str(e)
            # Bỏ qua các lỗi không quan trọng
            if any(skip in error_msg.lower() for skip in ['not a stock', 'not found', 'invalid', 'company']):
                return None
            print(f"  ✗ {symbol}: {error_msg[:50]}")
            return None
    
    def _analyze_stock_trend(self, df: pd.DataFrame) -> Dict:
        """
        Phân tích xu hướng của một cổ phiếu
        Returns: Dict với score và chi tiết
        """
        if df is None or len(df) < 20:
            return {'score': 0, 'details': 'Không đủ dữ liệu'}
        
        try:
            indicators = TechnicalIndicators(df)
            score = 0
            details = []
            
            # 1. RSI (20 điểm)
            rsi = indicators.calculate_rsi()
            if not rsi.empty:
                latest_rsi = rsi.iloc[-1]
                if 40 <= latest_rsi <= 60:
                    score += 20
                    details.append(f"RSI trung lập ({latest_rsi:.1f})")
                elif latest_rsi < 30:
                    score += 10
                    details.append(f"RSI quá bán ({latest_rsi:.1f})")
                elif 30 <= latest_rsi < 40:
                    score += 15
                    details.append(f"RSI tích cực ({latest_rsi:.1f})")
                elif 60 < latest_rsi <= 70:
                    score += 15
                    details.append(f"RSI mạnh ({latest_rsi:.1f})")
                else:
                    score += 5
                    details.append(f"RSI quá mua ({latest_rsi:.1f})")
            
            # 2. MACD (20 điểm)
            macd_line, signal_line, macd_diff = indicators.calculate_macd()
            if not macd_line.empty and not signal_line.empty:
                if macd_line.iloc[-1] > signal_line.iloc[-1]:
                    score += 20
                    details.append("MACD tích cực")
                elif macd_line.iloc[-1] > signal_line.iloc[-1] * 0.9:
                    score += 10
                    details.append("MACD trung lập")
                else:
                    details.append("MACD tiêu cực")
            
            # 3. MA Crossover (20 điểm)
            smas = indicators.calculate_moving_averages([20, 50])
            if 'sma_20' in smas and 'sma_50' in smas:
                ma20 = smas['sma_20']
                ma50 = smas['sma_50']
                if not ma20.empty and not ma50.empty:
                    if ma20.iloc[-1] > ma50.iloc[-1]:
                        score += 20
                        details.append("MA20 > MA50")
                    elif ma20.iloc[-1] > ma50.iloc[-1] * 0.98:
                        score += 10
                        details.append("MA20 ≈ MA50")
                    else:
                        details.append("MA20 < MA50")
            
            # 4. Xu hướng giá (20 điểm)
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20] * 100
            if price_change > 5:
                score += 20
                details.append(f"Tăng {price_change:.1f}%")
            elif price_change > 0:
                score += 15
                details.append(f"Tăng nhẹ {price_change:.1f}%")
            elif price_change > -5:
                score += 10
                details.append(f"Giảm nhẹ {price_change:.1f}%")
            else:
                score += 5
                details.append(f"Giảm {price_change:.1f}%")
            
            # 5. Volume (20 điểm)
            avg_volume_20 = df['volume'].iloc[-20:].mean()
            avg_volume_50 = df['volume'].iloc[-50:].mean() if len(df) >= 50 else avg_volume_20
            if avg_volume_20 > avg_volume_50 * 1.2:
                score += 20
                details.append("Volume tăng mạnh")
            elif avg_volume_20 > avg_volume_50:
                score += 15
                details.append("Volume tăng")
            else:
                score += 10
                details.append("Volume bình thường")
            
            return {
                'score': score,
                'details': ' | '.join(details)
            }
            
        except Exception as e:
            return {'score': 0, 'details': f'Lỗi: {str(e)}'}
    
    def analyze_sector(self, sector_name: str, symbols: List[str]) -> Dict:
        """
        Phân tích một nhóm ngành
        
        Args:
            sector_name: Tên nhóm ngành
            symbols: Danh sách mã cổ phiếu trong ngành
            
        Returns:
            Dict chứa điểm số và chi tiết của ngành
        """
        print(f"\n🔍 Đang phân tích ngành: {sector_name}...")
        
        scores = []
        stock_details = []
        
        for symbol in symbols:
            df = self._fetch_stock_data(symbol)
            if df is not None and len(df) > 0:
                result = self._analyze_stock_trend(df)
                scores.append(result['score'])
                stock_details.append({
                    'symbol': symbol,
                    'score': result['score'],
                    'details': result['details']
                })
                print(f"    {symbol}: {result['score']:.0f} điểm - {result['details'][:50]}...")
        
        print(f"  → Tổng: {len(scores)}/{len(symbols)} mã có dữ liệu")
        
        if not scores:
            return {
                'sector': sector_name,
                'score': 0,
                'status': 'KHÔNG CÓ DỮ LIỆU',
                'recommendation': 'CHỜ DỮ LIỆU',
                'stocks_analyzed': 0,
                'stock_details': []
            }
        
        # Tính điểm trung bình của ngành
        avg_score = np.mean(scores)
        
        # Xác định trạng thái
        if avg_score >= 70:
            status = 'MẠNH'
            recommendation = 'NÊN MUA'
        elif avg_score >= 50:
            status = 'TRUNG BÌNH'
            recommendation = 'THEO DÕI'
        else:
            status = 'YẾU'
            recommendation = 'TRÁNH MUA'
        
        return {
            'sector': sector_name,
            'score': avg_score,
            'status': status,
            'recommendation': recommendation,
            'stocks_analyzed': len(scores),
            'stock_details': sorted(stock_details, key=lambda x: x['score'], reverse=True)
        }
    
    def analyze_all_sectors(self) -> Dict[str, Dict]:
        """
        Phân tích tất cả các nhóm ngành
        
        Returns:
            Dict với key là tên ngành, value là kết quả phân tích
        """
        print("=" * 80)
        print("📊 BẮT ĐẦU PHÂN TÍCH CÁC NHÓM NGÀNH")
        print("=" * 80)
        
        results = {}
        
        for sector_name, symbols in self.SECTORS.items():
            result = self.analyze_sector(sector_name, symbols)
            results[sector_name] = result
        
        self.sector_results = results
        return results
    
    def get_ranked_sectors(self) -> List[Tuple[str, Dict]]:
        """
        Lấy danh sách các ngành đã được xếp hạng theo điểm số
        
        Returns:
            List of tuples (sector_name, sector_data) sorted by score
        """
        if not self.sector_results:
            self.analyze_all_sectors()
        
        return sorted(
            self.sector_results.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
    
    def get_summary(self) -> Dict:
        """
        Lấy tóm tắt phân tích các ngành
        
        Returns:
            Dict chứa thống kê tổng quan
        """
        if not self.sector_results:
            self.analyze_all_sectors()
        
        strong_sectors = [s for s, d in self.sector_results.items() if d['status'] == 'MẠNH']
        medium_sectors = [s for s, d in self.sector_results.items() if d['status'] == 'TRUNG BÌNH']
        weak_sectors = [s for s, d in self.sector_results.items() if d['status'] == 'YẾU']
        
        return {
            'total_sectors': len(self.sector_results),
            'strong_count': len(strong_sectors),
            'medium_count': len(medium_sectors),
            'weak_count': len(weak_sectors),
            'strong_sectors': strong_sectors,
            'medium_sectors': medium_sectors,
            'weak_sectors': weak_sectors,
            'best_sector': max(self.sector_results.items(), key=lambda x: x[1]['score'])[0] if self.sector_results else None,
            'worst_sector': min(self.sector_results.items(), key=lambda x: x[1]['score'])[0] if self.sector_results else None
        }
    
    def print_summary(self):
        """In tóm tắt phân tích các ngành"""
        summary = self.get_summary()
        ranked = self.get_ranked_sectors()
        
        print("\n" + "=" * 80)
        print("📊 TÓM TẮT PHÂN TÍCH CÁC NHÓM NGÀNH")
        print("=" * 80)
        print(f"Tổng số ngành: {summary['total_sectors']}")
        print(f"  🟢 Mạnh: {summary['strong_count']} ngành")
        print(f"  🟡 Trung bình: {summary['medium_count']} ngành")
        print(f"  🔴 Yếu: {summary['weak_count']} ngành")
        print(f"\n🏆 Ngành mạnh nhất: {summary['best_sector']}")
        print(f"⚠️ Ngành yếu nhất: {summary['worst_sector']}")
        
        print("\n" + "=" * 80)
        print("📈 BẢNG XẾP HẠNG CÁC NGÀNH")
        print("=" * 80)
        print(f"{'#':<4} {'Ngành':<25} {'Điểm':<8} {'Trạng thái':<15} {'Khuyến nghị':<15}")
        print("-" * 80)
        
        for idx, (sector_name, data) in enumerate(ranked, 1):
            icon = '🟢' if data['status'] == 'MẠNH' else ('🟡' if data['status'] == 'TRUNG BÌNH' else '🔴')
            print(f"{idx:<4} {icon} {sector_name:<23} {data['score']:<7.1f} {data['status']:<15} {data['recommendation']:<15}")
        
        print("=" * 80)
        
        # Hiển thị chi tiết TOP 3 ngành mạnh nhất
        print("\n🎯 CHI TIẾT TOP 3 NGÀNH MẠNH NHẤT:")
        print("=" * 80)
        for idx, (sector_name, data) in enumerate(ranked[:3], 1):
            print(f"\n{idx}. {sector_name} - Điểm: {data['score']:.1f} ({data['status']})")
            print(f"   Khuyến nghị: {data['recommendation']}")
            print(f"   Phân tích {data['stocks_analyzed']} mã:")
            for stock in data['stock_details'][:5]:  # Hiển thị top 5 mã trong ngành
                print(f"     • {stock['symbol']}: {stock['score']:.0f} điểm - {stock['details']}")
        
        print("\n" + "=" * 80)


def main():
    """Test module phân tích ngành"""
    analyzer = SectorAnalyzer(days_back=90)
    
    # Phân tích tất cả các ngành
    analyzer.analyze_all_sectors()
    
    # In tóm tắt
    analyzer.print_summary()
    
    # Lấy thông tin chi tiết
    summary = analyzer.get_summary()
    print(f"\n💡 Kết luận:")
    if summary['strong_count'] >= 3:
        print("✅ Thị trường có nhiều ngành mạnh, đây là thời điểm tốt để tìm kiếm cơ hội đầu tư.")
        print(f"   Tập trung vào: {', '.join(summary['strong_sectors'][:3])}")
    elif summary['weak_count'] >= len(summary['total_sectors']) * 0.6:
        print("⚠️ Đa số ngành đang yếu, nên thận trọng khi đầu tư.")
        print(f"   Tránh: {', '.join(summary['weak_sectors'][:3])}")
    else:
        print("📊 Thị trường hỗn hợp, cần lựa chọn ngành cẩn thận.")
        print(f"   Ưu tiên: {', '.join(summary['strong_sectors'])}")


if __name__ == '__main__':
    main()
