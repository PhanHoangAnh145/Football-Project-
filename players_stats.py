import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Hàm bao quanh code cũ của bạn
def run_my_code():
    options = uc.ChromeOptions()
    # THÊM: Chỉ định bản 145 để khớp với Chrome của Phan
    driver = uc.Chrome(options=options, version_main=145)

    url = "https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats"
    driver.get(url)

    time.sleep(15)

    # Lấy mã HTML tĩnh
    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    standings_table = soup.select_one('table.stats_table')

    team_links = []
    players_data = []

    for row in standings_table.select('tbody tr'):
        team_tag = row.select_one('a')
        if team_tag:
            full_link = "https://fbref.com" + team_tag['href']
            team_links.append(full_link)

    for link in team_links:
        driver.get(link)

        # Đợi đến khi bảng load xong
        WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,"stats_standard_9"))
        )

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        standard_table = soup.find('table', id='stats_standard_9')
        tbody = standard_table.find('tbody')

        for row in tbody.find_all('tr'):
            player_cell = row.find("th", {"data-stat": "player"})
            if player_cell is None:
                continue

            stats = {}
            for cell in row.find_all(["td", "th"]):
                stat_name = cell.get("data-stat")
                stat_value = cell.text.strip()
                stats[stat_name] = stat_value

            minutes = stats.get("minutes", "0")
            minutes = minutes.replace(",", "").strip()

            try:
                minutes = int(minutes)
            except:
                minutes = 0

            if minutes > 90:
                players_data.append(stats)

    conn = sqlite3.connect('football.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS players')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT, nationality TEXT, position TEXT, age INTEGER,
            games INTEGER, games_starts INTEGER, minutes INTEGER,
            minutes_90s FLOAT, goals INTEGER, assists INTEGER,
            goals_assists INTEGER, goals_pens INTEGER, pens_made INTEGER,
            pens_att INTEGER, cards_yellow INTEGER, cards_red INTEGER,
            goals_per90 FLOAT, assists_per90 FLOAT, goals_assists_per90 FLOAT,
            goals_pens_per90 FLOAT, goals_assists_pens_per90 FLOAT
        )
    ''')
    conn.commit()

    for x in players_data:
        # THÊM: bọc Try-Except ở đây để nếu 1 cầu thủ lỗi dữ liệu thì không dừng cả chương trình
        try:
            cursor.execute('''
                INSERT INTO players (player, nationality, position, age, games, games_starts, minutes, minutes_90s, goals, assists, 
                           goals_assists, goals_pens, pens_made, pens_att, cards_yellow, cards_red, goals_per90, assists_per90, 
                           goals_assists_per90, goals_pens_per90, goals_assists_pens_per90)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                x.get('player'), x.get('nationality'), x.get('position'),
                int(x.get('age', 0)), int(x.get('games', 0)), int(x.get('games_starts', 0)),
                int(x.get('minutes', '0').replace(",", "")), float(x.get('minutes_90s', 0)),
                int(x.get('goals', 0)), int(x.get('assists', 0)), int(x.get('goals_assists', 0)),
                int(x.get('goals_pens', 0)), int(x.get('pens_made', 0)), int(x.get('pens_att', 0)),
                int(x.get('cards_yellow', 0)), int(x.get('cards_red', 0)),
                float(x.get('goals_per90', 0)), float(x.get('assists_per90', 0)),
                float(x.get('goals_assists_per90', 0)), float(x.get('goals_pens_per90', 0)),
                float(x.get('goals_assists_pens_per90', 0))
            ))
        except:
            continue

    conn.commit()
    conn.close()
    driver.quit()
    print("--- CHÚC MỪNG PHAN, DỮ LIỆU ĐÃ LƯU THÀNH CÔNG VÀO DATABASE! ---")
    try:
        # driver.close()  # Đóng cửa sổ trước
        driver.quit()  # Thoát hẳn trình duyệt
    except:
        pass
    finally:
        # Buộc Python quên driver đi, tránh việc gọi __del__ lần nữa
        del driver
    # Nếu có lỗi handle thì kệ nó, bỏ qua luôn

# THÊM: Dòng này là bắt buộc để không bị lỗi WinError 6 trên Windows
if __name__ == "__main__":
    run_my_code()