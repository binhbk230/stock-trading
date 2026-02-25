"""
Cấu hình vnstock API key và các tham số
"""
import os
from dotenv import load_dotenv
from vnstock import Vnstock

# Load environment variables từ .env file
load_dotenv()


class VnstockConfig:
    """Singleton config cho vnstock"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Đọc config từ environment variables
        self.api_key = os.getenv('VNSTOCK_API_KEY', '').strip()
        self.source = os.getenv('VNSTOCK_SOURCE', 'VCI').upper()
        self.delay = float(os.getenv('VNSTOCK_DELAY', '3.5'))
        
        # Tự động điều chỉnh delay dựa vào có API key hay không
        if self.api_key:
            # Có API key (Community/Sponsor) → delay ngắn hơn
            if self.delay > 2.0:
                self.delay = 1.0  # 60 req/min
                print(f"✅ Sử dụng vnstock Community API - Delay: {self.delay}s (~60 req/min)")
        else:
            # Không có API key (Guest) → delay dài hơn
            if self.delay < 3.0:
                self.delay = 3.5  # 17 req/min
            print(f"⚠️ Sử dụng vnstock Guest API - Delay: {self.delay}s (~17 req/min)")
            print(f"💡 Nâng cấp miễn phí tại: https://vnstocks.com/login để tăng tốc lên 60 req/min")
    
    def create_vnstock(self, symbol, source=None):
        """
        Tạo Vnstock instance với config
        
        Args:
            symbol: Mã cổ phiếu
            source: Source (VCI, TCBS, SSI), mặc định từ config
        
        Returns:
            Vnstock instance
        """
        src = source if source else self.source
        
        # Vnstock v3+ sử dụng API key qua environment variable
        # hoặc có thể pass qua parameter (tùy phiên bản)
        if self.api_key:
            # Set environment variable để vnstock sử dụng
            os.environ['VNSTOCK_API_KEY'] = self.api_key
        
        return Vnstock().stock(symbol=symbol, source=src)
    
    def get_delay(self):
        """Lấy delay giữa các requests"""
        return self.delay
    
    def has_api_key(self):
        """Kiểm tra có API key hay không"""
        return bool(self.api_key)
    
    def get_rate_limit(self):
        """Lấy rate limit dự kiến (req/min)"""
        if self.has_api_key():
            return 60  # Community minimum
        return 20  # Guest


# Global instance
_config = VnstockConfig()


def get_vnstock_config():
    """Lấy vnstock config instance"""
    return _config


def create_vnstock(symbol, source=None):
    """
    Tạo Vnstock instance với config global
    
    Args:
        symbol: Mã cổ phiếu
        source: Source (VCI, TCBS, SSI)
    
    Returns:
        Vnstock instance
    """
    return _config.create_vnstock(symbol, source)


def get_default_delay():
    """Lấy default delay dựa vào config"""
    return _config.get_delay()
