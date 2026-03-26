import sqlite3
import time
import random
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def get_value(driver, name, team, age, nationality):
    try:
        # 1. Luôn mở lại trang search → reset DOM
        driver.get("https://www.footballtransfers.com/en/search")
        wait = WebDriverWait(driver, 10)

        # 2. Tìm input và gõ tên
        search = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.search-field"))
        )
        search.clear()
        search.send_keys(name)
        search.send_keys(Keys.RETURN)

        # 3. Chờ kết quả hiện ra
        try:
            results = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".searchResults a"))
            )
        except Exception:
            return "N/a"

        # 4. Gom link
        player_links = []
        for r in results:
            link = r.get_attribute("href")
            if link and "players" in link:
                player_links.append(link)

        if not player_links:
            return "N/a"

        # --- CHUẨN BỊ TỪ KHÓA ---
        nat_keyword = str(nationality).split()[-1].upper() if nationality else ""
        team_words = [w for w in str(team).split() if len(w) > 3]

        try:
            db_age = int(age)
            allowed_ages = [db_age, db_age + 1, db_age + 2]
        except Exception:
            allowed_ages = [age]

        # 5. Đi thăm từng link
        for link in player_links:
            driver.get(link)
            
            try:
                price_element = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "span.player-tag"))
                )
                price = price_element.text.strip()
                
                # --- THU THẬP VÀ GỘP DỮ LIỆU TỪ 2 KHUNG CÙNG LÚC ---
                combined_text = ""
                
                # Khung 1: Profile (Để lấy Tuổi, Quốc tịch, Đội hiện tại)
                try:
                    profile_box = driver.find_element(By.CSS_SELECTOR, "article.playerProfile-panel")
                    combined_text += profile_box.text + " \n "
                except Exception:
                    pass
                
                # Khung 2: Transfer History (Để tìm Đội cũ)
                try:
                    history_box = driver.find_element(By.CSS_SELECTOR, "article.transferhistory-panel")
                    combined_text += history_box.text + " \n "
                except Exception:
                    pass
                
                # Nếu web đổi giao diện, không tìm thấy cả 2 khung trên, dùng phương án dự phòng
                if not combined_text.strip():
                    combined_text = driver.find_element(By.CSS_SELECTOR, "main").text[:2000]
                # ----------------------------------------------------

                # --- HỆ THỐNG CHẤM ĐIỂM ---
                match_score = 0
                
                # 1. Check Tuổi (Tìm trong đoạn text tổng hợp)
                age_matched = False
                for allowed_age in allowed_ages:
                    if f"{allowed_age} years old" in combined_text:
                        age_matched = True
                        break
                        
                if age_matched:
                    match_score += 1
                    
                # 2. Check Quốc tịch
                if nat_keyword and nat_keyword in combined_text:
                    match_score += 1
                    
                # 3. Check Đội bóng (quét qua cả phần Lịch sử chuyển nhượng)
                for word in team_words:
                    if word in combined_text:
                        match_score += 1
                        break 
                    
                if match_score >= 2:
                    return price
                    
            except Exception:
                continue

        return "N/a"

    except Exception as e:
        print(f"Lỗi khi xử lý {name}: {e}")
        return "N/a"


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "football.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT player, team, age, nationality FROM players")
    players_db = cursor.fetchall()

    cursor.execute("DROP TABLE IF EXISTS transfer_values")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfer_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            value TEXT
        )
    """)
    conn.commit()

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print(f"Bắt đầu tra giá cho {len(players_db)} cầu thủ...\n")

    for row in players_db:
        name = row[0]
        team = row[1]
        age = row[2]
        nationality = row[3]
        
        value = get_value(driver, name, team, age, nationality)

        print(f"{name} ({team} | Tuổi DB: {age} | {nationality}) => {value}")

        cursor.execute(
            "INSERT INTO transfer_values (player_name, value) VALUES (?, ?)",
            (name, value)
        )
        conn.commit()

        time.sleep(random.uniform(2, 4))

    driver.quit()
    conn.close()

    print("\n--- HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH ---")


if __name__ == "__main__":
    main()