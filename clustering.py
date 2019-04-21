import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def create_clusters(bat_stats_in='data/bat_stats.csv', bowl_stats_in='data/bowl_stats.csv',
                    bat_stats_out='data/bat_clusters.csv', bowl_stats_out='data/bowl_clusters.csv',
                    n_bat_clusters=5, n_bowl_clusters=5):
    # Batsman clusters
    df = pd.read_csv(bat_stats_in)
    bat_features = ['Inn', 'NO', 'Avg', 'SR']
    points = df.loc[:, bat_features]
    points = points.astype(float).fillna(0)
    points = StandardScaler().fit_transform(points)

    pca = PCA(n_components=2)
    points = pca.fit_transform(points)

    new_df = pd.DataFrame(data=points, columns=['X', 'Y'])

    plt.subplot(2, 2, 1)
    plt.scatter(new_df.X, new_df.Y)
    plt.title('Batting Stats - PCA Transformed points')

    kmeans = KMeans(n_clusters=n_bat_clusters)
    fit = kmeans.fit(points)

    df['Cluster'] = fit.labels_
    clusters = [g[1] for g in df.groupby('Cluster')]
    plt.subplot(2, 2, 2)
    plt.title('Batting Clusters - Post PCA Transformation')
    new_df['Cluster'] = fit.labels_
    colors = ['r', 'g', 'blue', 'black',
                'yellow', 'orange', 'magenta', 'purple']
    i = 0
    for c in new_df.groupby('Cluster'):
            plt.scatter(c[1].X, c[1].Y, c=colors[i])
            i += 1

    """
    for c in clusters:
        print(c)
        print()
        print()
    """

    with open(bat_stats_out, 'w') as f:
        df.to_csv(f)
        f.close()

    # Bowler clusters
    df = pd.read_csv(bowl_stats_in)
    bowl_features = ['Inn', 'Econ', 'Avg', 'SR']
    points = df.loc[:, bowl_features]
    points = points.astype(float).fillna(0)

    points = StandardScaler().fit_transform(points)

    pca = PCA(n_components=2)
    points = pca.fit_transform(points)

    new_df = pd.DataFrame(data=points, columns=['X', 'Y'])

    plt.subplot(2, 2, 3)
    plt.scatter(new_df.X, new_df.Y)
    plt.title('Bowling Stats - PCA Transformed points')

    kmeans = KMeans(n_clusters=n_bowl_clusters)
    fit = kmeans.fit(points)

    plt.subplot(2, 2, 4)
    plt.title('Bowling Clusters - Post PCA Transform')
    new_df['Cluster'] = fit.labels_
    i = 0
    for c in new_df.groupby('Cluster'):
        plt.scatter(c[1].X, c[1].Y, c=colors[i])
        i += 1

    df['Cluster'] = fit.labels_
    
    """
    clusters = [g[1] for g in df.groupby('Cluster')]
    for c in clusters:
        print(c)
        print()
        print()
    """
    with open(bowl_stats_out, 'w') as f:
        df.to_csv(f)
        f.close()

    plt.show()

if __name__ == '__main__':
    create_clusters()