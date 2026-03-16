import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

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

for row in standings_table.select('tbody tr'):
    team_tag = row.select_one('a')
    if team_tag:
        full_link = "https://fbref.com" + team_tag['href']
        team_links.append(full_link)

for link in team_links:
    driver.get(link)
    time.sleep(15)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    standard_table = soup.find('table', id='stats_standard_9')
    tbody = standard_table.find('tbody')
    for row in tbody.find_all('tr'):
        player_cell = row.find(attrs={"data-stat": "player"})
        if player_cell is None:
            continue
        player_name = player_cell.text.strip()
        minutes_cell = row.find(attrs={"data-stat": "minutes"})
        minutes_text = minutes_cell.text.strip().replace(',', '') if minutes_cell else 0
        minutes = int(minutes_text) if minutes_text.isdigit() else 0
        if minutes > 90:
            print(player_name)

driver.quit()