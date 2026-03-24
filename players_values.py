import undetected_chromedriver as uc
import sqlite3
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def crawl_transfer_values():
    # 1. Kết nối database cũ để lấy tên cầu thủ
    try:
        conn = sqlite3.connect('football.db')
        cursor = conn.cursor()
        cursor.execute("SELECT player FROM players")
        # Lấy danh sách tên cầu thủ (unique) để tránh cào trùng
        players = [row[0] for row in cursor.fetchall()]

        # Tạo bảng mới cho giá chuyển nhượng
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS transfer_values
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           player_name
                           TEXT,
                           value
                           TEXT
                       )
                       ''')
        conn.commit()
    except Exception as e:
        print(f"Lỗi kết nối DB: {e}")
        return

    # 2. Khởi tạo Driver
    options = uc.ChromeOptions()
    # FootballTransfers rất nhạy cảm, nên để cửa sổ hiện ra để tránh bị bot detection
    driver = uc.Chrome(options=options)

    print(f"Bắt đầu cào giá cho {len(players)} cầu thủ...")

    try:
        for name in players:
            # Kiểm tra xem cầu thủ này đã có giá trong bảng transfer_values chưa (tránh cào lại nếu chạy dở)
            cursor.execute("SELECT player_name FROM transfer_values WHERE player_name = ?", (name,))
            if cursor.fetchone():
                continue

            try:
                # Format URL: Chuyển "Darwin Núñez" thành "darwin-nunez"
                # Lưu ý: Một số cầu thủ có tên đặc biệt có thể cần search thay vì vào thẳng URL
                slug = name.lower().replace(" ", "-")
                url = f"https://www.footballtransfers.com/en/players/{slug}"

                driver.get(url)

                # Chờ element chứa giá (ETV - Estimated Transfer Value)
                # Selector này dựa trên cấu trúc hiện tại của FootballTransfers
                wait = WebDriverWait(driver, 8)
                value_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.player-tag, div.price-tag, .etv-value")
                ))

                transfer_value = value_element.text.strip()
                if not transfer_value:
                    transfer_value = "N/a"

            except Exception:
                # Nếu không vào được thẳng URL, ta có thể thử dùng thanh Search (optional)
                transfer_value = "N/a"

            # 3. Lưu vào database ngay lập tức
            cursor.execute("INSERT INTO transfer_values (player_name, value) VALUES (?, ?)", (name, transfer_value))
            conn.commit()
            print(f"Cầu thủ: {name} | Giá: {transfer_value}")

            # Nghỉ ngẫu nhiên để tránh bị block (Rate-limit)
            time.sleep(random.uniform(2, 5))

    except KeyboardInterrupt:
        print("Dừng chương trình bởi người dùng.")
    finally:
        conn.close()
        driver.quit()
        print("--- HOÀN THÀNH PHẦN I.2 ---")


if __name__ == "__main__":
    crawl_transfer_values()