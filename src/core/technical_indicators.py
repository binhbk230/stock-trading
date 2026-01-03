"""
Module tính toán các chỉ báo kỹ thuật cho phân tích cổ phiếu
"""
import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice


class TechnicalIndicators:
    """Lớp tính toán các chỉ báo kỹ thuật"""
    
    def __init__(self, df):
        """
        Khởi tạo với DataFrame chứa dữ liệu giá
        
        Args:
            df: DataFrame với các cột: open, high, low, close, volume
        """
        self.df = df.copy()
        self._validate_dataframe()
    
    def _validate_dataframe(self):
        """Kiểm tra DataFrame có đủ các cột cần thiết"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(f"DataFrame thiếu các cột: {missing_columns}")
    
    def calculate_rsi(self, window=14):
        """
        Tính chỉ số RSI (Relative Strength Index)
        
        Args:
            window: Chu kỳ tính toán (mặc định 14)
        
        Returns:
            Series chứa giá trị RSI
        """
        rsi = RSIIndicator(close=self.df['close'], window=window)
        self.df['rsi'] = rsi.rsi()
        return self.df['rsi']
    
    def calculate_macd(self, window_slow=26, window_fast=12, window_sign=9):
        """
        Tính chỉ số MACD (Moving Average Convergence Divergence)
        
        Args:
            window_slow: Chu kỳ EMA chậm (mặc định 26)
            window_fast: Chu kỳ EMA nhanh (mặc định 12)
            window_sign: Chu kỳ Signal line (mặc định 9)
        
        Returns:
            Tuple (MACD, Signal, Histogram)
        """
        macd = MACD(
            close=self.df['close'],
            window_slow=window_slow,
            window_fast=window_fast,
            window_sign=window_sign
        )
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        self.df['macd_diff'] = macd.macd_diff()
        
        return self.df['macd'], self.df['macd_signal'], self.df['macd_diff']
    
    def calculate_moving_averages(self, windows=[20, 50, 200]):
        """
        Tính các đường trung bình động (SMA)
        
        Args:
            windows: Danh sách các chu kỳ tính toán
        
        Returns:
            Dictionary chứa các SMA
        """
        smas = {}
        for window in windows:
            sma = SMAIndicator(close=self.df['close'], window=window)
            col_name = f'sma_{window}'
            self.df[col_name] = sma.sma_indicator()
            smas[col_name] = self.df[col_name]
        
        return smas
    
    def calculate_ema(self, windows=[12, 26]):
        """
        Tính các đường trung bình động mũ (EMA)
        
        Args:
            windows: Danh sách các chu kỳ tính toán
        
        Returns:
            Dictionary chứa các EMA
        """
        emas = {}
        for window in windows:
            ema = EMAIndicator(close=self.df['close'], window=window)
            col_name = f'ema_{window}'
            self.df[col_name] = ema.ema_indicator()
            emas[col_name] = self.df[col_name]
        
        return emas
    
    def calculate_bollinger_bands(self, window=20, window_dev=2):
        """
        Tính các dải Bollinger
        
        Args:
            window: Chu kỳ tính toán (mặc định 20)
            window_dev: Số độ lệch chuẩn (mặc định 2)
        
        Returns:
            Tuple (Upper Band, Middle Band, Lower Band)
        """
        bb = BollingerBands(
            close=self.df['close'],
            window=window,
            window_dev=window_dev
        )
        self.df['bb_upper'] = bb.bollinger_hband()
        self.df['bb_middle'] = bb.bollinger_mavg()
        self.df['bb_lower'] = bb.bollinger_lband()
        self.df['bb_width'] = bb.bollinger_wband()
        
        return (
            self.df['bb_upper'],
            self.df['bb_middle'],
            self.df['bb_lower']
        )
    
    def calculate_stochastic(self, window=14, smooth_window=3):
        """
        Tính chỉ số Stochastic Oscillator
        
        Args:
            window: Chu kỳ tính toán (mặc định 14)
            smooth_window: Chu kỳ làm mượt (mặc định 3)
        
        Returns:
            Tuple (%K, %D)
        """
        stoch = StochasticOscillator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            window=window,
            smooth_window=smooth_window
        )
        self.df['stoch_k'] = stoch.stoch()
        self.df['stoch_d'] = stoch.stoch_signal()
        
        return self.df['stoch_k'], self.df['stoch_d']
    
    def calculate_obv(self):
        """
        Tính chỉ số On-Balance Volume (OBV)
        
        Returns:
            Series chứa giá trị OBV
        """
        obv = OnBalanceVolumeIndicator(
            close=self.df['close'],
            volume=self.df['volume']
        )
        self.df['obv'] = obv.on_balance_volume()
        return self.df['obv']
    
    def calculate_vwap(self):
        """
        Tính Volume Weighted Average Price (VWAP)
        
        Returns:
            Series chứa giá trị VWAP
        """
        try:
            vwap = VolumeWeightedAveragePrice(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                volume=self.df['volume']
            )
            self.df['vwap'] = vwap.volume_weighted_average_price()
        except:
            # Tính VWAP thủ công nếu thư viện không hỗ trợ
            self.df['vwap'] = (self.df['close'] * self.df['volume']).cumsum() / self.df['volume'].cumsum()
        
        return self.df['vwap']
    
    def calculate_atr(self, window=14):
        """
        Tính Average True Range (ATR) - đo độ biến động
        
        Args:
            window: Chu kỳ tính toán (mặc định 14)
        
        Returns:
            Series chứa giá trị ATR
        """
        atr = AverageTrueRange(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            window=window
        )
        self.df['atr'] = atr.average_true_range()
        return self.df['atr']
    
    def calculate_support_resistance(self, window=20):
        """
        Tính các mức hỗ trợ và kháng cự
        
        Args:
            window: Chu kỳ để xác định mức (mặc định 20)
        
        Returns:
            Tuple (support, resistance)
        """
        self.df['support'] = self.df['low'].rolling(window=window).min()
        self.df['resistance'] = self.df['high'].rolling(window=window).max()
        
        return self.df['support'], self.df['resistance']
    
    def calculate_all(self):
        """
        Tính tất cả các chỉ báo kỹ thuật
        
        Returns:
            DataFrame với tất cả các chỉ báo
        """
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_moving_averages()
        self.calculate_ema()
        self.calculate_bollinger_bands()
        self.calculate_stochastic()
        self.calculate_obv()
        self.calculate_vwap()
        self.calculate_atr()
        self.calculate_support_resistance()
        
        return self.df
    
    def get_latest_values(self):
        """
        Lấy các giá trị chỉ báo mới nhất
        
        Returns:
            Dictionary chứa các giá trị mới nhất
        """
        latest = {}
        for col in self.df.columns:
            if col not in ['open', 'high', 'low', 'close', 'volume']:
                latest[col] = self.df[col].iloc[-1]
        
        latest['close'] = self.df['close'].iloc[-1]
        latest['volume'] = self.df['volume'].iloc[-1]
        
        return latest
