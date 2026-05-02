import pandas as pd
import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'football.db')

conn = sqlite3.connect(db_path)
query = 'SELECT * FROM players'
df = pd.read_sql_query(query, conn)

numeric_cols = df.select_dtypes(include='number').columns.tolist()

if 'id' in numeric_cols:
    numeric_cols.remove('id')

cols_to_group = ['team'] + numeric_cols

df_numeric_only = df[cols_to_group]

team_stats = df_numeric_only.groupby('team').agg(['median', 'mean', 'std'])
csv_path = os.path.join(current_dir, 'team_statistics.csv')
team_stats.to_csv(csv_path)

print(f'Đã lưu kết quả thống kê vào file: {csv_path} ')

team_mean = df_numeric_only.groupby('team').mean()

best_team_per_metric = team_mean.idxmax()

print('\n --- ĐỘI BÓNG DẪN ĐẦU TỪNG CHỈ SỐ ---')
print(best_team_per_metric.head(15))
best_team_per_metric.to_csv(os.path.join(current_dir, 'leading_team.csv'))
