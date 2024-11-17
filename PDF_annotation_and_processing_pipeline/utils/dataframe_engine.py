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

    Attributes:

        best_reduced_embeddings (np.ndarray): A numpy array containing the best reduced embeddings.
        kmeans_prediction (np.ndarray): A numpy array containing the labels of the clusters.
        desired_columns_names str: A string containing the desired columns names.
        embeddings_names (list): A list containing the names of the embeddings.

    Methods:

        create_dataframe(): This method creates a pandas DataFrame of the best reduced embeddings with the labels of the clusters.
    """

    def __init__(self, best_reduced_embeddings: np.ndarray, kmeans_prediction: np.ndarray, desired_columns_names: str, embeddings_extracted: dict, save_to_excel_format: bool, **kwargs):
        self.best_reduced_embeddings = best_reduced_embeddings
        self.kmeans_labels = kmeans_prediction
        self.desired_columns_names = desired_columns_names
        self.embeddings_extracted = embeddings_extracted
        self.save_to_excel_format = save_to_excel_format
        self.kwargs = kwargs


    def create_dataframe(self):
        embeddings_df = pd.DataFrame(self.best_reduced_embeddings, columns=[self.desired_columns_names + str(i) for i in range(self.best_reduced_embeddings.shape[1])])
        embeddings_df['Pdf_page_name'] = self.embeddings_extracted['embeddings_names']
        embeddings_df['Cluster'] = self.kmeans_labels
        group_count = embeddings_df['Cluster'].value_counts().to_dict()
        sns.barplot(x=group_count.keys(), y=group_count.values(), hue=group_count.values(), estimator="sum", palette=sns.color_palette(None, len(group_count.keys())), legend= False)
        plt.grid(axis='both')
        plt.xlabel('Clusters')
        plt.ylabel('Counts')
        plt.title('Distribution of PDF pages by cluster')
        plt.savefig(f'{self.kwargs.get("path_to_save_dataframe")}distribution_of_PDF_pages_by_cluster.png')
        plt.close()

        if self.save_to_excel_format:
            embeddings_df.to_excel(f'{self.kwargs.get("path_to_save_dataframe")}embeddings_dataframe.xlsx', index=False)
            print('Dear User ! The embeddings dataframe has been saved successfully on the excel format. Check it out on the path you provided.')
        return embeddings_df
    
    

    def test_cosine_similarity(self, meta_data_folder: dict):
        """
        This method is responsible for testing the cosine similarity between the embeddings of the same cluster to help the user to select the documents images for annotation.

        Args:
            meta_data_folder (dict): A dictionary containing the metadata of the folders. It comes from DetermineEachPdfGroup class.
            Example: [{'cluster': integer, 'folder_path': string}]
        """

        embedding_df = pd.DataFrame(self.embeddings_extracted)
        embedding_df.rename(columns={'embeddings_names': 'Pdf_page_name'}, inplace=True)
        embedding_df["Cluster"] = self.kmeans_labels
        
        for cluster_label in np.unique(self.kmeans_labels):

            #Filter the dataframe by cluster
            filtered_per_cluster = embedding_df[embedding_df['Cluster'] == cluster_label]
            corresponding_pdf_img_names = filtered_per_cluster['Pdf_page_name'].values

            #Compute the cosine similarity between the embeddings of the same cluster
            compute_cos_sim = cosine_similarity(np.vstack(filtered_per_cluster["embeddings_extracted"].values))
            corresponding_dataframe = pd.DataFrame(compute_cos_sim, index=corresponding_pdf_img_names, columns=corresponding_pdf_img_names)

            #Compute general mean and std
            mean_similarity = corresponding_dataframe.mean(axis=1)
            std_similarity = corresponding_dataframe.std(axis=1)

            #Compute the threshold based on the general mean and std
            overall_mean = mean_similarity.mean()
            overall_std = std_similarity.mean()
            self.plot_distribution_of_PDF_pages_by_cluster(mean_similarity, overall_mean, cluster_label)

            #Calculate the first and third quantile
            first_quantile = mean_similarity.quantile(0.25)
            third_quantile = mean_similarity.quantile(0.75)

            #Get the image between the first and third quantile
            

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
            annotate_path_below_thr = os.path.join(self.kwargs.get("path_to_save_dataframe"), f'images_below_threshold_group_{cluster_label}')
            annotate_path_upper_thr = os.path.join(self.kwargs.get("path_to_save_dataframe"), f'image_upper_threshold_group_{cluster_label}')
            annotate_path_between_thr = os.path.join(self.kwargs.get("path_to_save_dataframe"), f'image_between_threshold_group_{cluster_label}')

            self.setup_folder(annotate_path_below_thr)
            self.setup_folder(annotate_path_upper_thr)
            self.setup_folder(annotate_path_between_thr)

            for meta in meta_data_folder:
                if meta['cluster'] == cluster_label:
                    each_images_path = {os.path.basename(path).split('.')[0]: path for path in glob(os.path.join(meta['folder_path'], '*.png'))}
                    
                    self.copy_image(page_below_threshold, annotate_path_below_thr, each_images_path)
                    self.copy_image(page_above_threshold, annotate_path_upper_thr, each_images_path)
                    self.copy_image(page_between_threshold, annotate_path_between_thr, each_images_path)

                    # for image_name in page_below_threshold.index:
                    #     if image_name in each_images_path:
                    #         shutil.copy(each_images_path[image_name], annotate_path_below_thr)

                    # for image_name in page_above_threshold.index:
                    #     if image_name in each_images_path:
                    #         shutil.copy(each_images_path[image_name], annotate_path_upper_thr)
                    
                    # for image_name in page_between_threshold.index:
                    #     if image_name in each_images_path:
                    #         shutil.copy(each_images_path[image_name], annotate_path_between_thr)

    def plot_distribution_of_PDF_pages_by_cluster(self, mean_similarity: pd.Series, overall_mean: float, cluster_label: int):
        """
        This method is responsible for plotting the distribution of the PDF pages by cluster.

        Args:
            mean_similarity (pd.Series): A pandas Series containing the mean similarity between the embeddings of the same cluster.
            std_similarity (pd.Series): A pandas Series containing the standard deviation of the similarity between the embeddings of the same cluster.
            overall_mean (float): A float number containing the overall mean similarity between the embeddings of the same cluster.

        Returns:
            None. However, it saves the plot on the path provided by the user.
        """

        #Plot the mean and std with plt.bar
        # plt.figure(figsize=(20, 20))
        # plt.bar(mean_similarity.index, mean_similarity, yerr=std_similarity, capsize=5, color='skyblue', edgecolor='black')
        # plt.axhline(y=overall_mean, color='r', linestyle='--', label='Overall mean')
        # plt.xlabel('Columns')
        # plt.ylabel('Value')
        # plt.title(f'Average and standard deviation per column for cluster {cluster_label}') 
        # plt.xticks(rotation=90)
        # plt.legend()
        # plt.grid(axis='x')
        # plt.savefig(f'{self.kwargs.get("path_to_save_dataframe")}Average_and_standard_deviation_per_column_for_cluster_{cluster_label}.png')
        # plt.close()

        #boxplot
        plt.figure(figsize=(15, 8))
        sns.boxplot(data=mean_similarity, color='skyblue')
        plt.axhline(y=overall_mean, color='r', linestyle='--', label='Overall mean')
        plt.xlabel('Columns')
        plt.ylabel('Value')
        plt.title(f'Boxplot of the average per column for cluster {cluster_label}')
        plt.xticks(rotation=90)
        plt.legend()
        plt.grid(axis='x')
        plt.savefig(f'{self.kwargs.get("path_to_save_dataframe")}Boxplot_of_the_average_per_column_for_cluster_{cluster_label}.png')
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
            print(f'Dear User, The folder {folder_path} already exists. I will delete it and create a new one.')
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

# def test_cosine_similarity(self, meta_data_folder: dict):
    #     """
    #     This method is responsible for testing the cosine similarity between the embeddings of the same cluster to help the user to select the documents images for annotation.

    #     Args:
    #         embeddings_df (pd.DataFrame): A pandas DataFrame containing the embeddings, output of the embeddings extractor which is the choosed one by the user.
    #         Example: Swin Transformer, Resnet, etc.

    #     Returns:
    #         mean_similarity (float): A float number containing the mean similarity between the embeddings of the same cluster
    #     """

    #     embedding_df = pd.DataFrame(self.embeddings_extracted)
    #     embedding_df.rename(columns={'embeddings_names': 'Pdf_page_name'}, inplace=True)
    #     embedding_df["Cluster"] = self.kmeans_labels
        

    #     page_image_name_above_threshold = set()
    #     page_image_name_under_threshold = set()
    #     for cluster_label in np.unique(self.kmeans_labels):
    #         #Filter the dataframe by cluster
    #         filtered_per_cluster = embedding_df[embedding_df['Cluster'] == cluster_label]
    #         corresponding_pdf_img_names = filtered_per_cluster['Pdf_page_name'].values

    #         #Compute the cosine similarity between the embeddings of the same cluster
    #         compute_cos_sim = cosine_similarity(np.vstack(filtered_per_cluster["embeddings_extracted"].values))
    #         corresponding_dataframe = pd.DataFrame(compute_cos_sim, index=corresponding_pdf_img_names, columns=corresponding_pdf_img_names)

    #         #As a symetric dataframe, the comparison between page 1 and page 2 is equal to comparison between page 2 and page 1.
    #         triangular_similarity = corresponding_dataframe.where(np.tril(np.ones(corresponding_dataframe.shape), k=-1).astype(bool)).stack()
            
    #         #Compute the threshold
    #         mean_similarity = triangular_similarity.mean()
    #         std_similarity = triangular_similarity.std()

    #         #Define the thresholds (upper and lower)
    #         threshold_lower, threshold_upper = mean_similarity - std_similarity, mean_similarity + std_similarity

    #         #Filter the pairs of images that are above and below the threshold
    #         page_above_threshold = triangular_similarity[triangular_similarity > threshold_upper]
    #         page_under_threshold = triangular_similarity[triangular_similarity < threshold_lower]

    #         #Save the pairs of images that are above and below the threshold
    #         page_image_name_above_threshold.update(page_above_threshold.index.get_level_values(0))
    #         page_image_name_above_threshold.update(page_above_threshold.index.get_level_values(1))
    #         page_image_name_under_threshold.update(page_under_threshold.index.get_level_values(0))
    #         page_image_name_under_threshold.update(page_under_threshold.index.get_level_values(1))

    #         # dico = {'Cluster': integer,
    #         #         'Mean_similarity': mean_similarity,
    #         #         'Std_similarity': std_similarity,
    #         #         'Threshold_lower': threshold_lower,
    #         #         'Threshold_upper': threshold_upper,
    #         #         'Page_image_name_above_threshold': page_image_name_above_threshold,
    #         #         'page_image_name_under_threshold': page_image_name_under_threshold}
    #         # meta_data.append(dico)
    #         image_to_annotate_path = os.path.join(self.kwargs.get("path_to_save_dataframe"), f'Image_to_annotate_for_group_{cluster_label}')
    #         if os.path.exists(image_to_annotate_path):
    #             print(f'Dear User, The folder {image_to_annotate_path} already exists. I will delete it and create a new one.')
    #             shutil.rmtree(image_to_annotate_path)
    #         os.makedirs(image_to_annotate_path)

    #         for meta in meta_data_folder:
    #             if meta['cluster'] == cluster_label:
    #                 each_images_path = glob(os.path.join(meta['folder_path'], '*.png'))
    #                 for image_name in page_image_name_under_threshold:
    #                     for image_path in each_images_path:
    #                         if image_name == os.path.basename(image_path).split('.')[0]:
    #                             shutil.copy(image_path, image_to_annotate_path)






    #                 #each_images_name = [os.path.basename(image_path).split('.')[0] for image_path in each_images_path]
    #                 #print(f'Each images name: {each_images_name}')

    #     #return meta_data