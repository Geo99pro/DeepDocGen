import os
import shutil
import numpy as np
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
from glob import glob
from sklearn.metrics.pairwise import cosine_similarity


class DataFrameEngine:
    """
    This class handles DataFrame creation and cluster analysis for embeddings.

    Methods:
        - create_dataframe: Creates a DataFrame with embeddings and cluster labels.
    """

    def create_dataframe(self,
                         best_reduced_embeddings: np.ndarray,
                         kmeans_labels: np.ndarray,
                         desired_columns_names: str,
                         embeddings_extracted: dict,
                         save_to_excel_format: bool,
                         **kwargs) -> pd.DataFrame:
        """
        This method is responsible for creating a DataFrame with embeddings and cluster labels.

        Args:
            - best_reduced_embeddings (np.ndarray): Reduced embeddings as a NumPy array.
            - kmeans_labels (np.ndarray): Cluster labels from K-means.
            - desired_columns_names (str): Base name for embedding columns.
            - embeddings_extracted (dict): Dictionary with extracted embedding names and values.
            - save_to_excel_format (bool): Whether to save the DataFrame in Excel format.
            - kwargs (dict): Additional arguments like the save path. 

        Returns:
            - embeddings_df (pd.DataFrame): DataFrame with embeddings and cluster labels.
        """
        embeddings_df = pd.DataFrame(best_reduced_embeddings, 
                                     columns=[desired_columns_names + str(i) for i in range(best_reduced_embeddings.shape[1])])
        embeddings_df['Pdf_page_name'] = embeddings_extracted['embeddings_names']
        embeddings_df['Cluster'] = kmeans_labels

        # Plot cluster distribution
        group_count = embeddings_df['Cluster'].value_counts().to_dict()
        sns.barplot(x=group_count.keys(),
                    y=group_count.values(),
                    hue=group_count.values(),
                    estimator="sum",
                    palette=sns.color_palette(None, len(group_count.keys())), legend= False)
        plt.grid(axis='both')
        plt.xlabel('Clusters')
        plt.ylabel('Counts')
        plt.title('Distribution of PDF pages by cluster')
        plt.savefig(f'{kwargs.get("path_to_save_dataframe")}distribution_of_PDF_pages_by_cluster.png')

        # Save DataFrame as Excel file
        if save_to_excel_format:
            output_path = os.path.join(kwargs.get("path_to_save_dataframe"), 'embeddings_dataframe.xlsx')
            embeddings_df.to_excel(output_path, index=False)
            print(f'Dear User ! The embeddings dataframe has been saved successfully on the excel format. Check it out at: {output_path}')
        return embeddings_df

    def test_cosine_similarity(self, 
                               embeddings_extracted,
                               kmeans_labels, 
                               meta_data_folder: dict,
                               **kwargs):
        """
        Analyzes cosine similarity within clusters and copies images to folders based on thresholds.

        Args:
            - embeddings_extracted (dict): Dictionary with extracted embeddings names and values.
            - kmeans_labels (np.ndarray): Cluster labels from K-means.
            - meta_data_folder (dict): Metadata for folders containing clustered images.
            - kwargs (dict): Additional arguments like the save path.

        Returns:
            None. However, it saves images to folders based on thresholds.
        """

        embedding_df = pd.DataFrame(embeddings_extracted)
        embedding_df.rename(columns={'embeddings_names': 'Pdf_page_name'}, inplace=True)
        embedding_df["Cluster"] = kmeans_labels
        
        for cluster_label in np.unique(kmeans_labels):
            #Filter the dataframe by cluster
            filtered_per_cluster = embedding_df[embedding_df['Cluster'] == cluster_label]
            pdf_names = filtered_per_cluster['Pdf_page_name'].values

            #Compute the cosine similarity between the embeddings of the same cluster
            cos_sim = cosine_similarity(np.vstack(filtered_per_cluster["embeddings_extracted"].values))
            cos_sim_df = pd.DataFrame(cos_sim, index=pdf_names, columns=pdf_names)

            # Compute statistics
            # 1. Compute the mean similarity
            # 2. Compute the first and third quantile 
            # 3. Compute the IQR
            # 4. Compute the lower and upper quantile
            mean_similarity = cos_sim_df.mean(axis=1)
            first_quantile = mean_similarity.quantile(0.25)
            third_quantile = mean_similarity.quantile(0.75)
            iqr = third_quantile - first_quantile
            lower_quantile, upper_quantile= first_quantile - 1.5*iqr, third_quantile + 1.5*iqr

            #Plot the distribution of the PDF pages by cluster
            overall_mean = mean_similarity.mean()
            self.plot_distribution_of_PDF_pages_by_cluster(mean_similarity,
                                                           overall_mean,
                                                           cluster_label)

            #Filter pages by thresholds
            page_below_threshold = mean_similarity[mean_similarity < lower_quantile]
            page_above_threshold = mean_similarity[mean_similarity > upper_quantile]
            page_between_threshold = mean_similarity[(mean_similarity > first_quantile) & (mean_similarity < third_quantile)]
            
            #Save the images that are above and below the threshold
            save_path = kwargs.get("path_to_save_dataframe")
            self.setup_folder(os.path.join(save_path, f'images_below_threshold_group_{cluster_label}'))
            self.setup_folder(os.path.join(save_path, f'image_upper_threshold_group_{cluster_label}'))
            self.setup_folder(os.path.join(save_path, f'image_between_threshold_group_{cluster_label}'))

            for meta in meta_data_folder:
                if meta['cluster'] == cluster_label:
                    each_images_path = {os.path.basename(path).split('.')[0]: path for path in glob(os.path.join(meta['folder_path'], '*.png'))}
                    
                    self.copy_image(page_below_threshold, os.path.join(save_path, f'images_below_threshold_group_{cluster_label}'), each_images_path)
                    self.copy_image(page_above_threshold, os.path.join(save_path, f'image_upper_threshold_group_{cluster_label}'), each_images_path)
                    self.copy_image(page_between_threshold, os.path.join(save_path, f'image_between_threshold_group_{cluster_label}'), each_images_path)

    def plot_distribution_of_PDF_pages_by_cluster(self,
                                                  mean_similarity: pd.Series, 
                                                  overall_mean: float,
                                                  cluster_label: int,
                                                  **kwargs):
        """
        This method is responsible for plotting the distribution of the PDF pages by cluster.

        Args:
            mean_similarity (pd.Series): A pandas Series containing the mean similarity between the embeddings of the same cluster.
            overall_mean (float): A float number containing the overall mean similarity between the embeddings of the same cluster.

        Returns:
            None. However, it saves the plot on the path provided by the user.
        """

        #Histplot
        plt.figure(figsize=(15, 8))
        sns.histplot(mean_similarity, kde=True, color='skyblue')
        plt.axvline(x=overall_mean, color='r', linestyle='--', label='Overall mean')
        plt.xlabel('Mean cosinus similarity')
        plt.ylabel('Counts')
        plt.title(f'Cluster {cluster_label} - Cosine Similarity Distribution')
        plt.legend()
        plt.grid(axis='both')
        plt.savefig(os.path.join(kwargs.get("path_to_save_dataframe"), f'cluster_{cluster_label}_similarity_distribution.png'))
        plt.close()

    def setup_folder(self, folder_path: str):
        """
        Prepares a folder by recreating it if it already exists.
        """
        if os.path.exists(folder_path):
            print(f'Dear User, The folder {folder_path} already exists. I will delete it and create a new one.')
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
    
    def copy_image(self, filtered_data: pd.Series, folder_path: str, each_images_path: dict):
        """
        Copies filtered images to the specified folder.

        Args:
            filtered_data (pd.Series): Filtered image names based on thresholds.
            folder_path (str): Path to the destination folder.
            image_paths (dict): Dictionary mapping image names to their paths.
        """
        for image_name in filtered_data.index:
            if image_name in each_images_path:
                shutil.copy(each_images_path[image_name], folder_path)