import os
import pandas as pd
import plotly.express as px

class ClusteringMapEngine:
    """
    This class is responsible for visualize in 2D space the clusters of the best reduced embeddings.
    By using this class, you can visualize the clusters of the best reduced embeddings in 2D space.

    Attributes:
        best_reduced_embeddings (pd.DataFrame): A pandas DataFrame containing the best reduced embeddings and the labels of the clusters.
        path_to_save_cluster_map (str): A string containing the path to save the plot of the clusters in 2D space.

    Method:

        visualize_clusters(): This method visualizes the clusters of the best reduced embeddings in 2D space.
    """

    def visualize_clusters(self,
                        best_embeddings_df: pd.DataFrame,
                        path_to_save_cluster_map: str):
        """
        This method visualizes the clusters of the best reduced embeddings in 2D space.

        Args:
            best_embeddings_df (pd.DataFrame): A pandas DataFrame containing the best reduced embeddings and the labels of the clusters.
            path_to_save_cluster_map (str): A string containing the path to save the plot of the clusters in 2D space.
        """

        df = best_embeddings_df.drop('Pdf_page_name', axis=1)
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], color='Cluster', hover_data=['Cluster'])
        fig.update_layout(title='Clusters in 2D space', template='plotly_dark')
        fig_path = os.path.join(path_to_save_cluster_map, 'clusters_in_2D_space.png')
        fig.write_image(fig_path)
        #print(f'Dear User ! The plot has been saved in {path_to_save_cluster_map} with the name {name}.')
