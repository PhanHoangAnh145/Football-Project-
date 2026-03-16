import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import sqlite3

options = uc.ChromeOptions()

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
    time.sleep(5)
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT,
        nationality TEXT,
        position TEXT,
        age INTEGER,
        games INTEGER,
        games_starts INTEGER,
        minutes INTEGER,
        goals INTEGER,
        assists INTEGER,
        goals_assists INTEGER,
        goals_pens INTEGER,
        pens_made INTEGER,
        pens_att INTEGER,
        cards_yellow INTEGER,
        cards_red INTEGER
    )
''')
conn.commit()

for x in players_data:
    cursor.execute('''
        INSERT INTO players (player, nationality, position, age, games, games_starts, minutes, goals, assists, 
                   goals_assists, goals_pens, pens_made, pens_att, cards_yellow, cards_red)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        x.get('player', 'N/a'),
        x.get('nationality', 'N/a'),
        x.get('position', 'N/a'),
        int(x.get('age', 'N/a')),
        int(x.get('games', 'N/a')),
        int(x.get('games_starts', 'N/a')),
        int(x.get('minutes', 'N/a').replace(",", "")), # Ép kiểu về số nguyên 
        int(x.get('goals', 'N/a')),
        int(x.get('assists', 'N/a')),
        int(x.get('goals_assists', 'N/a')),
        int(x.get('goals_pens', 'N/a')),
        int(x.get('pens_made', 'N/a')),
        int(x.get('pens_att', 'N/a')),
        int(x.get('cards_yellow', 'N/a')),
        int(x.get('cards_red', 'N/a')),
    ))

# Lưu lại các thay đổi vào file .db
conn.commit()
conn.close()

driver.quit()