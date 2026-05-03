import pandas as pd
import sqlite3
import os
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import seaborn as sns

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'football.db')

conn = sqlite3.connect(db_path)
df = pd.read_sql_query('SELECT * FROM players', conn)
conn.close()

features = df.select_dtypes(include='number').drop(columns=['id'], errors='ignore')

features = features.fillna(0) 

scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

wcss = []
silhouette_scores = []
K_range = range(2, 11)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_features)

    wcss.append(kmeans.inertia_)
    
    silhouette_avg = silhouette_score(scaled_features, cluster_labels)
    silhouette_scores.append(silhouette_avg)

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(K_range, wcss, marker='o', linestyle='--')
plt.title('Phương pháp Elbow')
plt.xlabel('Số lượng cụm (K)')
plt.ylabel('WCSS')

plt.subplot(1, 2, 2)
plt.plot(K_range, silhouette_scores, marker='s', color='green', linestyle='-')
plt.title('Điểm Silhouette')
plt.xlabel('Số lượng cụm (K)')
plt.ylabel('Silhouette Score')

plt.tight_layout()
plt.show()

optimal_k = 4 
final_kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['Cluster'] = final_kmeans.fit_predict(scaled_features)


pca_2d = PCA(n_components=2)
features_2d = pca_2d.fit_transform(scaled_features)
df['PCA1_2D'] = features_2d[:, 0]
df['PCA2_2D'] = features_2d[:, 1]

plt.figure(figsize=(8, 6))
sns.scatterplot(x='PCA1_2D', y='PCA2_2D', hue='Cluster', palette='viridis', data=df)
plt.title('Phân cụm cầu thủ trên mặt phẳng 2D (PCA)')
plt.show()

pca_3d = PCA(n_components=3)
features_3d = pca_3d.fit_transform(scaled_features)
df['PCA1_3D'] = features_3d[:, 0]
df['PCA2_3D'] = features_3d[:, 1]
df['PCA3_3D'] = features_3d[:, 2]

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
scatter = ax.scatter(df['PCA1_3D'], df['PCA2_3D'], df['PCA3_3D'], c=df['Cluster'], cmap='viridis')
ax.set_title('Phân cụm cầu thủ trong không gian 3D (PCA)')
ax.set_xlabel('PCA 1')
ax.set_ylabel('PCA 2')
ax.set_zlabel('PCA 3')
legend = ax.legend(*scatter.legend_elements(), title="Clusters")
ax.add_artist(legend)
plt.show()