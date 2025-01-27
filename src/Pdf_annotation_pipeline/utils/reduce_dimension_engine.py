import os
import numpy as np
import plotly.express as px
from sklearn.manifold import TSNE
from src.Pdf_annotation_pipeline.utils.embeddings_manager_engine import EmbeddingsManagerEngine

#helpful link: https://medium.com/rafaeltardivo/python-entendendo-o-uso-de-args-e-kwargs-em-fun%C3%A7%C3%B5es-e-m%C3%A9todos-c8c2810e9dc8
#https://plotly.com/python/static-image-export/
class ReduceDimensionEngine:
    """
    This class is responsible for reducing the dimension of the data to 2D space by using t-SNE algorithm.
    By using this class, you can reduce the dimension of the data and visualize it in 2D space.
    User can use other dimension reduction algorithms by changing the algorithm in the constructor.

    Methods:

        - reduce_dimension_with_tSNE: This method reduces the dimension of the data to 2D space with the t-SNE algorithm and returns the best embeddings reduced. 
        - reduce_dimension_with_PCA(): To do
        - reduce_dimension_with_LDA(): To do
        - reduce_dimension_with_MDS(): To do
        - reduce_dimension_with_Isomap(): To do
        - reduce_dimension_with_UMAP(): To do
    """

    def reduce_dimension_with_tSNE(self,
                                   desired_perplexity_range: tuple,
                                   n_components: int,
                                   embeddings_extracted: dict,
                                   t_SNE_init: str,
                                   random_state: int,
                                   should_save_best_embeddings: bool,
                                   **kwargs)-> np.ndarray:
        """
        This method reduces the dimension of the data to 2D space with the t-SNE algorithm and returns the best embeddings reduced.
        We recomment user to save the best embeddings reduced to use, because the t-SNE algorithm is a stochastic algorithm and the results may vary and also the t-SNE algorithm is computationally expensive.

        Args:
            - desired_perplexity_range (tuple): is the range of the desired perplexity to use for the t-SNE algorithm.
            - n_components (int): is the number of components to reduce the dimension.
            - embeddings_extracted (dict): is the dictionary containing the embeddings extracted.
            - t_SNE_init (str): is the initialization of the t-SNE algorithm.
            - random_state (int): is the random state to use for the t-SNE algorithm.
            - should_save_best_embeddings (bool): is the boolean value to save the best embeddings reduced.
            - kwargs (dict): is the dictionary containing the path to save the best embeddings and the path to save the divergence vs perplexity figure.

        Returns:
            - best_embedding_reduced (numpy.ndarray): is the best embeddings reduced.
        """

        if isinstance(embeddings_extracted, dict):
            embeddings_extracted = np.vstack(embeddings_extracted['embeddings_extracted'])
        else:
            raise ValueError('The embeddings_extracted should be a dictionary containing the embeddings extracted. Check it out !')

        hold_meta_data = []
        divergence_list = []
        perplexity  = np.arange(*desired_perplexity_range)

        for per in perplexity:
            temporal_list = []
            model = TSNE(n_components=n_components, perplexity=per, init=t_SNE_init, random_state=random_state)
            reduced_embeddings = model.fit_transform(embeddings_extracted)
            divergence = model.kl_divergence_
            meta_data = {'perplexity': per, 'embeddings': reduced_embeddings, 'divergence': divergence}
            temporal_list.append(meta_data)
            divergence_list.append(divergence)
            hold_meta_data.append(temporal_list)

        fig = px.line(x=perplexity, y=divergence_list, markers=True)
        fig.update_layout(xaxis_title='Perplexity', yaxis_title='Kullback-Leibler divergence')
        fig.update_traces(line_color='black', line_width=1)
        figure_path = os.path.join(kwargs.get('path_to_save_div_vs_perp'), 'perplexity_vs_divergence.png')
        fig.write_image(figure_path)

        if should_save_best_embeddings:
            best_embedding_reduced = hold_meta_data[np.argmin(divergence_list)][0]['embeddings']
            embeddings_path = os.path.join(kwargs.get('path_to_save_best_embeddings'), 'best_embeddings_reduced')
            embedding_manager = EmbeddingsManagerEngine()
            embedding_manager.save_embeddings(embeddings_path, best_embedding_reduced)
            return best_embedding_reduced

        best_embedding_reduced = hold_meta_data[np.argmin(divergence_list)][0]['embeddings']

        return best_embedding_reduced

    def reduce_dimension_with_PCA(self):
        #To do
        pass

    def reduce_dimension_with_LDA(self):
        #To do
        pass

    def reduce_dimension_with_MDS(self):
        #To do
        pass

    def reduce_dimension_with_Isomap(self):
        #To do
        pass

    def reduce_dimension_with_UMAP(self):
        #To do
        pass



