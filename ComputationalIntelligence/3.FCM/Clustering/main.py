import pandas as pd
from FCM_C_Means import FCM

data = pd.read_csv("data/sample1.csv")

cluster = FCM(data=data, number_of_clusters=4, m=2, error=0.007, random_state=42)

cluster.fit()

# plot the result
cluster.plot()
# plot the clustering regions
cluster.plot_clustering_regions()
# plot the performance_index and entropy and cost for different number of clusters
cluster.plot_fcp()
