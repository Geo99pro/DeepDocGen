import os
import numpy as np 
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer


# Helper link : https://www.scikit-yb.org/en/latest/faq.html
# https://www.scikit-yb.org/en/latest/api/cluster/silhouette.html
# https://www.scikit-yb.org/en/latest/api/cluster/elbow.html
# https://www.scikit-yb.org/en/latest/api/cluster/icdm.html
class GetClusterEngine:
    """
    This class is used to get the best clusters from the extracted embeddings.
    By calling this GetClusterEngine, user creates an instance of this class.

    Attributes:
        desired_clusters_list (tuple): A tuple containing the range of clusters to be evaluated.
        embeddings_extracted (dict): A dictionary containing the embeddings extracted.
        which_cluster_method (str): A string containing the method to be used to get the best cluster. It can be 'elbow' or 'silhouette'.
        n_init (int): An integer containing the number of times the K-means algorithm will be run with different centroid seeds.
        random_state (int): An integer containing the random state to be used for the K-means algorithm.
        path_to_save_graph (str): A string containing the path to save the graph of the best cluster based on the method used.

    Method:

        get_best_clusters(self): This method is used to get the best cluster from the extracted embeddings.
    """

    def __init__(self, desired_clusters_list: tuple, embeddings_extracted: dict, which_cluster_method: str, n_init: int, random_state: int, path_to_save_graph: str):
        self.desired_clusters_list = desired_clusters_list
        self.embeddings_extracted = embeddings_extracted
        self.which_cluster_method = which_cluster_method
        self.n_init = n_init
        self.random_state = random_state
        self.path_to_save_graph = path_to_save_graph

    def get_best_clusters(self):
        """
        This method is used to get the best cluster from the extracted embeddings.
        The method can use either elbow method or silhouette method to get the best cluster.
        It can also save the graph of the best cluster in a given path.

        Returns:
            best_cluster (int): An integer containing the best cluster.
        """

        if isinstance(self.embeddings_extracted, dict):
            embeddings_extracted = np.vstack(self.embeddings_extracted['embeddings_extracted'])
            self.embeddings_extracted = embeddings_extracted

        else:
            raise ValueError('The embeddings_extracted should be a dictionary containing the embeddings extracted. Check it out !')

        if self.which_cluster_method == 'elbow':
            print(f'Dear User, I am finding the best cluster with Elbow Method. Please wait for a while.')
            title = 'Elbow Method'
            Kmeans_model = KMeans(random_state=self.random_state, n_init=self.n_init)
            visualizer = KElbowVisualizer(Kmeans_model, k=self.desired_clusters_list, title=title)
            visualizer.fit(self.embeddings_extracted)
            best_cluster = visualizer.elbow_value_
            graph_path = os.path.join(self.path_to_save_graph, 'elbow_graph.png')
            visualizer.show(outpath=graph_path, clear_figure=True)
            return best_cluster

        elif self.which_cluster_method == 'silhouette':
            title = 'Silhouette Method'
            best_cluster = None
            best_score = -1
            
            for cluster in tqdm(range(self.desired_clusters_list[0], self.desired_clusters_list[1])):
                Kmeans_model = KMeans(n_clusters=cluster, random_state=self.random_state, n_init=self.n_init)
                labels = Kmeans_model.fit_predict(self.embeddings_extracted)
                score = silhouette_score(self.embeddings_extracted, labels)

                if score > best_score:
                    best_score = score
                    best_cluster = cluster

            Kmeans_model = KMeans(n_clusters=best_cluster, random_state=self.random_state, n_init=self.n_init)
            visualizer = SilhouetteVisualizer(Kmeans_model,  colors='yellowbrick', title=title)
            visualizer.fit(self.embeddings_extracted)
            graph_path = os.path.join(self.path_to_save_graph, 'silhouette_graph.png')
            visualizer.show(outpath=graph_path, clear_figure=True)
            return best_cluster

        elif self.which_cluster_method == 'Gap method':
            #To do
            pass
        
        else:
            raise ValueError('The "which_cluster_method" should be either elbow or silhouette. Check it out !')

        def visualize_intercluster_distance(): 
            #To do
            pass
