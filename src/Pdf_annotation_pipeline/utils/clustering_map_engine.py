import os
import pandas as pd
import plotly.express as px

class ClusteringMapEngine:
    """
    This class is responsible for visualize in 2D space the clusters of the best reduced embeddings.
    By using this class, you can visualize the clusters of the best reduced embeddings in 2D space.

    Method:

        visualize_clusters: This method visualizes the clusters of the best reduced embeddings in 2D space.
    """

    def visualize_clusters(self, best_embeddings_df: pd.DataFrame, 
                           path_to_save_cluster_map: str)-> None:
        """
        This method visualizes the clusters of the best reduced embeddings in 2D space.
        
        Args:
            - best_embeddings_df: The best reduced embeddings with clusters in a dataframe format.
            - path_to_save_cluster_map: The path to save the cluster map.
            
        Returns:
            - None. However, it saves the cluster map in the given path.
        """

        df = best_embeddings_df.drop('Pdf_page_name', axis=1)
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], color='Cluster', hover_data=['Cluster'])
        fig.update_layout(title='Clusters in 2D space', template='plotly_dark')
        figure_path = os.path.join(path_to_save_cluster_map, 'clusters_in_2D_space.png')
        fig.write_image(figure_path)