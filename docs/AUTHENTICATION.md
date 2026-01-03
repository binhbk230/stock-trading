# 🔐 Authentication System - Portfolio Security

## Hệ thống xác thực bảo mật cho Portfolio

### ✅ Đã implement

#### 1. **File cấu hình users** 
**File:** [users_config.json](users_config.json)

```json
{
  "users": {
    "user1": {
      "username": "user1",
      "password": "123456",
      "full_name": "Người dùng 1",
      "portfolio_file": "portfolios/user1.json"
    },
    "user2": {
      "username": "user2",
      "password": "123456",
      "full_name": "Người dùng 2",
      "portfolio_file": "portfolios/user2.json"
    }
  }
}
```

#### 2. **Functions xác thực**
**File:** [portfolio_manager.py](portfolio_manager.py)

```python
# Load config
load_users_config() -> Dict

# Xác thực login
verify_login(username, password) -> bool

# Lấy thông tin user
get_user_info(username) -> Optional[Dict]
```

#### 3. **Login flow trong Streamlit**
**File:** [app.py](app.py)

- ✅ Form đăng nhập với username + password
- ✅ Session state để lưu trạng thái đăng nhập
- ✅ Nút đăng xuất
- ✅ Bảo vệ content - chỉ hiển thị khi đã login

---

## 🚀 Cách sử dụng

### 1. Truy cập Portfolio
- Chọn mode "💼 Danh mục của tôi"
- Sẽ thấy màn hình đăng nhập

### 2. Đăng nhập
**Tài khoản mặc định:**
- **User 1:** 
  - Username: `user1`
  - Password: `123456`
  
- **User 2:**
  - Username: `user2`
  - Password: `123456`

### 3. Sau khi đăng nhập
- Hiển thị tên user ở header
- Có nút "🚪 Đăng xuất"
- Truy cập đầy đủ 4 tabs portfolio

### 4. Đăng xuất
- Click nút "🚪 Đăng xuất"
- Session bị xóa
- Quay về màn hình login

---

## 🔒 Tính năng bảo mật

### ✅ Đã có:
1. **Authentication**: Phải nhập đúng username + password
2. **Session Management**: Dùng `st.session_state` để track login
3. **Content Protection**: Chỉ user đã login mới thấy portfolio
4. **User Isolation**: Mỗi user chỉ thấy portfolio của mình
5. **Logout Function**: Có thể đăng xuất bất kỳ lúc nào

### ⚠️ Hạn chế hiện tại:
1. **Plain text password**: Password lưu dạng text thường trong JSON
2. **No encryption**: Dữ liệu không được mã hóa
3. **No session timeout**: Session không tự động hết hạn
4. **Local storage**: Config lưu trên máy local, không có database
5. **No password reset**: Chỉ có thể sửa file config thủ công

---

## 🔧 Cách đổi mật khẩu

### Cách 1: Sửa file config
1. Mở [users_config.json](users_config.json)
2. Đổi giá trị `password`:
```json
{
  "users": {
    "user1": {
      "username": "user1",
      "password": "matkhaumoi123",  // ← Đổi đây
      ...
    }
  }
}
```
3. Save file
4. Login lại với password mới

### Cách 2: Thêm user mới
Thêm vào `users_config.json`:
```json
{
  "users": {
    "user1": {...},
    "user2": {...},
    "user3": {
      "username": "user3",
      "password": "123456",
      "full_name": "Người dùng 3",
      "portfolio_file": "portfolios/user3.json"
    }
  }
}
```

---

## 🎯 Security Flow

```
1. User chọn mode "💼 Danh mục của tôi"
   ↓
2. Kiểm tra st.session_state.logged_in_user
   ↓
3. Nếu None → Hiển thị form login
   ↓
4. User nhập username + password
   ↓
5. Click "Đăng nhập"
   ↓
6. verify_login(username, password)
   ↓
7. Nếu đúng:
   - Lưu username vào session_state
   - Redirect về portfolio
   ↓
8. Nếu sai:
   - Hiển thị error
   - Giữ ở màn hình login
```

---

## 💡 Best Practices

### Cho người dùng:
1. **Đổi password mặc định** ngay sau lần đăng nhập đầu tiên
2. **Không chia sẻ password** với người khác
3. **Đăng xuất** khi dùng xong (đặc biệt trên máy chung)
4. **Backup** file `users_config.json` và `portfolios/*.json` thường xuyên

### Cho developer:
1. **Không commit** `users_config.json` vào git public
2. Thêm vào `.gitignore`:
   ```
   users_config.json
   portfolios/*.json
   ```
3. Tạo file `users_config.example.json` làm template
4. Cân nhắc upgrade lên hash password (bcrypt) trong tương lai

---

## 🔮 Future Enhancements

Các cải tiến có thể thêm:

- [ ] **Password hashing**: Dùng bcrypt thay vì plain text
- [ ] **Session timeout**: Auto logout sau X phút không hoạt động
- [ ] **Remember me**: Checkbox lưu đăng nhập
- [ ] **Password strength**: Yêu cầu password mạnh
- [ ] **2FA**: Two-factor authentication
- [ ] **Activity log**: Ghi lại lịch sử đăng nhập
- [ ] **Password recovery**: Chức năng quên mật khẩu
- [ ] **Email verification**: Xác thực email khi đăng ký
- [ ] **Role-based access**: Admin vs User permissions
- [ ] **Database backend**: SQLite/PostgreSQL thay vì JSON

---

## 🐛 Troubleshooting

### Vấn đề: Không đăng nhập được
**Giải pháp:**
1. Kiểm tra username có đúng không (phân biệt hoa/thường)
2. Kiểm tra password trong `users_config.json`
3. Mật khẩu mặc định: `123456`

### Vấn đề: Bị logout khi reload page
**Nguyên nhân:** Streamlit session_state bị reset khi reload
**Giải pháp:** Đăng nhập lại (hoặc implement remember me)

### Vấn đề: Muốn reset tất cả
**Giải pháp:**
1. Xóa hoặc sửa file `users_config.json`
2. Trong browser: Clear cache Streamlit
3. Restart app: `Ctrl+C` và chạy lại `streamlit run app.py`

---

## 📝 Example Code

### Kiểm tra đăng nhập programmatically:
```python
from portfolio_manager import verify_login, get_user_info

# Xác thực
if verify_login("user1", "123456"):
    print("✅ Login success")
    user_info = get_user_info("user1")
    print(f"Welcome, {user_info['full_name']}")
else:
    print("❌ Login failed")
```

### Thêm user mới programmatically:
```python
import json

# Load config
with open('users_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Thêm user
config['users']['user3'] = {
    "username": "user3",
    "password": "newpass123",
    "full_name": "Người dùng 3",
    "portfolio_file": "portfolios/user3.json"
}

# Save
with open('users_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
```

---

Made with 🔐 for secure portfolio management
