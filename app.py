from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# Cấu hình CORS để Browser không chặn yêu cầu từ file index.html
CORS(app)

DB_NAME = 'football.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/player', methods=['GET'])
def get_player_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Vui lòng nhập tên cầu thủ"}), 400

    conn = get_db_connection()
    # Tìm kiếm chính xác tên cầu thủ
    player = conn.execute('SELECT * FROM players WHERE player = ?', (name,)).fetchone()
    conn.close()

    if player is None:
        return jsonify({"message": f"Không tìm thấy cầu thủ '{name}'"}), 404

    # Chuyển đổi Row thành Dictionary để trả về JSON
    return jsonify(dict(player))

# API này để hỗ trợ nếu bạn muốn mở rộng tìm kiếm theo nhóm (Quốc tịch/CLB)
@app.route('/api/club', methods=['GET'])
def get_players_by_club():
    club = request.args.get('name')
    conn = get_db_connection()
    # Nếu DB của bạn có cột 'club', dùng cái này. Nếu không, tạm thời để trả về lỗi 404
    try:
        players = conn.execute('SELECT * FROM players WHERE club = ?', (club,)).fetchall()
        conn.close()
        return jsonify([dict(row) for row in players])
    except sqlite3.OperationalError:
        return jsonify({"message": "Tính năng tìm theo CLB chưa sẵn sàng vì thiếu cột 'club'"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)