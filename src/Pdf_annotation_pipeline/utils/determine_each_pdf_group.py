import os
import shutil
import pandas as pd
from glob import glob
import warnings

class DetermineEachPdfGroup:

    """
    This class is used to determine the group of each pdf file and fit them into a folder.
    By using the pdf file name, the group of the pdf file is determined.

    Methods:
    
        - determine_each_pdf_group: This function determines the group of each pdf file.
        - find_pdf_per_group_and_fit_folder: This function finds the pdfs per group and fit them into a folder.
        - fill_folder_with_images: This function fills the folder with the images of the pdfs respective to their group.
    """

    def determine_each_pdf_group(self,
                                dataframe: pd.DataFrame,
                                pdf_metadata: dict) -> list[dict]:
        """
        This method determines the group of each pdf file (Entire pdf file in this case).

        Args:
            - pdf_folder_path (str): is the path to the folder containing the pdfs.
            - dataframe (pd.DataFrame): is the dataframe containing the pdf file name and the cluster of the pdf file.
            - pdf_metadata (dict): is the metadata of the pdf files. Such as the pdf file name, the number of pages in the pdf file.
            - best_cluster (int): is the best cluster number.
            - path_to_save_pdf_per_group (str): is the path to save the pdfs per group.
            - **kwargs: is the dictionary containing the image path list.
        
        Returns:
            pdf_group_meta (list): is the list of dictionaries, which contains the pdf name, total pages, most common group, and pdf group.
        """
        warnings.warm("This usage is deprecated use the cosine_similarity_check function instead.")
        pdf_group_meta = []
        for metadata in pdf_metadata:
            pdf_name = metadata['pdf_name'] # come without ".pdf"
            total_pages = metadata['total_pages']
            filtered_df_by_name = dataframe[dataframe['Pdf_page_name'].str.contains(pdf_name, regex=False)]
            most_common_group  = filtered_df_by_name['Cluster'].value_counts().idxmax()

            meta_per_pdf = {'Original_pdf_name': pdf_name,
                            'Total_pages': total_pages,
                            'Most_common_group': most_common_group, 
                            'Pdf_group': most_common_group}

            pdf_group_meta.append(meta_per_pdf)

        return pdf_group_meta

    def find_pdf_per_group_and_fit_folder(self, 
                                        best_cluster: int,
                                        pdf_folder_path: str,
                                        path_to_save_pdf_per_group: str,
                                        pdf_group_meta: list[dict])-> None:
        """
        This method finds the pdfs per group and fit them into a folder.

        Args:
            - best_cluster (int): is the best cluster number.
            - pdf_folder_path (str): is the path to the folder containing the pdfs.
            - path_to_save_pdf_per_group (str): is the path to save the pdfs per group.
            - pdf_group_meta (list): is the list of dictionaries, which contains the pdf name, total pages, most common group, and pdf group.

        Returns:
            - None. However, it creates a folder for each group and copies the pdfs into the folder.
        """
        group_created_meta = []
        for integer in range(best_cluster):
            group_path = os.path.join(path_to_save_pdf_per_group, f'Pdfs_Of_Group_{integer}')

            if os.path.exists(group_path):
                shutil.rmtree(group_path)
            os.makedirs(group_path)
            group_created_meta.append({'Group': integer, 'Folder_path': group_path})

        list_of_pdf_path = glob(os.path.join(pdf_folder_path, '*.pdf'))

        for pdf_path in pdf_group_meta:
            pdf_group = pdf_path['Pdf_group']
            pdf_name = pdf_path['Original_pdf_name']

            for pdf_path in list_of_pdf_path:
                if pdf_name in os.path.basename(pdf_path).split('.')[0]:
                    for meta in group_created_meta:
                        if pdf_group == meta['Group']:
                            shutil.copy(pdf_path, meta['Folder_path'])
                            print(f'{pdf_name} is copied to {meta["Folder_path"]}')
                            break

    def fill_folder_with_images(self,
                                best_cluster: int,
                                path_to_save_pdf_per_group: str,
                                dataframe: pd.DataFrame,
                                **kwargs) -> list[dict]:
        """
        This method fills the folder with the images of the pdfs respective to their group.

        Args:
            - best_cluster (int): is the best cluster number.
            - path_to_save_pdf_per_group (str): is the path to save the pdfs per group.
            - dataframe (pd.DataFrame): is the dataframe containing the pdf file name and the cluster of the pdf file.
            - **kwargs: is the dictionary containing the image path list. Like image_path_list.

        Returns:
            - meta_data_folder (list): is the list of dictionaries, which contains the cluster and the folder path.
        """

        meta_data_folder = []
        for integer in range(best_cluster):
            folder_group_path = os.path.join(path_to_save_pdf_per_group, f'pdf_image_of_group_{integer}')
            dico = {'cluster': integer, 'folder_path': folder_group_path}
            meta_data_folder.append(dico)

            if os.path.exists(folder_group_path):
                shutil.rmtree(folder_group_path)
            os.makedirs(folder_group_path)

            dataframe_fltred=dataframe[dataframe['Cluster'] == integer] #filtre dataframe to get image name cluster
            for image_path in kwargs.get("image_path_list"):
                pdf_image_name = os.path.basename(image_path).split('.')[0]
                if pdf_image_name in dataframe_fltred['Pdf_page_name'].values: 
                    shutil.copy(image_path, folder_group_path)

        return meta_data_folder