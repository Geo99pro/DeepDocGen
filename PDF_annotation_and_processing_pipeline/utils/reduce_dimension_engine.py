import numpy as np
import plotly.express as px
from sklearn.manifold import TSNE
from Pdf_annotation_pipeline.utils.embeddings_manager_engine import EmbeddingsManagerEngine

#helpful link: https://medium.com/rafaeltardivo/python-entendendo-o-uso-de-args-e-kwargs-em-fun%C3%A7%C3%B5es-e-m%C3%A9todos-c8c2810e9dc8
#https://plotly.com/python/static-image-export/
class ReduceDimensionEngine:
    """
    This class is responsible for reducing the dimension of the data to 2D space by using t-SNE algorithm.
    By using this class, you can reduce the dimension of the data and visualize it in 2D space.
    User can use other dimension reduction algorithms by changing the algorithm in the constructor.

    Attributes:
        desired_perplexity_range (tuple): A tuple containing the range of perplexity to be evaluated.
        n_components (int): An integer containing the number of components to be reduced.
        embeddings_extracted (dict): A dictionary containing the embeddings extracted.
        t_SNE_init (str): A string containing the initialization method for t-SNE algorithm. check the documentation in https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html for more details.
        random_state (int): An integer containing the random state for t-SNE algorithm.
        path_to_save_div_vs_perp (str): A string containing the path to divergences vs perplexity plot.
        should_save_best_embeddings (bool): A boolean value to save the best reduced embeddings. We recommand to user to save the best reduced embeddings because reduce the dimension of the data is a time consuming process.
        kwargs: Additional keyword arguments. It can be the path to save the metadata for example.

    Methods:

        reduce_dimension_with_tSNE(): This method reduces the dimension of the data to 2D space and returns the best embeddings reduced. 
        Also this method can save the best reduced embeddings and the divergence of the t-SNE algorithm. 
        It can also save the plot of the perplexity vs Kullback-Leibler divergence.
        reduce_dimension_with_PCA(): To do
        reduce_dimension_with_LDA(): To do
        reduce_dimension_with_MDS(): To do
        reduce_dimension_with_Isomap(): To do
        reduce_dimension_with_UMAP(): To do


    """

    def __init__(self, desired_perplexity_range: tuple, n_components: int, embeddings_extracted: dict, t_SNE_init: str, random_state: int, path_to_save_div_vs_perp: str, should_save_best_embeddings: bool, **kwargs):
        self.desired_perplexity_range = desired_perplexity_range
        self.n_components = n_components
        self.embeddings_extracted = embeddings_extracted
        self.t_SNE_init = t_SNE_init
        self.random_state = random_state
        self.path_to_save_div_vs_perp = path_to_save_div_vs_perp
        self.should_save_best_embeddings = should_save_best_embeddings
        self.kwargs = kwargs

    def reduce_dimension_with_tSNE(self)-> np.ndarray:
        print(f'In reduce dimension process -> t-SNE algorithm.')

        if isinstance(self.embeddings_extracted, dict):
            embeddings_extracted = np.vstack(self.embeddings_extracted['embeddings_extracted'])
            self.embeddings_extracted = embeddings_extracted

        else:
            raise ValueError('The embeddings_extracted should be a dictionary containing the embeddings extracted. Check it out !')

        hold_meta_data = []
        divergence_list = []
        perplexity  = np.arange(*self.desired_perplexity_range)

        for per in perplexity:
            temporal_list = []
            model = TSNE(n_components=self.n_components, perplexity=per, init=self.t_SNE_init, random_state=self.random_state)
            reduced_embeddings = model.fit_transform(self.embeddings_extracted)
            divergence = model.kl_divergence_
            meta_data = {'perplexity': per, 'embeddings': reduced_embeddings, 'divergence': divergence}
            temporal_list.append(meta_data)
            divergence_list.append(divergence)
            hold_meta_data.append(temporal_list)

        fig = px.line(x=perplexity, y=divergence_list, markers=True)
        fig.update_layout(xaxis_title='Perplexity', yaxis_title='Kullback-Leibler divergence')
        fig.update_traces(line_color='black', line_width=1)
        fig.write_image(f'{self.path_to_save_div_vs_perp}perplexity_vs_divergence.png')

        if self.should_save_best_embeddings:
            best_embedding_reduced = hold_meta_data[np.argmin(divergence_list)][0]['embeddings']
            embedding_manager = EmbeddingsManagerEngine(path= f'{self.kwargs.get("path_to_save_best_embeddings")}best_embeddings_reduced', element = best_embedding_reduced)
            embedding_manager.save_embeddings()
            return best_embedding_reduced
            #embedding_manager = EmbeddingsManagerEngine(path= self.kwargs.get('path_to_save_metadata'), element = hold_meta_data) # decoment this line if you want to save the metadata
            #EmbeddingsManagerEngine(path= self.kwargs.get('path_to_save_divergence'), element = divergence_list).save_embeddings() # decoment this line if you want to save the divergence

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



