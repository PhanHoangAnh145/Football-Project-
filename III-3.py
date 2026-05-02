import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'football.db')

conn = sqlite3.connect(db_path)
df = pd.read_sql_query('SELECT * FROM players', conn)
conn.close()

df_outfield = df[df['position'] != 'GK'].copy()

numeric_cols = df_outfield.select_dtypes(include='number').columns.tolist()
if 'id' in numeric_cols:
    numeric_cols.remove('id')

X = df_outfield[numeric_cols].fillna(0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

inertia = []
silhouette_scores = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    
    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(K_range, inertia, marker='o', linestyle='-', color='b')
ax1.set_title('Biểu đồ Elbow (Tìm điểm "gãy")')
ax1.set_xlabel('Số lượng cụm (K)')
ax1.set_ylabel('Inertia (Độ phân tán)')

ax2.plot(K_range, silhouette_scores, marker='s', linestyle='-', color='orange')
ax2.set_title('Biểu đồ Silhouette (Chỉ số càng cao càng tốt)')
ax2.set_xlabel('Số lượng cụm (K)')
ax2.set_ylabel('Silhouette Score')

plt.tight_layout()
plt.show()