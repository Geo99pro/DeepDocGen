import numpy as np 
from sklearn.cluster import KMeans

# https://www.alura.com.br/artigos/clusterizacao?srsltid=AfmBOooTiDenl3BNTNzQ5RKefEGSN1UpafD71pOGjrghOThdyCmKw8uj
class TrainKmeansEngine:
    """
    This class is used to train the K-means algorithm to get the predicted clusters.
    By calling this TrainKmeansEngine, user creates an instance of this class.

    Attributes:
        embeddings_extracted (dict): A dictionary containing the embeddings extracted.
        n_clusters (int): An integer containing the number of clusters to be created.
        n_init (int): An integer containing the number of times the K-means algorithm will be run with different centroid seeds.
        random_state (int): An integer containing the random state to be used for the K-means algorithm.

    Method:

        get_predicted_clusters(): This method is used to get the predicted clusters from the extracted embeddings.
    """

    def __init__(self, embeddings_extracted: dict, best_cluster: int, n_init: str, random_state: int):
        self.embeddings_extracted = embeddings_extracted
        self.best_cluster = best_cluster
        self.n_init = n_init
        self.random_state = random_state

    def get_predicted_clusters(self):

        if isinstance(self.embeddings_extracted, dict):
            embeddings_extracted = np.vstack(self.embeddings_extracted['embeddings_extracted'])
            self.embeddings_extracted = embeddings_extracted

        else:
            raise ValueError('The embeddings_extracted should be a dictionary containing the embeddings extracted. Check it out!')

        Model = KMeans(n_clusters=self.best_cluster, random_state=self.random_state, n_init=self.n_init)
        predicted_clusters = Model.fit_predict(self.embeddings_extracted)
        return predicted_clusters
