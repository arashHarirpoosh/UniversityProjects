import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class KMeans:
    # Read The Data From CSV File
    def read_data(self, addr):
        df = pd.read_csv(addr)
        return df.values

    def find_initial_points(self, data, k, min_distance):
        num_of_data = len(data)
        centroids = []
        while len(centroids) < k:
            remained_cluster_points = k - len(centroids)
            random_index = np.random.choice(num_of_data, remained_cluster_points, replace=False)
            centroids_temp = data.iloc[random_index]
            for d in range(remained_cluster_points):
                distances = []
                # print(len(centroids_temp))
                for t in range(remained_cluster_points):
                    if t != d:
                        distances.append(np.linalg.norm(centroids_temp.iloc[d] - centroids_temp.iloc[t]))
                for c in centroids:
                    # print(len(c), len(centroids_temp.iloc[d]))
                    if not (c == centroids_temp.iloc[d]).all():
                        distances.append(np.linalg.norm(centroids_temp.iloc[d] - c))
                # print(distances)
                if all([True if x > min_distance else False for x in distances]):
                    centroids.append(centroids_temp.iloc[d])
            # print('centroids:', centroids)
        return np.array(centroids)

    # Assign Each Point Into The Closest Centroid
    @staticmethod
    def find_data_cluster(data, center):
        num_of_data = data.shape[0]
        k = center.shape[0]
        num_of_each_cluster_data = np.zeros(shape=(k,))
        cluster = []
        for i, d in data.iterrows():
            min_dist = float('inf')
            selected_cluster = None
            for c in range(k):
                dist = np.linalg.norm(d - center[c])
                if dist < min_dist:
                    min_dist = dist
                    selected_cluster = c
            cluster.append((selected_cluster, [x1 for x1 in d]))
            num_of_each_cluster_data[selected_cluster] += 1
        cluster = np.array(cluster, dtype=tuple)
        return cluster, num_of_each_cluster_data

    # Calculate The Distances Between New And Old Centroids
    @staticmethod
    def calculate_distances_between_centroid(cntr1, cntr2):
        num_of_clusters = cntr1.shape[0]
        dist = 0
        for ce in range(num_of_clusters):
            # print(cntr2[ce].shape, cntr1[ce].shape)
            dist += np.linalg.norm(cntr2[ce] - cntr1[ce])
        return dist

    # Calculate The Error Of Each Cluster
    @staticmethod
    def each_cluster_error(center, points):
        dist = [np.square(np.linalg.norm(center - p)) for p in points]
        return np.array(dist).sum()

    # Calculate The Average Cluster Error
    def average_cluster_error(self, center, points):
        cluster_error = 0
        cluster_size = center.shape[0]
        for c in range(cluster_size):
            cluster_error += self.each_cluster_error(center[c], points[c]) / cluster_size
        return cluster_error

    def calculate_rss(self, centroids, clusters):
        clustering_error = 0
        for ci, p in clusters:
            error = np.square(np.linalg.norm(p - centroids[ci]))
            clustering_error += error
        return clustering_error

    # Clustering Data With KMeans Algorithm
    def clustering(self, data, k, iteration_info=False, num_of_iteration=15, min_initial_centroids_dist=12.5,
                   min_centroids_dist=0.0001, min_num_of_each_cluster_data=3):
        clusters = {}
        num_of_data = data.shape[0]
        # Initialize Random Points For Centers
        # random_index = np.random.choice(num_of_data, k, replace=False)
        # centroids = data.iloc[random_index].to_numpy()

        centroids = self.find_initial_points(data=data, k=k, min_distance=min_initial_centroids_dist)
        print(centroids.shape)
        num_of_each_cluster_data = [0, 0]
        for i in range(num_of_iteration):
            # Assign Each Point Into The Closest Centroid
            clusters, num_of_each_cluster_data[i % 2] = self.find_data_cluster(data, centroids)
            new_centroids = []
            for uc in range(k):
                r, c = np.where(clusters == uc)
                cst = [x for x in clusters[r, 1]]
                new_centroids.append(np.array(cst).mean(axis=0))

            dist_between_centroids = self.calculate_distances_between_centroid(centroids, np.array(new_centroids))
            diff_each_cluster_data = np.sum(abs(num_of_each_cluster_data[0] - num_of_each_cluster_data[1]))
            centroids = np.array([x for x in new_centroids])
            if iteration_info:
                print('K =', k, 'Iteration:', i, ', Error Rate:', self.average_cluster_error(centroids, clusters),
                      ', Number Of Points That Changed Between Clusters:', diff_each_cluster_data,
                      'Distance Between Old And New Centroids:', dist_between_centroids)
            if diff_each_cluster_data < min_num_of_each_cluster_data \
                    or dist_between_centroids < min_centroids_dist:
                break
        # Assign Each Point Into The Closest Centroid
        clusters, _ = self.find_data_cluster(data, centroids)
        return centroids, clusters

    # Plot The Clustering Result
    def plot_cluster(self, cntr, cluster):
        c_key = cluster.keys()
        color_map = ['b', 'm', 'c', 'r', 'g', 'orange', 'y', 'Brown', 'ForestGreen']
        for c in range(len(c_key)):
            x = np.array(cluster[c])[:, 0]
            y = np.array(cluster[c])[:, 1]
            x_c = cntr[:, 0]
            y_c = cntr[:, 1]
            plt.scatter(x, y, color=color_map[c])
            plt.scatter(x_c, y_c, marker='*', color='k', s=350)
        plt.title('KMeans\nk=' + str(len(cluster)))
        plt.show()

    # Plot The KMeans Error For K Less Than max_k
    def plot_k_means_error(self, data, min_k=1, max_k=15):
        all_errors = []
        all_rss = []
        for k in range(min_k, max_k):
            cnt, clt = self.clustering(data, k, min_initial_centroids_dist=10 - (k/10))
            error = self.average_cluster_error(cnt, clt)
            error_rss = self.calculate_rss(cnt, clt)
            print('Error Rate For K =', k, ':', error)
            print('Error RSS For K =', k, ':', error_rss)
            all_errors.append(error)
            all_rss.append(error_rss)

        x = range(min_k, max_k)
        plt.plot(x, all_errors, label='Average Error')
        plt.plot(x, all_rss, label='RSS Error')
        plt.legend(loc="upper left")
        plt.savefig(f'Elbow_{max_k}.png')
        plt.show()
