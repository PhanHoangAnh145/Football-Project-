# Football Player Search Project

Dự án tìm kiếm thông tin cầu thủ bóng đá với frontend và backend.

## Cấu trúc project

- `app.py` - Flask API server
- `index.html` - Frontend HTML/CSS/JavaScript
- `football.db` - Database SQLite chứa thông tin cầu thủ
- `players_stats.py` - Script crawl dữ liệu từ fbref.com

## Cách chạy

### 1. Khởi động backend API
```bash
python app.py
```
Server sẽ chạy tại http://localhost:5000

### 2. Mở frontend
Mở file `index.html` trong trình duyệt hoặc chạy một web server đơn giản:
```bash
# Nếu có Python
python -m http.server 8000

# Hoặc mở trực tiếp file index.html
```

## Tính năng

- 🔍 Tìm kiếm cầu thủ theo tên
- 📊 Hiển thị thông tin chi tiết dạng bảng
- 🎨 Giao diện responsive đẹp mắt
- ⚡ Real-time search với API

## API Endpoints

- `GET /api/player?name=<tên_cầu thủ>` - Tìm cầu thủ theo tên
- `GET /api/nationality?name=<quốc_tịch>` - Tìm cầu thủ theo quốc tịch

## Database schema

Bảng `players` chứa các trường:
- player, nationality, position, age
- games, games_starts, minutes, minutes_90s
- goals, assists, goals_assists, goals_pens
- pens_made, pens_att, cards_yellow, cards_red
- goals_per90, assists_per90, goals_assists_per90
- goals_pens_per90, goals_assists_pens_per90