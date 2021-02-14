import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# Read The Data From CSV File
def read_data(addr):
    df = pd.read_csv(addr)
    return df.values


# Assign Each Point Into The Closest Centroid
def find_data_cluster(data, center, cluster):
    num_of_data = data.shape[0]
    k = center.shape[0]
    num_of_each_cluster_data = np.zeros(shape=(k, ))
    for d in range(num_of_data):
        min_dist = float('inf')
        selected_cluster = None
        for c in range(k):
            dist = np.linalg.norm(data[d] - center[c])
            if dist < min_dist:
                min_dist = dist
                selected_cluster = c
        cluster[selected_cluster].append([x1 for x1 in data[d]])
        num_of_each_cluster_data[selected_cluster] += 1
    return num_of_each_cluster_data


# Calculate The Distances Between New And Old Centroids
def calculate_distances_between_centroid(cntr1, cntr2):
    num_of_clusters = cntr1.shape[0]
    dist = 0
    for ce in range(num_of_clusters):
        dist += np.linalg.norm(cntr2[ce] - cntr1[ce])
    return dist


# Calculate The Error Of Each Cluster
def each_cluster_error(center, points):
    dist = [np.linalg.norm(center - p) for p in points]
    return np.array(dist).mean()


# Calculate The Average Cluster Error
def average_cluster_error(center, points):
    cluster_error = 0
    cluster_size = center.shape[0]
    for c in range(cluster_size):
        cluster_error += each_cluster_error(center[c], points[c]) / cluster_size
    return cluster_error


# Clustering Data With KMeans Algorithm
def k_mean(data, k, iteration_info=False, num_of_iteration=15,
           min_centroids_dist=0.0001, min_num_of_each_cluster_data=3):
    clusters = {}
    num_of_data = data.shape[0]
    # Initialize Random Points For Centers
    random_index = np.random.choice(num_of_data, k, replace=False)
    centroids = data[random_index]
    num_of_each_cluster_data = [0, 0]
    for i in range(k):
        clusters[i] = [centroids[i]]

    for i in range(num_of_iteration):
        # Assign Each Point Into The Closest Centroid
        num_of_each_cluster_data[i % 2] = find_data_cluster(data, centroids, clusters)
        new_centroids = []
        for uc in range(k):
            new_centroids.append(np.array(clusters[uc]).mean(axis=0))
            clusters[uc] = []
            clusters[uc].append([x1 for x1 in centroids[uc]])
        dist_between_centroids = calculate_distances_between_centroid(centroids, np.array(new_centroids))
        diff_each_cluster_data = np.sum(abs(num_of_each_cluster_data[0] - num_of_each_cluster_data[1]))
        centroids = np.array([x for x in new_centroids])
        if iteration_info:
            print('K =', k, 'Iteration:', i, ', Error Rate:', average_cluster_error(centroids, clusters),
                  ', Number Of Points That Changed Between Clusters:', diff_each_cluster_data,
                  'Distance Between Old And New Centroids:', dist_between_centroids)
        if diff_each_cluster_data < min_num_of_each_cluster_data \
                or dist_between_centroids < min_centroids_dist:
            break
    # Assign Each Point Into The Closest Centroid
    find_data_cluster(data, centroids, clusters)
    return centroids, clusters


# Plot The Clustering Result
def plot_cluster(cntr, cluster):
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
def plot_k_means_error(data, max_k=15):
    all_errors = []
    for k in range(1, max_k):
        cnt, clt = k_mean(data, k)
        error = average_cluster_error(cnt, clt)
        print('Error Rate For K =', k, ':', error)
        all_errors.append(error)
    plt.plot(range(1, max_k), all_errors)
    plt.savefig('Elbow.png')
    plt.show()


