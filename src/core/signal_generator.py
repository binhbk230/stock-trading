"""
Module sinh tín hiệu mua/bán dựa trên các chỉ báo kỹ thuật
"""
import pandas as pd
import numpy as np
from src.utils.top_stocks import get_sector, SECTOR_MAPPING


class SignalGenerator:
    """Lớp sinh tín hiệu giao dịch dựa trên phân tích kỹ thuật"""
    
    def __init__(self, df, vnindex_status=None, symbol=None):
        """
        Khởi tạo với DataFrame chứa dữ liệu và các chỉ báo
        
        Args:
            df: DataFrame với giá và các chỉ báo kỹ thuật
            vnindex_status: Dictionary chứa thông tin phân tích VNINDEX (tùy chọn)
            symbol: Mã cổ phiếu để tính điểm ngành (tùy chọn)
        """
        self.df = df.copy()
        self.signals = {}
        self.vnindex_status = vnindex_status
        self.symbol = symbol
        self.sector_score = None
    
    def analyze_rsi(self, oversold=30, overbought=70):
        """
        Phân tích tín hiệu từ RSI
        
        Args:
            oversold: Ngưỡng quá bán (mặc định 30)
            overbought: Ngưỡng quá mua (mặc định 70)
        
        Returns:
            Dictionary chứa tín hiệu và điểm số
        """
        if 'rsi' not in self.df.columns:
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Không có dữ liệu RSI'}
        
        rsi = self.df['rsi'].iloc[-1]
        
        if pd.isna(rsi):
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'RSI không hợp lệ'}
        
        if rsi < oversold:
            score = min((oversold - rsi) / oversold * 100, 100)
            return {
                'signal': 'MUA',
                'score': score,
                'reason': f'RSI = {rsi:.2f} (Quá bán, < {oversold})',
                'value': rsi
            }
        elif rsi > overbought:
            score = min((rsi - overbought) / (100 - overbought) * 100, 100)
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': f'RSI = {rsi:.2f} (Quá mua, > {overbought})',
                'value': rsi
            }
        else:
            return {
                'signal': 'NEUTRAL',
                'score': 0,
                'reason': f'RSI = {rsi:.2f} (Trong vùng trung lập)',
                'value': rsi
            }
    
    def analyze_macd(self):
        """
        Phân tích tín hiệu từ MACD
        
        Returns:
            Dictionary chứa tín hiệu và điểm số
        """
        if 'macd' not in self.df.columns or 'macd_signal' not in self.df.columns:
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Không có dữ liệu MACD'}
        
        macd = self.df['macd'].iloc[-1]
        signal = self.df['macd_signal'].iloc[-1]
        macd_prev = self.df['macd'].iloc[-2] if len(self.df) > 1 else macd
        signal_prev = self.df['macd_signal'].iloc[-2] if len(self.df) > 1 else signal
        
        if pd.isna(macd) or pd.isna(signal):
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'MACD không hợp lệ'}
        
        # Kiểm tra cắt lên (Golden Cross)
        if macd_prev <= signal_prev and macd > signal:
            score = 80
            return {
                'signal': 'MUA',
                'score': score,
                'reason': f'MACD cắt lên Signal (Golden Cross)',
                'macd': macd,
                'macd_signal': signal
            }
        # Kiểm tra cắt xuống (Death Cross)
        elif macd_prev >= signal_prev and macd < signal:
            score = 80
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': f'MACD cắt xuống Signal (Death Cross)',
                'macd': macd,
                'macd_signal': signal
            }
        # MACD ở trên Signal
        elif macd > signal:
            score = min(abs(macd - signal) * 10, 60)
            return {
                'signal': 'MUA',
                'score': score,
                'reason': f'MACD > Signal (Xu hướng tăng)',
                'macd': macd,
                'macd_signal': signal
            }
        # MACD ở dưới Signal
        else:
            score = min(abs(macd - signal) * 10, 60)
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': f'MACD < Signal (Xu hướng giảm)',
                'macd': macd,
                'macd_signal': signal
            }
    
    def analyze_moving_averages(self):
        """
        Phân tích tín hiệu từ các đường trung bình động
        
        Returns:
            Dictionary chứa tín hiệu và điểm số
        """
        price = self.df['close'].iloc[-1]
        signals = []
        
        # Kiểm tra các SMA
        for col in ['sma_20', 'sma_50', 'sma_200']:
            if col in self.df.columns:
                ma = self.df[col].iloc[-1]
                if not pd.isna(ma):
                    if price > ma:
                        signals.append(('MUA', col))
                    else:
                        signals.append(('BÁN', col))
        
        if not signals:
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Không có dữ liệu MA'}
        
        buy_count = sum(1 for s in signals if s[0] == 'MUA')
        sell_count = len(signals) - buy_count
        
        if buy_count > sell_count:
            score = (buy_count / len(signals)) * 70
            return {
                'signal': 'MUA',
                'score': score,
                'reason': f'Giá trên {buy_count}/{len(signals)} đường MA',
                'price': price
            }
        elif sell_count > buy_count:
            score = (sell_count / len(signals)) * 70
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': f'Giá dưới {sell_count}/{len(signals)} đường MA',
                'price': price
            }
        else:
            return {
                'signal': 'NEUTRAL',
                'score': 0,
                'reason': 'Giá ở giữa các đường MA',
                'price': price
            }
    
    def analyze_bollinger_bands(self):
        """
        Phân tích tín hiệu từ Bollinger Bands
        
        Returns:
            Dictionary chứa tín hiệu và điểm số
        """
        if 'bb_upper' not in self.df.columns or 'bb_lower' not in self.df.columns:
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Không có dữ liệu Bollinger Bands'}
        
        price = self.df['close'].iloc[-1]
        upper = self.df['bb_upper'].iloc[-1]
        lower = self.df['bb_lower'].iloc[-1]
        middle = self.df['bb_middle'].iloc[-1]
        
        if pd.isna(upper) or pd.isna(lower):
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'BB không hợp lệ'}
        
        band_width = upper - lower
        distance_from_lower = price - lower
        distance_from_upper = upper - price
        
        # Giá chạm hoặc gần dải dưới
        if distance_from_lower / band_width < 0.1:
            score = 75
            return {
                'signal': 'MUA',
                'score': score,
                'reason': 'Giá gần dải dưới BB (Oversold)',
                'price': price,
                'bb_lower': lower
            }
        # Giá chạm hoặc gần dải trên
        elif distance_from_upper / band_width < 0.1:
            score = 75
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': 'Giá gần dải trên BB (Overbought)',
                'price': price,
                'bb_upper': upper
            }
        # Giá trên đường giữa
        elif price > middle:
            score = 40
            return {
                'signal': 'MUA',
                'score': score,
                'reason': 'Giá trên đường giữa BB',
                'price': price,
                'bb_middle': middle
            }
        # Giá dưới đường giữa
        else:
            score = 40
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': 'Giá dưới đường giữa BB',
                'price': price,
                'bb_middle': middle
            }
    
    def analyze_stochastic(self, oversold=20, overbought=80):
        """
        Phân tích tín hiệu từ Stochastic Oscillator
        
        Args:
            oversold: Ngưỡng quá bán (mặc định 20)
            overbought: Ngưỡng quá mua (mặc định 80)
        
        Returns:
            Dictionary chứa tín hiệu và điểm số
        """
        if 'stoch_k' not in self.df.columns or 'stoch_d' not in self.df.columns:
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Không có dữ liệu Stochastic'}
        
        k = self.df['stoch_k'].iloc[-1]
        d = self.df['stoch_d'].iloc[-1]
        
        if pd.isna(k) or pd.isna(d):
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Stochastic không hợp lệ'}
        
        # Quá bán
        if k < oversold and d < oversold:
            score = min((oversold - k) / oversold * 100, 100)
            return {
                'signal': 'MUA',
                'score': score,
                'reason': f'Stochastic quá bán (%K={k:.2f}, %D={d:.2f})',
                'k': k,
                'd': d
            }
        # Quá mua
        elif k > overbought and d > overbought:
            score = min((k - overbought) / (100 - overbought) * 100, 100)
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': f'Stochastic quá mua (%K={k:.2f}, %D={d:.2f})',
                'k': k,
                'd': d
            }
        # %K cắt lên %D
        elif len(self.df) > 1:
            k_prev = self.df['stoch_k'].iloc[-2]
            d_prev = self.df['stoch_d'].iloc[-2]
            
            if k_prev <= d_prev and k > d:
                return {
                    'signal': 'MUA',
                    'score': 70,
                    'reason': '%K cắt lên %D (Golden Cross)',
                    'k': k,
                    'd': d
                }
            elif k_prev >= d_prev and k < d:
                return {
                    'signal': 'BÁN',
                    'score': 70,
                    'reason': '%K cắt xuống %D (Death Cross)',
                    'k': k,
                    'd': d
                }
        
        return {
            'signal': 'NEUTRAL',
            'score': 0,
            'reason': f'Stochastic trung lập (%K={k:.2f}, %D={d:.2f})',
            'k': k,
            'd': d
        }
    
    def analyze_volume(self):
        """
        Phân tích tín hiệu từ khối lượng giao dịch
        
        Returns:
            Dictionary chứa tín hiệu và điểm số
        """
        if len(self.df) < 20:
            return {'signal': 'NEUTRAL', 'score': 0, 'reason': 'Không đủ dữ liệu volume'}
        
        current_volume = self.df['volume'].iloc[-1]
        avg_volume = self.df['volume'].iloc[-20:].mean()
        current_price = self.df['close'].iloc[-1]
        prev_price = self.df['close'].iloc[-2]
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Khối lượng tăng mạnh và giá tăng
        if volume_ratio > 1.5 and current_price > prev_price:
            score = min(volume_ratio * 30, 70)
            return {
                'signal': 'MUA',
                'score': score,
                'reason': f'Khối lượng tăng mạnh ({volume_ratio:.1f}x) + giá tăng',
                'volume_ratio': volume_ratio
            }
        # Khối lượng tăng mạnh và giá giảm
        elif volume_ratio > 1.5 and current_price < prev_price:
            score = min(volume_ratio * 30, 70)
            return {
                'signal': 'BÁN',
                'score': score,
                'reason': f'Khối lượng tăng mạnh ({volume_ratio:.1f}x) + giá giảm',
                'volume_ratio': volume_ratio
            }
        else:
            return {
                'signal': 'NEUTRAL',
                'score': 0,
                'reason': f'Khối lượng bình thường ({volume_ratio:.1f}x)',
                'volume_ratio': volume_ratio
            }
    
    def calculate_sector_score(self):
        """
        Tính điểm ngành dựa trên phân tích các cổ phiếu cùng ngành
        
        Returns:
            Dictionary chứa điểm số và trạng thái ngành
        """
        if not self.symbol:
            return {
                'score': 50,  # Trung lập nếu không có symbol
                'status': 'TRUNG LẬP',
                'sector': 'N/A',
                'reason': 'Không xác định được ngành'
            }
        
        sector = get_sector(self.symbol)
        sector_stocks = SECTOR_MAPPING.get(sector, [])
        
        if not sector_stocks:
            return {
                'score': 50,
                'status': 'TRUNG LẬP',
                'sector': sector,
                'reason': 'Ngành không có dữ liệu'
            }
        
        # Tính điểm tương đối trong ngành dựa trên các chỉ báo của cổ phiếu hiện tại
        score = 50  # Baseline
        reasons = []
        
        # 1. RSI so với vùng lý tưởng (20 điểm)
        if 'rsi' in self.df.columns and not pd.isna(self.df['rsi'].iloc[-1]):
            rsi = self.df['rsi'].iloc[-1]
            if 40 <= rsi <= 60:
                score += 15
                reasons.append("RSI tốt trong ngành")
            elif 30 <= rsi < 40:
                score += 10
                reasons.append("RSI khả quan")
            elif rsi < 30:
                score += 5
                reasons.append("RSI yếu so với ngành")
        
        # 2. MACD tích cực (15 điểm)
        if 'macd' in self.df.columns and 'macd_signal' in self.df.columns:
            macd = self.df['macd'].iloc[-1]
            signal = self.df['macd_signal'].iloc[-1]
            if not pd.isna(macd) and not pd.isna(signal):
                if macd > signal and macd > 0:
                    score += 15
                    reasons.append("MACD mạnh trong ngành")
                elif macd > signal:
                    score += 10
                    reasons.append("MACD khả quan")
                else:
                    score -= 5
                    reasons.append("MACD yếu")
        
        # 3. Xu hướng giá (15 điểm)
        if len(self.df) >= 20:
            price_change_20d = (self.df['close'].iloc[-1] - self.df['close'].iloc[-20]) / self.df['close'].iloc[-20] * 100
            if price_change_20d > 10:
                score += 15
                reasons.append(f"Outperform ngành (+{price_change_20d:.1f}%)")
            elif price_change_20d > 5:
                score += 10
                reasons.append(f"Tăng tốt (+{price_change_20d:.1f}%)")
            elif price_change_20d > 0:
                score += 5
                reasons.append(f"Tăng nhẹ (+{price_change_20d:.1f}%)")
            elif price_change_20d > -5:
                score -= 5
                reasons.append(f"Giảm nhẹ ({price_change_20d:.1f}%)")
            else:
                score -= 10
                reasons.append(f"Underperform ngành ({price_change_20d:.1f}%)")
        
        # 4. Volume (10 điểm)
        if len(self.df) >= 20:
            current_volume = self.df['volume'].iloc[-1]
            avg_volume = self.df['volume'].iloc[-20:].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:
                score += 10
                reasons.append(f"Thanh khoản cao ({volume_ratio:.1f}x)")
            elif volume_ratio > 1.0:
                score += 5
                reasons.append("Thanh khoản ổn định")
            else:
                score -= 5
                reasons.append(f"Thanh khoản thấp ({volume_ratio:.1f}x)")
        
        # Chuẩn hóa điểm về khoảng 0-100
        score = max(0, min(100, score))
        
        # Xác định trạng thái
        if score >= 70:
            status = 'MẠNH'
        elif score >= 55:
            status = 'TRUNG BÌNH KHỐI'
        elif score >= 40:
            status = 'TRUNG LẬP'
        else:
            status = 'YẾU'
        
        self.sector_score = {
            'score': round(score, 1),
            'status': status,
            'sector': sector,
            'reason': ' | '.join(reasons) if reasons else 'Phân tích cơ bản'
        }
        
        return self.sector_score

    def generate_signals(self):
        """
        Tổng hợp tất cả các tín hiệu
        
        Returns:
            Dictionary chứa tất cả các tín hiệu và điểm tổng hợp
        """
        self.signals = {
            'rsi': self.analyze_rsi(),
            'macd': self.analyze_macd(),
            'ma': self.analyze_moving_averages(),
            'bollinger': self.analyze_bollinger_bands(),
            'stochastic': self.analyze_stochastic(),
            'volume': self.analyze_volume()
        }
        
        return self.signals
    
    def get_overall_signal(self):
        """
        Tính toán tín hiệu tổng hợp (có tích hợp phân tích VNINDEX)
        
        Returns:
            Dictionary chứa tín hiệu tổng hợp và điểm số
        """
        if not self.signals:
            self.generate_signals()
        
        buy_score = 0
        sell_score = 0
        neutral_count = 0
        buy_indicators = []
        sell_indicators = []
        
        for indicator, signal_data in self.signals.items():
            if signal_data['signal'] == 'MUA':
                buy_score += signal_data['score']
                buy_indicators.append(indicator)
            elif signal_data['signal'] == 'BÁN':
                sell_score += signal_data['score']
                sell_indicators.append(indicator)
            else:
                neutral_count += 1
        
        total_score = buy_score + sell_score
        total_indicators = len(self.signals)
        
        # Xác định tín hiệu ban đầu
        if total_score == 0:
            final_signal = 'NEUTRAL'
            confidence = 0
        else:
            buy_percentage = (buy_score / total_score) * 100
            sell_percentage = (sell_score / total_score) * 100
            
            # Xác định tín hiệu chính với base confidence có gradient
            if buy_percentage > 60:
                final_signal = 'MUA MẠNH'
                # Gradient: 60% -> 70, 80% -> 85, 100% -> 100
                base_confidence = 70 + (buy_percentage - 60) / 40 * 30
                active_count = len(buy_indicators)
            elif buy_percentage > 50:
                final_signal = 'MUA'
                # Gradient: 50% -> 60, 60% -> 70
                base_confidence = 60 + (buy_percentage - 50) / 10 * 10
                active_count = len(buy_indicators)
            elif sell_percentage > 60:
                final_signal = 'BÁN MẠNH'
                # Gradient: 60% -> 70, 80% -> 85, 100% -> 100
                base_confidence = 70 + (sell_percentage - 60) / 40 * 30
                active_count = len(sell_indicators)
            elif sell_percentage > 50:
                final_signal = 'BÁN'
                # Gradient: 50% -> 60, 60% -> 70
                base_confidence = 60 + (sell_percentage - 50) / 10 * 10
                active_count = len(sell_indicators)
            else:
                final_signal = 'NEUTRAL'
                base_confidence = 50
                active_count = 0
            
            # === CẢI TIẾN CONFIDENCE ===
            # 1. Điều chỉnh dựa trên số lượng indicator đồng thuận (weight: 15%)
            consensus_ratio = active_count / total_indicators  # 0-1
            consensus_adjustment = consensus_ratio * 15  # 0-15 điểm
            
            # 2. Phạt neutral indicators (mỗi neutral giảm 3%)
            neutral_penalty = neutral_count * 3  # Mỗi neutral trừ 3 điểm
            
            # 3. Tính average score per indicator (phản ánh strength) - QUAN TRỌNG
            if active_count > 0:
                avg_score_per_indicator = (buy_score if 'MUA' in final_signal else sell_score) / active_count
                # Normalize về 0-15: score trung bình 20-70, map sang 0-15
                # avg < 20 -> 0, avg 20-40 -> 0-7.5, avg 40-60 -> 7.5-12, avg > 60 -> 12-15
                if avg_score_per_indicator < 20:
                    strength_bonus = 0
                elif avg_score_per_indicator < 40:
                    strength_bonus = (avg_score_per_indicator - 20) / 20 * 7.5
                elif avg_score_per_indicator < 60:
                    strength_bonus = 7.5 + (avg_score_per_indicator - 40) / 20 * 4.5
                else:
                    strength_bonus = 12 + min((avg_score_per_indicator - 60) / 40 * 3, 3)
            else:
                strength_bonus = 0
            
            # 4. Bonus nếu có sự đồng thuận giữa các nhóm indicator quan trọng
            harmony_bonus = 0
            if 'MUA' in final_signal or 'BÁN' in final_signal:
                # Check RSI + MACD đồng thuận
                rsi_signal = self.signals.get('rsi', {}).get('signal', 'NEUTRAL')
                macd_signal = self.signals.get('macd', {}).get('signal', 'NEUTRAL')
                ma_signal = self.signals.get('ma', {}).get('signal', 'NEUTRAL')
                
                signal_type = 'MUA' if 'MUA' in final_signal else 'BÁN'
                
                harmony_count = 0
                if signal_type in rsi_signal:
                    harmony_count += 1
                if signal_type in macd_signal:
                    harmony_count += 1
                if signal_type in ma_signal:
                    harmony_count += 1
                
                # 3 chỉ báo quan trọng đồng thuận
                if harmony_count >= 3:
                    harmony_bonus = 15
                elif harmony_count == 2:
                    harmony_bonus = 8
                elif harmony_count == 1:
                    harmony_bonus = 3
            
            # Tính confidence cuối cùng
            confidence = base_confidence + consensus_adjustment + strength_bonus + harmony_bonus - neutral_penalty
            
            # 5. Điều chỉnh nhỏ dựa trên volume và price momentum (±3%)
            if len(self.df) >= 5:
                # Volume factor (-2 to +2)
                volume_data = self.signals.get('volume', {})
                volume_ratio = volume_data.get('volume_ratio', 1.0) if isinstance(volume_data, dict) else 1.0
                if volume_ratio > 1.5:
                    confidence += 2
                elif volume_ratio < 0.8:
                    confidence -= 1.5
                
                # Price momentum factor (-1 to +1) 
                recent_change = (self.df['close'].iloc[-1] - self.df['close'].iloc[-5]) / self.df['close'].iloc[-5] * 100
                if abs(recent_change) > 3:
                    # Mạnh momentum
                    if ('MUA' in final_signal and recent_change > 0) or ('BÁN' in final_signal and recent_change < 0):
                        confidence += 1
                elif abs(recent_change) < 1:
                    # Yếu momentum
                    confidence -= 0.5
            
            # Normalize về 0-100
            confidence = max(0, min(100, confidence))
        
        # Điều chỉnh tín hiệu dựa trên VNINDEX
        vnindex_warning = None
        original_signal = final_signal
        
        if self.vnindex_status and 'allow_buy' in self.vnindex_status:
            vnindex_allow_buy = self.vnindex_status['allow_buy']
            vnindex_status = self.vnindex_status.get('status', 'UNKNOWN')
            vnindex_score = self.vnindex_status.get('percentage', 50)
            
            # === XỬ LÝ TÍN HIỆU MUA ===
            # Nếu VNINDEX yếu và có tín hiệu mua
            if not vnindex_allow_buy and 'MUA' in final_signal:
                final_signal = 'CHỜ - VNINDEX YẾU'
                vnindex_warning = f"⚠️ VNINDEX đang {vnindex_status} ({vnindex_score:.0f}%), KHÔNG khuyến nghị mua mới"
                # Giảm confidence
                confidence = confidence * 0.3
            
            # Nếu VNINDEX trung bình và có tín hiệu mua mạnh
            elif vnindex_status == 'TRUNG BÌNH' and final_signal == 'MUA MẠNH':
                final_signal = 'MUA (THẬN TRỌNG)'
                vnindex_warning = f"⚠️ VNINDEX {vnindex_status} ({vnindex_score:.0f}%), nên thận trọng"
                confidence = confidence * 0.8
            
            # Nếu VNINDEX tốt, tăng confidence cho tín hiệu mua
            elif vnindex_status == 'TỐT' and 'MUA' in final_signal:
                confidence = min(confidence * 1.1, 100)
                vnindex_warning = f"✅ VNINDEX {vnindex_status} ({vnindex_score:.0f}%), phù hợp mua"
            
            # === XỬ LÝ TÍN HIỆU BÁN ===
            # Nếu VNINDEX yếu và có tín hiệu bán → tăng cường tín hiệu bán
            if vnindex_status == 'YẾU' and 'BÁN' in final_signal:
                if final_signal == 'BÁN':
                    final_signal = 'BÁN MẠNH'
                    vnindex_warning = f"🔴 VNINDEX {vnindex_status} ({vnindex_score:.0f}%), NÊN BÁN để bảo vệ vốn"
                    confidence = min(confidence * 1.2, 100)
                else:  # BÁN MẠNH
                    vnindex_warning = f"🔴 VNINDEX {vnindex_status} ({vnindex_score:.0f}%), THOÁT NGAY để bảo vệ vốn"
                    confidence = min(confidence * 1.15, 100)
            
            # Nếu VNINDEX yếu và tín hiệu NEUTRAL → cảnh báo nên bán
            elif vnindex_status == 'YẾU' and final_signal == 'NEUTRAL':
                final_signal = 'CÂN NHẮC BÁN - VNINDEX YẾU'
                vnindex_warning = f"🟠 VNINDEX {vnindex_status} ({vnindex_score:.0f}%), cân nhắc giảm tỷ trọng"
                confidence = 60
            
            # Nếu VNINDEX tốt và có tín hiệu bán → giảm bớt mức độ bán
            elif vnindex_status == 'TỐT' and 'BÁN MẠNH' in final_signal:
                final_signal = 'BÁN (THẬN TRỌNG)'
                vnindex_warning = f"⚠️ VNINDEX {vnindex_status} ({vnindex_score:.0f}%), có thể chờ thêm"
                confidence = confidence * 0.85
            
            # Nếu VNINDEX tốt và có tín hiệu bán → cảnh báo có thể giữ
            elif vnindex_status == 'TỐT' and final_signal == 'BÁN':
                vnindex_warning = f"💡 VNINDEX {vnindex_status} ({vnindex_score:.0f}%), có thể GIỮ thêm nếu chưa lãi nhiều"
                confidence = confidence * 0.9
        
        result = {
            'signal': final_signal,
            'original_signal': original_signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'total_indicators': len(self.signals),
            'neutral_count': neutral_count,
            'details': self.signals,
            'vnindex_status': self.vnindex_status,
            'vnindex_warning': vnindex_warning
        }
        
        # Tính điểm ngành nếu có symbol
        if self.symbol:
            sector_info = self.calculate_sector_score()
            result['sector'] = sector_info
            
            # Điều chỉnh confidence dựa trên điểm ngành
            sector_score = sector_info['score']
            if 'MUA' in final_signal:
                # Nếu ngành mạnh, tăng confidence
                if sector_score >= 70:
                    confidence = min(confidence * 1.08, 100)
                elif sector_score >= 55:
                    confidence = min(confidence * 1.03, 100)
                elif sector_score < 40:
                    # Ngành yếu, giảm confidence
                    confidence = confidence * 0.92
            elif 'BÁN' in final_signal:
                # Nếu ngành yếu, tăng confidence bán
                if sector_score < 40:
                    confidence = min(confidence * 1.05, 100)
                elif sector_score >= 70:
                    # Ngành mạnh nhưng có tín hiệu bán, giảm confidence bán
                    confidence = confidence * 0.95
            
            # Cập nhật confidence sau điều chỉnh ngành
            result['confidence'] = round(confidence, 1)
        
        # Thêm các mức giá khuyến nghị
        price_levels = self.calculate_price_targets()
        result.update(price_levels)
        
        return result
    
    def round_to_tick_size(self, price):
        """
        Làm tròn giá theo bước giá của sàn chứng khoán Việt Nam
        
        Bước giá:
        - Giá < 10: bước 0.01 (10 VNĐ)
        - Giá 10-50: bước 0.05 (50 VNĐ)
        - Giá >= 50: bước 0.1 (100 VNĐ)
        
        Args:
            price: Giá cần làm tròn (đơn vị: nghìn VNĐ)
        
        Returns:
            Giá đã được làm tròn theo bước giá
        """
        if pd.isna(price) or price is None:
            return None
        
        if price < 10:
            # Bước giá 0.01 (10 VNĐ)
            return round(price / 0.01) * 0.01
        elif price < 50:
            # Bước giá 0.05 (50 VNĐ)
            return round(price / 0.05) * 0.05
        else:
            # Bước giá 0.1 (100 VNĐ)
            return round(price / 0.1) * 0.1
    
    def calculate_price_targets(self):
        """
        Tính toán các mức giá khuyến nghị - Kết hợp Support/Resistance và Bollinger Bands
        
        Returns:
            Dictionary chứa các mức giá
        """
        current_price = self.df['close'].iloc[-1]
        
        # Lấy các chỉ báo để tính toán
        result = {
            'current_price': current_price,
            'take_profit_1': None,
            'take_profit_2': None,
            'take_profit_3': None,
            'stop_loss': None
        }
        
        # Lấy mức hỗ trợ và kháng cự
        support = self.df['support'].iloc[-1] if 'support' in self.df.columns else None
        resistance = self.df['resistance'].iloc[-1] if 'resistance' in self.df.columns else None
        
        # Lấy Bollinger Bands
        bb_lower = self.df['bb_lower'].iloc[-1] if 'bb_lower' in self.df.columns else None
        bb_middle = self.df['bb_middle'].iloc[-1] if 'bb_middle' in self.df.columns else None
        bb_upper = self.df['bb_upper'].iloc[-1] if 'bb_upper' in self.df.columns else None
        
        # Tìm các mức hỗ trợ/kháng cự trong 20 ngày gần nhất
        recent_support = None
        recent_resistance = None
        
        if 'support' in self.df.columns and 'resistance' in self.df.columns:
            # Lấy support gần nhất dưới giá hiện tại
            supports_below = self.df[self.df['support'] < current_price]['support'].tail(20)
            if not supports_below.empty:
                recent_support = supports_below.max()  # Support gần nhất
            
            # Lấy resistance gần nhất trên giá hiện tại
            resistances_above = self.df[self.df['resistance'] > current_price]['resistance'].tail(20)
            if not resistances_above.empty:
                recent_resistance = resistances_above.min()  # Resistance gần nhất
        
        # Lấy ATR để tính stop loss
        atr = self.df['atr'].iloc[-1] if 'atr' in self.df.columns else current_price * 0.02
        
        # --- 1. CẮT LỖ (STOP LOSS) ---
        # Đặt DƯỚI mức hỗ trợ hoặc BB Lower (theo phân tích kỹ thuật)
        stop_candidates = []
        
        if recent_support is not None and not pd.isna(recent_support):
            # Cắt lỗ dưới support 2-3% để tránh bị quét
            stop_candidates.append(recent_support * 0.97)
        
        if bb_lower is not None and not pd.isna(bb_lower):
            # Cắt lỗ dưới BB lower 2-3%
            stop_candidates.append(bb_lower * 0.97)
        
        # ATR-based stop (từ giá hiện tại)
        atr_stop = current_price - (1.5 * atr)
        stop_candidates.append(atr_stop)
        
        if stop_candidates:
            # Lấy mức cao nhất (bảo thủ nhất - stop xa hơn)
            result['stop_loss'] = self.round_to_tick_size(max(stop_candidates))
        else:
            result['stop_loss'] = self.round_to_tick_size(current_price * 0.95)
        
        # Đảm bảo stop loss hợp lý: không quá gần giá hiện tại (< 2%)
        min_stop = current_price * 0.98
        if result['stop_loss'] and result['stop_loss'] >= min_stop:
            result['stop_loss'] = self.round_to_tick_size(current_price * 0.95)  # Ít nhất 5% buffer
        
        # --- 3. CHỐT LỜI (TAKE PROFIT) ---
        # Dựa trên kháng cự và BB bands (theo phân tích kỹ thuật)
        
        # TP1: Mục tiêu ngắn hạn - BB Middle hoặc kháng cự gần
        tp1_targets = []
        
        if bb_middle is not None and not pd.isna(bb_middle) and bb_middle > current_price:
            # Chốt lời T1 tại BB middle (mức trung bình)
            tp1_targets.append(bb_middle * 0.99)  # 1% dưới để đảm bảo khớp
        
        if recent_resistance is not None and not pd.isna(recent_resistance):
            # Hoặc 50% khoảng cách đến resistance
            distance_to_resistance = recent_resistance - current_price
            if distance_to_resistance > 0:
                tp1_targets.append(current_price + (distance_to_resistance * 0.5))
        
        if tp1_targets:
            result['take_profit_1'] = self.round_to_tick_size(min(tp1_targets))  # Mục tiêu gần nhất
        else:
            result['take_profit_1'] = self.round_to_tick_size(current_price * 1.03)
        
        # TP2: Mục tiêu trung hạn - Resistance hoặc BB Upper
        tp2_targets = []
        
        if recent_resistance is not None and not pd.isna(recent_resistance):
            # Chốt lời T2 tại mức kháng cự (resistance)
            tp2_targets.append(recent_resistance * 0.99)  # 1% dưới để đảm bảo khớp
        
        if bb_upper is not None and not pd.isna(bb_upper) and bb_upper > current_price:
            # Hoặc tại BB upper
            tp2_targets.append(bb_upper * 0.98)  # 2% dưới BB upper
        
        if tp2_targets:
            result['take_profit_2'] = self.round_to_tick_size(max(tp2_targets))  # Lấy mục tiêu cao hơn
        else:
            result['take_profit_2'] = self.round_to_tick_size(current_price * 1.08)
        
        # TP3: Mục tiêu dài hạn - Resistance tiếp theo hoặc trên BB Upper
        tp3_targets = []
        
        if recent_resistance is not None and not pd.isna(recent_resistance):
            # Tìm resistance tiếp theo
            resistances_higher = self.df[self.df['resistance'] > recent_resistance]['resistance'].tail(20)
            if not resistances_higher.empty:
                next_resistance = resistances_higher.min()
                tp3_targets.append(next_resistance * 0.99)
            else:
                # Không có resistance cao hơn, đặt target 10% trên resistance hiện tại
                tp3_targets.append(recent_resistance * 1.10)
        
        if bb_upper is not None and not pd.isna(bb_upper):
            # Hoặc 5% trên BB upper (vượt biên)
            tp3_targets.append(bb_upper * 1.05)
        
        if tp3_targets:
            result['take_profit_3'] = self.round_to_tick_size(max(tp3_targets))
        else:
            result['take_profit_3'] = self.round_to_tick_size(current_price * 1.15)
        
        # Đảm bảo thứ tự logic: Stop Loss < Giá hiện tại < TP1 < TP2 < TP3
        if result['take_profit_1'] and result['take_profit_1'] <= current_price * 1.02:
            result['take_profit_1'] = self.round_to_tick_size(current_price * 1.03)
        
        if result['take_profit_2'] and result['take_profit_2'] <= result['take_profit_1']:
            result['take_profit_2'] = self.round_to_tick_size(result['take_profit_1'] * 1.05)
        
        if result['take_profit_3'] and result['take_profit_3'] <= result['take_profit_2']:
            result['take_profit_3'] = self.round_to_tick_size(result['take_profit_2'] * 1.05)
        
        # Tính tỷ lệ Risk/Reward (dựa trên giá hiện tại)
        if result['stop_loss'] and result['take_profit_2']:
            risk = current_price - result['stop_loss']
            reward = result['take_profit_2'] - current_price
            result['risk_reward_ratio'] = round(reward / risk, 2) if risk > 0 else 0
        else:
            result['risk_reward_ratio'] = 0
        
        return result
