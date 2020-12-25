from sklearn.datasets import make_blobs
from sklearn import metrics
from sklearn.cluster import KMeans
import time

def main(param):

    start = time.time()
    
    for _ in range(20):
        # X为样本特征，Y为样本簇类别， 共1000个样本，每个样本2个特征，共4个簇，簇中心在[-1,-1], [0,0],[1,1], [2,2]， 簇方差分别为[0.4, 0.2, 0.2]
        X, y = make_blobs(n_samples=1000, n_features=2, centers=[[-1,-1], [0,0], [1,1], [2,2]], cluster_std=[0.4, 0.2, 0.2, 0.2], 
                    random_state =9)

        y_pred = KMeans(n_clusters=4, random_state=9).fit_predict(X)

        print('calinski Harabasz score:', metrics.calinski_harabasz_score(X, y_pred))

    print('latency:', time.time() - start)

