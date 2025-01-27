import os
import h5py
import json
import shutil
import numpy as np
from glob import glob
from collections import defaultdict
from sklearn.model_selection import train_test_split



class AnnotationExtractor:
    """
    This class is used to extract annotations from the PubLayNet dataset or custom dataset in the same format.
    By using this class, users can extract annotations from the PubLayNet dataset or custom dataset in the same format and save them in a folder
    """

    def __init__(self, path_data_on_publyanet_format: str, path_to_save: str) -> None:
        """
        The constructor of the ExtractAnnotationEngine class.

        Args:
            - path_data_on_publyanet_format (str): The path to the annotation file of the PubLayNet dataset or custom dataset in the same format.
            - path_to_save (str): The path to save the extracted annotations.

        Returns:
            - None.
        """

        self.path_data_on_publyanet_format = path_data_on_publyanet_format
        self.path_to_save = path_to_save

    def extract_each_annotation(self, desired_folder_name: str) -> None:
        """
        This function processes the annotations in the PubLayNet format.
        It extracts the corresponding annotation of each image from the PubLayNet JSON file or custom dataset in the same format and saves them in a folder.
        Note that the PubLayNet JSON can represent either the train, val, or test dataset of PubLayNet or a custom dataset in the same format.
        
        Args:
            - desired_folder_name (str): The name of the folder to save the extracted annotations.
        Returns:
            - None. However, it saves annotations of each image in a folder named 'annotation_extracted'.
        """

        new_folder = os.path.join(self.path_to_save, desired_folder_name)
        if os.path.exists(new_folder):
            shutil.rmtree(new_folder)
        os.makedirs(new_folder)

        with open(self.path_data_on_publyanet_format, "r") as file:
            data = json.load(file)

        image_metas = data.get('images', [])
        annotations_metas = data.get('annotations', [])
        categories_metas = data.get('categories', [])

        annotations_by_image_id = defaultdict(list)
        for annotation in annotations_metas:
            annotations_by_image_id[annotation['image_id']].append(annotation)

        previous_image_id = None

        for each_image_meta in image_metas:
            current_image_id = each_image_meta['id']
            file_processed_name = '.'.join(each_image_meta['file_name'].split('.')[:-1])

            if previous_image_id is not None and current_image_id == previous_image_id:
                raise Exception(f'Dear user, the image id {current_image_id} is duplicated. Please check the consistency of the data you provided.')
            previous_image_id = current_image_id

            empty_list = annotations_by_image_id.get(current_image_id, [])
            temporal_dict = {'image': each_image_meta, 'annotations': empty_list, "categories": categories_metas}
            
            output_file_path = os.path.join(new_folder, f"{file_processed_name}.json")
            with open(output_file_path, 'w') as files:
                json.dump(temporal_dict, files, indent=4)
                
        print(f'All annotations have been extracted and saved in the folder {new_folder}.')

    def split_data(self, data_path: str, test_size: float = 0.2, shuffle: bool = False, random_state: int = 42) -> None:
        """
        This function is used to split the data into train and validation datasets.

        Args:
            - test_size (float): The size of the val dataset. Default is 0.2.
            - shuffle (bool): Whether to shuffle the data or not.
            - random_state (int): The random state to use when shuffling the data.

        Returns:
            - None. However, it saves the train and test datasets in the folder 'train_test_split'.
        """

        folder = glob(os.path.join(data_path, '*.json'))
        train, val = train_test_split(folder, 
                                      test_size=test_size, 
                                      shuffle=shuffle, 
                                      random_state=random_state)
        
        train_fold = os.path.join(self.path_to_save, 'train')
        val_fold = os.path.join(self.path_to_save, 'val')
        self._create_folder(train_fold)
        self._create_folder(val_fold)

        for each_train in train:
            self._copy_file(each_train, train_fold)
        for each_val in val:
            self._copy_file(each_val, val_fold)

    def _create_folder(self, folder: str) -> None:
        """
        This function is used to manage the folder.

        Args:
            folder (str): The folder to manage.

        Returns:
            None.
        """

        if os.path.exists(folder):
            print(f'The folder {folder} already exists. It will be removed and a new one will be created.')
            shutil.rmtree(folder)
        os.makedirs(folder)
        
    def _copy_file(self, file: str, folder: str) -> None:
        """
        This function is used to copy files from one folder to another.

        Args:
            file (str): The file to copy.
            folder (str): The folder to copy the file to.

        Returns:
            None.
        """

        shutil.copy(file, folder)

    def convert_to_hdf5(self, data_path: str, path_to_save: str, desired_name: str, is_data_already_normalized: bool) -> None:
        """
        This function is used to convert the either the train or val dataset in publyanet format to hdf5 format.
        This one is utils for train model such as LayoutFlow: https://julianguerreiro.github.io/layoutflow/

        Args:
            - path_to_data (str): The path to the data.
            - path_to_save (str): The path to save the data.

        Returns:
            - None. However, it saves the data in hdf5 format.
        """
        previous_image_id = None
        list_of_data = glob(os.path.join(data_path, '*.json'))
        with h5py.File(f'{path_to_save}/{desired_name}.h5', 'a') as h5f:
            for each_data in list_of_data:
                with open(each_data, 'r') as json_file:
                    data = json.load(json_file)
                image_id = data['image']['id']
                width = data['image']['width']
                height = data['image']['height']

                group_for_h5 = str(image_id)

                if previous_image_id is not None and image_id == previous_image_id:
                    raise Exception(f'Dear user, the image id {image_id} is duplicated. Please check the consistency of the data you provided.')
                else:
                    previous_image_id = image_id

                bbox_list = []
                categories_data = []

                for each_annotation in data['annotations']:
                    if is_data_already_normalized:
                        bbox_list.append(each_annotation['bbox'])
                    else:
                        bbox_normalized = [each_annotation['bbox'][0]/width, 
                                           each_annotation['bbox'][1]/height, 
                                           each_annotation['bbox'][2]/width, 
                                           each_annotation['bbox'][3]/height]
                        bbox_list.append(bbox_normalized)
                    categories_data.append(each_annotation['category_id'])
                h5f.create_group(group_for_h5)
                h5f[group_for_h5].create_dataset('bbox', data=np.array(bbox_list))
                h5f[group_for_h5].create_dataset('categories', data=np.array(categories_data))
                h5f[group_for_h5].create_dataset('length', data=np.array(len(categories_data)))
        print(f'The data has been successfully saved in the folder {path_to_save} in hdf5 format.')