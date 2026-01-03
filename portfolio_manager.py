"""
Portfolio Manager - Quản lý danh mục đầu tư cá nhân
Lưu trữ và tính toán lãi/lỗ cho các cổ phiếu đang nắm giữ
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from main import StockAnalyzer


def load_users_config() -> Dict:
    """Load cấu hình users từ file config"""
    config_file = "users_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}}


def verify_login(username: str, password: str) -> bool:
    """
    Xác thực đăng nhập
    
    Args:
        username: Tên đăng nhập
        password: Mật khẩu
    
    Returns:
        True nếu đăng nhập thành công
    """
    config = load_users_config()
    users = config.get("users", {})
    
    if username not in users:
        return False
    
    user_data = users[username]
    return user_data.get("password") == password


def get_user_info(username: str) -> Optional[Dict]:
    """
    Lấy thông tin user
    
    Args:
        username: Tên đăng nhập
    
    Returns:
        Dictionary chứa thông tin user hoặc None
    """
    config = load_users_config()
    users = config.get("users", {})
    return users.get(username)


class PortfolioManager:
    """Quản lý danh mục đầu tư cá nhân"""
    
    def __init__(self, username: str):
        """
        Khởi tạo Portfolio Manager
        
        Args:
            username: Tên người dùng (user1, user2, ...)
        """
        self.username = username
        self.portfolio_dir = "portfolios"
        self.portfolio_file = os.path.join(self.portfolio_dir, f"{username}.json")
        
        # Tạo thư mục nếu chưa có
        if not os.path.exists(self.portfolio_dir):
            os.makedirs(self.portfolio_dir)
        
        # Load portfolio
        self.data = self._load_portfolio()
    
    def _load_portfolio(self) -> Dict:
        """Load portfolio từ file JSON"""
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Migration: Chuyển từ holdings sang transactions nếu cần
                if "holdings" in data and "transactions" not in data:
                    transactions = []
                    for holding in data["holdings"]:
                        transactions.append({
                            "type": "buy",
                            "symbol": holding["symbol"],
                            "quantity": holding["quantity"],
                            "price": holding["buy_price"],
                            "date": holding["buy_date"],
                            "notes": holding.get("notes", ""),
                            "timestamp": holding.get("added_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        })
                    data["transactions"] = transactions
                    data["realized_pnl"] = 0.0
                    del data["holdings"]  # Xóa holdings cũ
                return data
        else:
            # Tạo portfolio mới với cấu trúc transactions
            return {
                "username": self.username,
                "transactions": [],
                "realized_pnl": 0.0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _save_portfolio(self):
        """Lưu portfolio vào file JSON"""
        self.data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_stock(self, symbol: str, quantity: int, buy_price: float, 
                  buy_date: str, notes: str = "") -> bool:
        """
        Thêm giao dịch MUA cổ phiếu vào danh mục
        
        Args:
            symbol: Mã cổ phiếu
            quantity: Số lượng
            buy_price: Giá mua
            buy_date: Ngày mua (YYYY-MM-DD)
            notes: Ghi chú (optional)
        
        Returns:
            True nếu thêm thành công
        """
        transaction = {
            "type": "buy",
            "symbol": symbol.upper(),
            "quantity": quantity,
            "price": buy_price,
            "date": buy_date,
            "notes": notes,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.data["transactions"].append(transaction)
        self._save_portfolio()
        return True
    
    def sell_stock(self, symbol: str, quantity: int, sell_price: float,
                   sell_date: str, notes: str = "") -> Dict:
        """
        Bán cổ phiếu và ghi nhận lãi/lỗ
        
        Args:
            symbol: Mã cổ phiếu
            quantity: Số lượng bán
            sell_price: Giá bán
            sell_date: Ngày bán (YYYY-MM-DD)
            notes: Ghi chú (optional)
        
        Returns:
            Dict với kết quả: {"success": bool, "message": str, "realized_pnl": float}
        """
        symbol = symbol.upper()
        
        # Kiểm tra số lượng đang nắm giữ
        current_holdings = self._get_current_holdings()
        
        if symbol not in current_holdings:
            return {"success": False, "message": f"Bạn không có {symbol} trong danh mục!", "realized_pnl": 0}
        
        available_qty = current_holdings[symbol]["quantity"]
        
        if quantity > available_qty:
            return {
                "success": False,
                "message": f"Không đủ số lượng! Bạn chỉ có {available_qty} cổ {symbol}",
                "realized_pnl": 0
            }
        
        # Tính P&L realized (dựa theo giá mua trung bình)
        avg_buy_price = current_holdings[symbol]["avg_price"]
        realized_pnl = (sell_price - avg_buy_price) * quantity
        
        # Ghi nhận giao dịch bán
        transaction = {
            "type": "sell",
            "symbol": symbol,
            "quantity": quantity,
            "price": sell_price,
            "date": sell_date,
            "notes": notes,
            "avg_buy_price": avg_buy_price,
            "realized_pnl": realized_pnl,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.data["transactions"].append(transaction)
        self.data["realized_pnl"] = self.data.get("realized_pnl", 0) + realized_pnl
        self._save_portfolio()
        
        return {
            "success": True,
            "message": f"Đã bán {quantity} cổ {symbol} với giá {sell_price:,.0f}",
            "realized_pnl": realized_pnl,
            "avg_buy_price": avg_buy_price
        }
    
    def _get_current_holdings(self) -> Dict[str, Dict]:
        """
        Tính holdings hiện tại từ transactions
        
        Returns:
            Dict {symbol: {"quantity": int, "total_cost": float, "avg_price": float}}
        """
        holdings = {}
        
        for txn in self.data["transactions"]:
            symbol = txn["symbol"]
            quantity = txn["quantity"]
            price = txn["price"]
            
            if symbol not in holdings:
                holdings[symbol] = {
                    "quantity": 0,
                    "total_cost": 0.0,
                    "avg_price": 0.0
                }
            
            if txn["type"] == "buy":
                holdings[symbol]["total_cost"] += quantity * price
                holdings[symbol]["quantity"] += quantity
            elif txn["type"] == "sell":
                # Giảm số lượng khi bán
                holdings[symbol]["quantity"] -= quantity
                # Giảm cost theo tỷ lệ
                if holdings[symbol]["quantity"] > 0:
                    holdings[symbol]["total_cost"] = holdings[symbol]["quantity"] * holdings[symbol]["avg_price"]
                else:
                    holdings[symbol]["total_cost"] = 0
            
            # Tính giá trung bình
            if holdings[symbol]["quantity"] > 0:
                holdings[symbol]["avg_price"] = holdings[symbol]["total_cost"] / holdings[symbol]["quantity"]
        
        # Lọc bỏ các mã đã bán hết
        holdings = {k: v for k, v in holdings.items() if v["quantity"] > 0}
        
        return holdings
    
    def remove_stock(self, index: int) -> bool:
        """
        Xóa cổ phiếu khỏi danh mục theo index
        
        Args:
            index: Vị trí trong danh sách holdings
        
        Returns:
            True nếu xóa thành công
        """
        if 0 <= index < len(self.data["holdings"]):
            self.data["holdings"].pop(index)
            self._save_portfolio()
            return True
        return False
    
    def update_stock(self, index: int, quantity: Optional[int] = None, 
                     buy_price: Optional[float] = None, 
                     notes: Optional[str] = None) -> bool:
        """
        Cập nhật thông tin cổ phiếu
        
        Args:
            index: Vị trí trong danh sách holdings
            quantity: Số lượng mới (optional)
            buy_price: Giá mua mới (optional)
            notes: Ghi chú mới (optional)
        
        Returns:
            True nếu cập nhật thành công
        """
        if 0 <= index < len(self.data["holdings"]):
            holding = self.data["holdings"][index]
            
            if quantity is not None:
                holding["quantity"] = quantity
            if buy_price is not None:
                holding["buy_price"] = buy_price
            if notes is not None:
                holding["notes"] = notes
            
            self._save_portfolio()
            return True
        return False
    
    def get_holdings(self) -> List[Dict]:
        """
        Lấy danh sách cổ phiếu đang nắm giữ (từ transactions)
        
        Returns:
            List of dicts với symbol, quantity, avg_price
        """
        holdings_dict = self._get_current_holdings()
        
        # Chuyển từ dict sang list
        holdings_list = []
        for symbol, data in holdings_dict.items():
            holdings_list.append({
                "symbol": symbol,
                "quantity": data["quantity"],
                "buy_price": data["avg_price"],  # Giá mua trung bình
                "buy_date": "Nhiều lần",  # Vì có thể mua nhiều lần
                "notes": ""
            })
        
        return holdings_list
    
    def get_transactions(self) -> List[Dict]:
        """Lấy lịch sử giao dịch"""
        return self.data.get("transactions", [])
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        Lấy giá hiện tại của tất cả cổ phiếu trong danh mục
        
        Returns:
            Dictionary {symbol: current_price} (đơn vị: VND)
        """
        # Lấy danh sách holdings hiện tại từ transactions
        holdings = self.get_holdings()
        symbols = list(set([h["symbol"] for h in holdings]))
        prices = {}
        
        for symbol in symbols:
            try:
                analyzer = StockAnalyzer(symbol)
                analyzer.fetch_data()  # Phải gọi fetch_data() để lấy dữ liệu
                
                if analyzer.data is not None and not analyzer.data.empty:
                    # Giá từ API là nghìn đồng, nhân 1000 để ra VND
                    current_price = analyzer.data['close'].iloc[-1] * 1000
                    prices[symbol] = current_price
                else:
                    prices[symbol] = 0
                    
            except Exception as e:
                print(f"Lỗi lấy giá {symbol}: {e}")
                prices[symbol] = 0
        
        return prices
    
    def calculate_pnl(self, group_by_symbol: bool = True) -> pd.DataFrame:
        """
        Tính toán lãi/lỗ cho cổ phiếu đang nắm giữ (unrealized P&L)
        
        Args:
            group_by_symbol: Luôn True (đã gộp tự động từ transactions)
        
        Returns:
            DataFrame với thông tin P&L chi tiết
        """
        holdings_dict = self._get_current_holdings()
        
        if not holdings_dict:
            return pd.DataFrame()
        
        # Lấy giá hiện tại
        current_prices = self.get_current_prices()
        
        results = []
        
        for symbol, holding_data in holdings_dict.items():
            quantity = holding_data["quantity"]
            avg_buy_price = holding_data["avg_price"]
            investment = holding_data["total_cost"]
            current_price = current_prices.get(symbol, 0)
            
            # Tính toán unrealized P&L
            current_value = quantity * current_price
            unrealized_pnl = current_value - investment
            unrealized_pnl_pct = (unrealized_pnl / investment * 100) if investment > 0 else 0
            
            results.append({
                "symbol": symbol,
                "quantity": quantity,
                "buy_price": avg_buy_price,
                "current_price": current_price,
                "investment": investment,
                "current_value": current_value,
                "pnl": unrealized_pnl,
                "pnl_pct": unrealized_pnl_pct,
                "buy_date": "Nhiều lần",
                "notes": ""
            })
        
        df = pd.DataFrame(results)
        # Sắp xếp theo giá trị danh mục giảm dần
        if not df.empty:
            df = df.sort_values('current_value', ascending=False)
        return df
    
    def get_portfolio_summary(self) -> Dict:
        """
        Tạo báo cáo tổng hợp danh mục
        
        Returns:
            Dictionary chứa thống kê tổng hợp
        """
        df = self.calculate_pnl()
        
        if df.empty:
            return {
                "total_stocks": 0,
                "total_investment": 0,
                "total_current_value": 0,
                "total_pnl": 0,
                "total_pnl_pct": 0,
                "best_performer": None,
                "worst_performer": None
            }
        
        summary = {
            "total_stocks": len(df),
            "total_investment": df["investment"].sum(),
            "total_current_value": df["current_value"].sum(),
            "total_pnl": df["pnl"].sum(),
            "total_pnl_pct": (df["pnl"].sum() / df["investment"].sum() * 100) if df["investment"].sum() > 0 else 0,
            "best_performer": df.loc[df["pnl_pct"].idxmax()].to_dict() if not df.empty else None,
            "worst_performer": df.loc[df["pnl_pct"].idxmin()].to_dict() if not df.empty else None
        }
        
        return summary
    
    def get_portfolio_distribution(self) -> pd.DataFrame:
        """
        Tính phân bổ danh mục theo giá trị
        
        Returns:
            DataFrame với phân bổ theo %
        """
        df = self.calculate_pnl()
        
        if df.empty:
            return pd.DataFrame()
        
        # Nhóm theo symbol (nếu có nhiều lần mua cùng mã)
        dist = df.groupby("symbol").agg({
            "current_value": "sum",
            "pnl": "sum"
        }).reset_index()
        
        total_value = dist["current_value"].sum()
        dist["allocation_pct"] = (dist["current_value"] / total_value * 100) if total_value > 0 else 0
        
        return dist.sort_values("allocation_pct", ascending=False)
    
    def check_sell_signals(self) -> pd.DataFrame:
        """
        Kiểm tra tín hiệu bán cho các cổ phiếu trong danh mục
        
        Returns:
            DataFrame với thông tin tín hiệu bán
        """
        # Lấy holdings hiện tại từ transactions
        holdings = self.get_holdings()
        
        if not holdings:
            return pd.DataFrame()
        
        from signal_generator import SignalGenerator
        
        results = []
        
        for idx, holding in enumerate(holdings):
            symbol = holding["symbol"]
            
            try:
                # Lấy dữ liệu
                analyzer = StockAnalyzer(symbol)
                
                if analyzer.data.empty:
                    continue
                
                # Sinh tín hiệu
                signal_gen = SignalGenerator(analyzer.data, symbol=symbol)
                signal_gen.generate_signals()
                
                signal_info = signal_gen.get_signal_info()
                
                # Chỉ lấy tín hiệu BÁN
                if 'BÁN' in signal_info['signal']:
                    results.append({
                        "index": idx,
                        "symbol": symbol,
                        "signal": signal_info['signal'],
                        "confidence": signal_info['confidence'],
                        "sell_score": signal_info.get('sell_score', 0),
                        "quantity": holding["quantity"],
                        "buy_price": holding["buy_price"],
                        "current_price": analyzer.data['close'].iloc[-1],
                        "recommendation": signal_info.get('recommendation', '')
                    })
                    
            except Exception as e:
                print(f"Lỗi kiểm tra tín hiệu {symbol}: {e}")
                continue
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        return df.sort_values(['confidence', 'sell_score'], ascending=[False, False])


def test_portfolio_manager():
    """Test function"""
    pm = PortfolioManager("test_user")
    
    # Thêm cổ phiếu
    pm.add_stock("VCB", 100, 85.5, "2025-01-15", "Ngân hàng vốn hóa lớn")
    pm.add_stock("VHM", 50, 45.2, "2025-02-10", "Bất động sản")
    pm.add_stock("HPG", 200, 25.0, "2025-03-05")
    
    # Xem danh sách
    print("Holdings:", pm.get_holdings())
    
    # Tính P&L
    pnl_df = pm.calculate_pnl()
    print("\nP&L DataFrame:")
    print(pnl_df)
    
    # Tổng hợp
    summary = pm.get_portfolio_summary()
    print("\nPortfolio Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_portfolio_manager()
