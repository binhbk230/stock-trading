"""
Global rate limiter để đảm bảo tất cả API calls đều tuân thủ rate limit
Dùng singleton pattern để chia sẻ state giữa các analyzer instances
"""
import time
import threading


class GlobalRateLimiter:
    """
    Singleton rate limiter chia sẻ giữa tất cả API calls
    Đảm bảo không vượt quá rate limit dù có bao nhiêu analyzer instances
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.last_request_time = None
        self.request_count = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self, delay_seconds=3.5):
        """
        Chờ nếu cần để tuân thủ rate limit
        
        Args:
            delay_seconds: Số giây delay tối thiểu giữa các requests
        """
        with self.lock:
            if self.last_request_time is not None:
                elapsed = time.time() - self.last_request_time
                if elapsed < delay_seconds:
                    sleep_time = delay_seconds - elapsed
                    time.sleep(sleep_time)
            self.last_request_time = time.time()
            self.request_count += 1
    
    def reset(self):
        """Reset counter (dùng cho testing)"""
        with self.lock:
            self.last_request_time = None
            self.request_count = 0


# Global instance
_global_rate_limiter = GlobalRateLimiter()


def get_rate_limiter():
    """Lấy global rate limiter instance"""
    return _global_rate_limiter
