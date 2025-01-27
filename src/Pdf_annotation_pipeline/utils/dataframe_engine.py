import os
import shutil
import numpy as np
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from sklearn.metrics.pairwise import cosine_similarity

class DataFrameEngine:
    """
    This class is responsible for handling the dataframes.
    By using this class, you can handle the dataframes.

    Methods:

        create_dataframe: This method creates a pandas DataFrame of the best reduced embeddings with the labels of the clusters.
        cosine_similarity_check: This method is responsible for checking the cosine similarity between the embeddings of the same cluster to help the user to select the documents images for annotation.
        plot_distribution_of_PDF_pages_by_cluster: This method is responsible for plotting the distribution of the PDF pages by cluster.
        setup_folder: This method is responsible for setting up the folder.
        copy_image: This method is responsible for copying the images to the folder based on the corresponding threshold.
    """

    def create_dataframe(self,
                         best_reduced_embeddings: np.ndarray,
                         kmeans_prediction: np.ndarray, 
                         desired_columns_names: str,
                         embeddings_extracted: dict,
                         save_to_excel_format: bool,
                         **kwargs):
        """
        This method creates a pandas DataFrame of the best reduced embeddings with the labels of the clusters.
        
        Args:
            - best_reduced_embeddings (np.ndarray): A numpy array containing the best reduced embeddings.
            - kmeans_prediction (np.ndarray): A numpy array containing the labels of the clusters.
            - desired_columns_names (str): A string containing the desired columns names.
            - embeddings_extracted (dict): A dictionary containing the embeddings extracted.
            - save_to_excel_format (bool): A boolean indicating whether to save the dataframe to the excel format.
            - kwargs (dict): A dictionary containing the path to save the dataframe. Like the path_to_save_dataframe.
            
        Returns:
            
            - embeddings_df (pd.DataFrame): A pandas DataFrame containing the best reduced embeddings with the labels of the clusters.
        """
        
        embeddings_df = pd.DataFrame(best_reduced_embeddings, columns=[desired_columns_names + str(i) for i in range(best_reduced_embeddings.shape[1])])
        embeddings_df['Pdf_page_name'] = embeddings_extracted['embeddings_names']
        embeddings_df['Cluster'] = kmeans_prediction
        group_count = embeddings_df['Cluster'].value_counts().to_dict()
        sns.barplot(x=group_count.keys(), y=group_count.values(), hue=group_count.values(), estimator="sum", palette=sns.color_palette(None, len(group_count.keys())), legend= False)
        plt.grid(axis='both')
        plt.xlabel('Clusters')
        plt.ylabel('Counts')
        plt.title('PDF pages distribution by cluster.')
        figure_path = os.path.join(kwargs.get('path_to_save_dataframe'), 'distribution_of_PDF_pages_by_cluster.png')
        plt.savefig(figure_path)
        plt.close()

        if save_to_excel_format:
            file_path = os.path.join(kwargs.get('path_to_save_dataframe'), 'embeddings_dataframe.xlsx')
            embeddings_df.to_excel(file_path, index=False)
        return embeddings_df
    
    def cosine_similarity_check(self,
                               embeddings_extracted: dict,
                               Kmeans_prediction: np.ndarray,
                               meta_data_folder: dict,
                               path_to_save_folders: str):
        """
        This method is responsible for testing the cosine similarity between the embeddings of the same cluster to help the user to select the documents images for annotation.

        Args:
            - embeddings_extracted (dict): A dictionary containing the embeddings extracted.
            - Kmeans_prediction (np.ndarray): A numpy array containing the labels of the clusters.
            - meta_data_folder (dict): A dictionary containing the metadata of the folders. It comes from DetermineEachPdfGroup class.
                - Example: [{'cluster': integer, 'folder_path': string}]
            - path_to_save_folders (str): A string containing the path to save the folders.
        """

        embedding_df = pd.DataFrame(embeddings_extracted)
        embedding_df.rename(columns={'embeddings_names': 'Pdf_page_name'}, inplace=True)
        embedding_df["Cluster"] = Kmeans_prediction
        
        for cluster_label in np.unique(Kmeans_prediction):

            #Filter the dataframe by cluster
            filtered_per_cluster = embedding_df[embedding_df['Cluster'] == cluster_label]
            corresponding_pdf_img_names = filtered_per_cluster['Pdf_page_name'].values

            #Compute the cosine similarity between the embeddings of the same cluster
            compute_cos_sim = cosine_similarity(np.vstack(filtered_per_cluster["embeddings_extracted"].values))
            corresponding_dataframe = pd.DataFrame(compute_cos_sim, index=corresponding_pdf_img_names, columns=corresponding_pdf_img_names)

            #Compute general mean and std
            mean_similarity = corresponding_dataframe.mean(axis=1)

            #Compute the threshold based on the general mean
            overall_mean = mean_similarity.mean()
            self.plot_distribution_of_PDF_pages_by_cluster(mean_similarity, overall_mean, cluster_label, path_to_save_folders)

            #Calculate the first and third quantile
            first_quantile = mean_similarity.quantile(0.25)
            third_quantile = mean_similarity.quantile(0.75)

            #compute the IQR
            iqr = third_quantile - first_quantile

            #Compute the lower and upper quantile
            lower_quantile = first_quantile - 1.5*iqr
            upper_quantile = third_quantile + 1.5*iqr

            #Filter the pairs of images that are above and below the threshold and remove nan values
            page_below_threshold = mean_similarity[mean_similarity < lower_quantile]
            page_above_threshold = mean_similarity[mean_similarity > upper_quantile]
            page_between_threshold = mean_similarity[(mean_similarity > first_quantile) & (mean_similarity < third_quantile)]
            
            #Save the images that are above and below the threshold
            annotate_path_below_thr = os.path.join(path_to_save_folders, f'images_below_threshold_group_{cluster_label}')
            annotate_path_upper_thr = os.path.join(path_to_save_folders, f'image_upper_threshold_group_{cluster_label}')
            annotate_path_between_thr = os.path.join(path_to_save_folders, f'image_between_threshold_group_{cluster_label}')

            self.setup_folder(annotate_path_below_thr)
            self.setup_folder(annotate_path_upper_thr)
            self.setup_folder(annotate_path_between_thr)

            for meta in meta_data_folder:
                if meta['cluster'] == cluster_label:
                    each_images_path = {os.path.basename(path).split('.')[0]: path for path in glob(os.path.join(meta['folder_path'], '*.png'))}
                    
                    self.copy_image(page_below_threshold, annotate_path_below_thr, each_images_path)
                    self.copy_image(page_above_threshold, annotate_path_upper_thr, each_images_path)
                    self.copy_image(page_between_threshold, annotate_path_between_thr, each_images_path)

    def plot_distribution_of_PDF_pages_by_cluster(self, 
                                                  mean_similarity: pd.Series,
                                                  overall_mean: float,
                                                  cluster_label: int,
                                                  path_to_save_plot: str):
        """
        This method is responsible for plotting the distribution of the PDF pages by cluster.

        Args:
            - mean_similarity (pd.Series): A pandas Series containing the mean similarity between the embeddings of the same cluster.
            - std_similarity (pd.Series): A pandas Series containing the standard deviation of the similarity between the embeddings of the same cluster.
            - overall_mean (float): A float number containing the overall mean similarity between the embeddings of the same cluster.
            - cluster_label (int): An integer containing the label of the cluster.
            - path_to_save_plot (str): A string containing the path to save the plot.

        Returns:
            - None. However, it saves the plot on the path provided by the user.
        """

        plt.figure(figsize=(15, 8))
        sns.histplot(mean_similarity, kde=True, color='skyblue')
        plt.axvline(x=overall_mean, color='r', linestyle='--', label='Overall mean')
        plt.xlabel('Mean cosine similarity')
        plt.ylabel('Total number of PDF pages.')
        plt.title(f'Distribution of the average per column for cluster {cluster_label}')
        plt.xticks(rotation=90)
        plt.legend()
        plt.grid(axis='both')
        figure_path = os.path.join(path_to_save_plot, f'Distribution_of_the_average_per_column_for_cluster_{cluster_label}.png')
        plt.savefig(figure_path)
        plt.close()

    def setup_folder(self, folder_path: str):
        """
        This method is responsible for setting up the folder.

        Args:
            folder_path (str): A string containing the path of the folder.

        Returns:
            None. However, it creates the folder if it does not exist.
        """

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
    
    def copy_image(self, filtered_per_threshold: pd.Series, folder_path: str, each_images_path: dict):
        """
        This method is responsible for copying the images to the folder based on the corresponding threshold.

        Args:
            filtered_per_threshold (pd.Series): A pandas Series containing the filtered images.
            folder_path (str): A string containing the path of the corresponding folder.

        Returns:
            None. However, it copies the images to the folder.
        """
        for image_name in filtered_per_threshold.index:
            if image_name in each_images_path:
                shutil.copy(each_images_path[image_name], folder_path)