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

    def __init__(self, best_embeddings_df: pd.DataFrame, path_to_save_cluster_map: str):
        self.best_embeddings_df = best_embeddings_df
        self.path_to_save_cluster_map = path_to_save_cluster_map

    def visualize_clusters(self):
        name = 'clusters_in_2D_space'
        df = self.best_embeddings_df.drop('Pdf_page_name', axis=1)
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], color='Cluster', hover_data=['Cluster'])
        fig.update_layout(title='Clusters in 2D space', template='plotly_dark')
        fig.write_image(f'{self.path_to_save_cluster_map}{name}.png')
        print(f'Dear User ! The plot has been saved in {self.path_to_save_cluster_map} with the name {name}.')
