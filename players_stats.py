import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import sqlite3
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_my_code():
    # Khởi động trình duyệt
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=145)

    url = "https://fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats"
    print(f"Đang truy cập: {url}")
    driver.get(url)

    time.sleep(15) # Đợi trang chủ tải xong

    # Lấy mã HTML tĩnh
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    standings_table = soup.select_one('table.stats_table')

    # Dùng team_info để lưu cả Tên đội bóng và Link
    team_info = []
    players_data = []

    for row in standings_table.select('tbody tr'):
        team_tag = row.select_one('a')
        if team_tag:
            team_name = team_tag.text.strip() # Lấy tên CLB
            full_link = "https://fbref.com" + team_tag['href']
            team_info.append((team_name, full_link))

    print(f"Tìm thấy {len(team_info)} đội bóng. Bắt đầu cào dữ liệu cầu thủ...")

    for team_name, link in team_info:
        print(f"Đang xử lý đội: {team_name}")
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
            stats['team'] = team_name

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

    # --- PHẦN LƯU DATABASE ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'football.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS players')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT, 
            team TEXT, 
            nationality TEXT, position TEXT, age INTEGER,
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
        try:
            cursor.execute('''
                INSERT INTO players (player, team, nationality, position, age, games, games_starts, minutes, minutes_90s, goals, assists, 
                           goals_assists, goals_pens, pens_made, pens_att, cards_yellow, cards_red, goals_per90, assists_per90, 
                           goals_assists_per90, goals_pens_per90, goals_assists_pens_per90)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                x.get('player'), 
                x.get('team'), # Lưu tên đội bóng vào cột team
                x.get('nationality'), x.get('position'),
                int(x.get('age', 0)), int(x.get('games', 0)), int(x.get('games_starts', 0)),
                int(x.get('minutes', '0').replace(",", "")), float(x.get('minutes_90s', 0)),
                int(x.get('goals', 0)), int(x.get('assists', 0)), int(x.get('goals_assists', 0)),
                int(x.get('goals_pens', 0)), int(x.get('pens_made', 0)), int(x.get('pens_att', 0)),
                int(x.get('cards_yellow', 0)), int(x.get('cards_red', 0)),
                float(x.get('goals_per90', 0)), float(x.get('assists_per90', 0)),
                float(x.get('goals_assists_per90', 0)), float(x.get('goals_pens_per90', 0)),
                float(x.get('goals_assists_pens_per90', 0))
            ))
        except Exception as e:
            print(f"Lỗi khi lưu cầu thủ {x.get('player')}: {e}")
            continue

    conn.commit()
    conn.close()
    
    print(f"\n--- {len(players_data)} CẦU THỦ ĐÃ LƯU THÀNH CÔNG VÀO DATABASE! ---")
    
    try:
        driver.quit()  
    except:
        pass
    finally:
        del driver

if __name__ == "__main__":
    run_my_code()