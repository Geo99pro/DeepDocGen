import os
import h5py
import json
import shutil
import numpy as np
from glob import glob
from collections import defaultdict
from sklearn.model_selection import train_test_split


class ExtractAnnotationEngine:
    """
    This class extracts annotations from the PubLayNet dataset and performs operations like saving annotations,
    splitting datasets, and converting them into HDF5 format.

    Attributes:
        path_data_on_publyanet_format (str): Path to the PubLayNet JSON file.
        path_to_save (str): Path to save the processed files.

    Methods:
        process_annotations(): Extract and save annotations for each image.
        split_data(): Split the dataset into train and validation sets.
        convert_to_hdf5(): Convert data into HDF5 format.
    """

    def __init__(self, path_data_on_publyanet_format: str, path_to_save: str) -> None:
        """
        Initializes the ExtractAnnotationEngine.

        Args:
            path_data_on_publyanet_format (str): Path to the PubLayNet JSON file.
            path_to_save (str): Path to save the extracted annotations.
        """

        self.path_data_on_publyanet_format = path_data_on_publyanet_format
        self.path_to_save = path_to_save

    def process_annotations(self) -> None:
        """
        Extracts and saves annotations from the PubLayNet JSON file.

        This method creates a folder named `annotation_extracted` in the specified save path
        and saves each image's annotations as individual JSON files.

        Returns:
            None.
        """

        new_folder = os.path.join(self.path_to_save, 'annotation_extracted')
        if os.path.exists(new_folder):
            print(f'The folder {new_folder} already exists. It will be removed and a new one will be created.')
            shutil.rmtree(new_folder)
        os.makedirs(new_folder)

        with open(self.path_data_on_publyanet_format, "r") as files:
            data = json.load(files)

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
                raise Exception(f"Duplicate image ID {current_image_id} detected. Check data consistency.")
            previous_image_id = current_image_id

            empty_list = annotations_by_image_id.get(current_image_id, [])
            temporal_dict = {'image': each_image_meta, 'annotations': empty_list, "categories": categories_metas}
            
            output_file_path = os.path.join(new_folder, f"{file_processed_name}.json")
            with open(output_file_path, 'w') as files:
                json.dump(temporal_dict, files, indent=4)
                
        print(f'All annotations have been successfully saved in the folder {new_folder}. Check it out!')

    def split_data(self, data_path: str, test_size: float = 0.2, shuffle: bool = False, random_state: int = 42) -> None:
        """
        Splits data into train and validation sets.

        Args:
            data_path (str): Path to the data folder containing JSON files.
            test_size (float): Proportion of the validation dataset. Default is 0.2.
            shuffle (bool): Whether to shuffle the data. Default is False.
            random_state (int): Random state for reproducibility. Default is 42.

        Returns:
            None.
        """

        json_files = glob(os.path.join(data_path, '*.json'))
        train, val = train_test_split(json_files, 
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

        print(f"Data split completed. Train and validation sets saved in {self.path_to_save}")

    def convert_to_hdf5(self, data_path: str, path_to_save: str, desired_name: str, is_data_already_normalized: bool) -> None:
        """
        Converts dataset into HDF5 format.

        Args:
            data_path (str): Path to the folder containing JSON files.
            path_to_save (str): Path to save the HDF5 file.
            desired_name (str): Name for the HDF5 file.
            is_data_already_normalized (bool): Whether the bounding box coordinates are already normalized.

        Returns:
            None.
        """
        previous_image_id = None
        json_files = glob(os.path.join(data_path, '*.json'))
        hdfpy_file_path = os.path.join(path_to_save, f'{desired_name}.h5')

        with h5py.File(hdfpy_file_path, 'a') as h5f:

            for each_data in json_files:
                with open(each_data, 'r') as json_file:
                    data = json.load(json_file)
                image_id = data['image']['id']
                width = data['image']['width']
                height = data['image']['height']

                group_for_h5 = str(image_id)

                if previous_image_id is not None and image_id == previous_image_id:
                    raise ValueError(f"Duplicate image ID {image_id} detected. Check data consistency.")
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
        print(f'The data has been successfully saved in the folder {path_to_save} in HDF5 format.')

    def _create_folder(self, folder: str) -> None:
        """
        Creates or resets a folder.

        Args:
            folder (str): Path to the folder.

        Returns:
            None.
        """
        if os.path.exists(folder):
            print(f'The folder {folder} already exists. It will be removed and a new one will be created.')
            shutil.rmtree(folder)
        os.makedirs(folder)
        
    def _copy_file(self, file: str, folder: str) -> None:
        """
        Copies a file to the specified folder.

        Args:
            file (str): Path to the file.
            destination_folder (str): Destination folder.

        Returns:
            None.
        """
        shutil.copy(file, folder)
