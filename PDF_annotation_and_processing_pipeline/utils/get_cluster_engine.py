import os
import numpy as np 
from tqdm import tqdm
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans


# Helper link : https://www.scikit-yb.org/en/latest/faq.html
# https://www.scikit-yb.org/en/latest/api/cluster/silhouette.html
# https://www.scikit-yb.org/en/latest/api/cluster/elbow.html
# https://www.scikit-yb.org/en/latest/api/cluster/icdm.html
class GetClusterEngine:
    """
    This class is used to get the best clusters from the extracted embeddings.
    By calling this GetClusterEngine, user creates an instance of this class.

    Method:

        get_best_clusters(self): This method is used to get the best cluster from the extracted embeddings.
    """

    def get_best_clusters(self,
                          desired_clusters_list: tuple,
                          embeddings_extracted: dict,
                          which_cluster_method: str,
                          n_init: int,
                          random_state: int,
                          path_to_save_graph: str)-> int:

        """
        This method is used to get the best cluster from the extracted embeddings.
        The method can use either elbow method or silhouette method to get the best cluster.
        It can also save the graph of the best cluster in a given path.

        Args:
            - desired_clusters_list (tuple): A tuple containing the desired clusters.
            - embeddings_extracted (dict): A dictionary containing the embeddings extracted.
            - which_cluster_method (str): A string containing the method to get the best cluster. It can be either elbow or silhouette.
            - n_init (int): An integer containing the number of times the KMeans algorithm will run with different centroid seeds.
            - random_state (int): An integer containing the random state.
            - path_to_save_graph (str): A string containing the path to save the graph.

        Returns:
            best_cluster (int): An integer containing the best cluster.
        """

        if isinstance(embeddings_extracted, dict):
            embeddings_extracted = np.vstack(embeddings_extracted['embeddings_extracted'])

        else:
            raise ValueError('The embeddings_extracted should be a dictionary containing the embeddings extracted. Check it out !')

        if which_cluster_method == 'elbow':
            print(f'Dear User, I am finding the best cluster with Elbow Method. Please wait for a while.')
            title = 'Elbow Method'
            Kmeans_model = KMeans(random_state=random_state, n_init=n_init)
            visualizer = KElbowVisualizer(Kmeans_model, k=desired_clusters_list, title=title)
            visualizer.fit(embeddings_extracted)
            best_cluster = visualizer.elbow_value_
            file_path = os.path.join(path_to_save_graph, 'elbow_graph.png')
            visualizer.show(outpath=file_path)
            return best_cluster

        elif which_cluster_method == 'silhouette':
            title = 'Silhouette Method'
            best_cluster = None
            best_score = -1
            
            print(f'Dear User, I am finding the best cluster with Silhouette Method. Please wait for a while.')
            for cluster in tqdm(range(desired_clusters_list[0], desired_clusters_list[1])):
                Kmeans_model = KMeans(n_clusters=cluster, random_state=random_state, n_init=n_init)
                labels = Kmeans_model.fit_predict(embeddings_extracted)
                score = silhouette_score(embeddings_extracted, labels)

                if score > best_score:
                    best_score = score
                    best_cluster = cluster

            Kmeans_model = KMeans(n_clusters=best_cluster, random_state=random_state, n_init=n_init)
            visualizer = SilhouetteVisualizer(Kmeans_model,  colors='yellowbrick', title=title)
            visualizer.fit(embeddings_extracted)
            file_path = os.path.join(path_to_save_graph, 'silhouette_graph.png')
            visualizer.show(outpath=file_path)
            return best_cluster

        else:
            raise ValueError('The which_cluster_method should be either elbow or silhouette. Check it out !')

        def visualize_intercluster_distance(): 
            #To do
            pass
