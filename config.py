import os

# Tính năng đăng nhập: True nếu muốn bật, False nếu muốn tắt
LOGIN_SYSTEM = bool(os.environ.get('LOGIN_SYSTEM', True)) # True hoặc False

if LOGIN_SYSTEM == False:
    # Nếu hệ thống đăng nhập là False, hãy điền String Session của tài khoản Telegram vào đây
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
else:
    STRING_SESSION = None

# Bot token lấy từ @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# API ID của bạn lấy từ trang my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))

# API Hash của bạn lấy từ trang my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# ID của Chủ sở hữu / Admin để sử dụng tính năng Gửi tin nhắn hàng loạt (Broadcast)
ADMINS = int(os.environ.get("ADMINS", "6379209139"))

# ID Kênh nơi Bot sẽ tải lên Video/File/Tin nhắn đã tải xuống...
# Lưu ý: Hãy thêm Bot làm Admin trong kênh này với đầy đủ quyền hạn.
# Nếu bạn không muốn tải lên kênh, hãy để trống (không điền gì cả).
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

# Đường dẫn cơ sở dữ liệu Mongodb của bạn
# Cảnh báo: Nên điền DB URI vào biến môi trường (Environment Variable) trên server, không nên để trực tiếp trong repo code.
DB_URI = os.environ.get("DB_URI", "") 
DB_NAME = os.environ.get("DB_NAME", "HgAnh7")

# Tăng thời gian chờ càng cao càng tốt để tránh lỗi Floodwait, Spam và bị Telegram khóa tài khoản.
WAITING_TIME = int(os.environ.get("WAITING_TIME", "10")) # thời gian tính bằng giây

# Nếu bạn muốn nhận thông báo lỗi gửi trực tiếp vào tin nhắn cá nhân thì chọn True, ngược lại chọn False.
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))