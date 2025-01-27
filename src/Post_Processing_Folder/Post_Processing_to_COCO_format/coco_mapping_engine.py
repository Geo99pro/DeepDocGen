import os 
import yaml
import json
import shutil
import logging
import datetime
import xmltodict
import warnings
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from glob import glob
from random import randint
from random import sample as random
from sklearn.model_selection import train_test_split


class CocoMappingEngine:
    """
    This class is used to convert the xml files (output of the CONTENT GENERATOR) to COCO format.
    By default, the class will split the dataset into training and validation datasets with 80% and 20% respectively.

    Args:

        config_path (str):
            - The path to the configuration file.
    """

    def __init__(self, config_path, setup_logger: callable):
        
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logger = setup_logger
        process_output_path = self.config["Post_process_to_coco_format"]["parameters"]["process_output_path"]
        logger_file = os.path.join(process_output_path, f"coco_mapping_logs.log")
        if os.path.isfile(logger_file):
            os.remove(logger_file)
        self.logger = self.setup_logger(name='CocoMappingEngine', log_file=logger_file, level=logging.INFO)

    def load_config(self):
        """
        This method is used to load the configuration file.
        """
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        return self.config
    
    def visualize_image(self, rows: int, cols: int, random_choice: int, should_save_plot: bool, fig_size = (20, 20))-> None:
        """
        This method is used to visualize the images.

        Args:
            - rows(int): The number of rows.
            - cols(int): The number of columns.
            - random_choice(int): The number of random images to choose.
            - should_save_plot(bool): If True, the plot will be saved.
            - fig_size(tuple): The figure size.
        
        Returns:
            - None. However, the plot will be saved if should_save_plot is set to True.
        """
        list_of_images = glob(os.path.join(self.images_path, '*.png'))
        image_readed = []

        for image_path in random(list_of_images, random_choice):
            image_readed.append(mpimg.imread(image_path))
        fig = plt.figure(figsize=fig_size)
        rows, cols = rows, cols
        for i in range(1, rows*cols + 1):
            random_index = randint(0, len(image_readed)-1)
            imgs = image_readed[random_index]
            fig.add_subplot(rows, cols, i)
            plt.imshow(imgs)
            plt.axis(False)
            if should_save_plot:
                plt.savefig(self.output_path + '/visualize_image.png')

    def get_general_bbox_coords(self, block: dict)-> tuple:
        """
        This method is used to get the general bounding box coordinates.
        
        Args:
            - block (dict): The block dictionary.
            - width (int): The width of the image.
            - height (int): The height of the image.

        Returns:
            tuple : a tuple containing 
                - bbox (list): The bounding box coordinates.
                - area (float): The area of the bounding box.
                - subtype (str): The subtype of the bounding box.
                - polygone (list): list of polygone coordinates.
        """
        #logging.info('Getting the general bounding box coordinates...')
        bbox_normalized = [float(block["@x0"]), float(block["@y0"]), float(block["@x1"]), float(block["@y1"])]
        bbox_absolute = [self.width*bbox_normalized[0], self.height*bbox_normalized[1], self.width*bbox_normalized[2], self.height*bbox_normalized[3]]
        bbox_width = bbox_absolute[2] - bbox_absolute[0]
        bbox_height = bbox_absolute[3] - bbox_absolute[1]
        area = bbox_width*bbox_height

        bbox = [bbox_absolute[0], bbox_absolute[1], bbox_width, bbox_height] #-> format [x0, y0, width, height]
        subtype = block["@subtype"]

        all_point_x = [bbox_absolute[0], bbox_absolute[2], bbox_absolute[2], bbox_absolute[0], bbox_absolute[0]] #[x0, x1, x1, x0, x0]
        all_point_y = [bbox_absolute[1], bbox_absolute[1], bbox_absolute[3], bbox_absolute[3], bbox_absolute[1]] #[y0, y0, y1, y1, y0]

        polygone = [(x, y) for x, y in zip(all_point_x, all_point_y)]
        polygone = [p for x in polygone for p in x]
        polygone = [polygone]
        #logging.info('The general bounding box coordinates are successfully extracted.')
        return bbox, area, subtype, polygone

    def get_multiple_line_segmentation_coords(self, block: dict)-> list:
        """
        This method extracts the multiple line segmentation coordinates.

        Args:
            block: dict
                The block dictionary.
        Returns:
            list: list containing segmentation coordinates for all lines.
        """
        #logging.info('Getting the multiple line segmentation coordinates...')
        segmentation_coords_for_all_lines = []
        if self.which_segmentation == 'all_line_inside_block':

            for each_line in block['line']:
                bbox_per_line = [int(each_line['@x0']), int(each_line['@y0']), int(each_line['@x1']), int(each_line['@y1'])]
                all_point_x = [bbox_per_line[0], bbox_per_line[2], bbox_per_line[2], bbox_per_line[0], bbox_per_line[0]]
                all_point_y = [bbox_per_line[1], bbox_per_line[1], bbox_per_line[3], bbox_per_line[3], bbox_per_line[1]]

                polygone = [(x, y) for x, y in zip(all_point_x, all_point_y)]
                polygone = [p for x in polygone for p in x]
                polygone = [polygone]

                segmentation_coords_for_all_lines.extend(polygone)
                segmentation_coords_for_all_lines = [sum(segmentation_coords_for_all_lines, [])]

            return segmentation_coords_for_all_lines

        elif self.which_segmentation == 'only_block':
            bbox_per_block = [float(block['@x0'])*1200, float(block['@y0'])*1600, float(block['@x1'])*1200, float(block['@y1'])*1600] #you should optimize this part after.
            all_point_x = [bbox_per_block[0], bbox_per_block[2], bbox_per_block[2], bbox_per_block[0], bbox_per_block[0]]
            all_point_y = [bbox_per_block[1], bbox_per_block[1], bbox_per_block[3], bbox_per_block[3], bbox_per_block[1]]

            polygone = [(x, y) for x, y in zip(all_point_x, all_point_y)]
            polygone = [p for x in polygone for p in x]
            polygone = [polygone]
            #logging.info('The multiple line segmentation coordinates are successfully extracted.')
            return polygone
        else: 
            raise ValueError('The value of which_segmentation should be either all_line_inside_block or only_block.')

    def get_unique_line_segmentation_coords(self, block: dict)-> list:
        """
        This method extract the unique line segmentation coordinates.
        
        Args:
            - block (dict): The block dictionary.
        """
        #logging.info('Getting the unique line segmentation coordinates...')
        unique_line = block['line']
        if unique_line:
            bbox_for_unique_line = [int(unique_line['@x0']), int(unique_line['@y0']), int(unique_line['@x1']), int(unique_line['@y1'])]

            all_point_x = [bbox_for_unique_line[0], bbox_for_unique_line[2], bbox_for_unique_line[2], bbox_for_unique_line[0], bbox_for_unique_line[0]]
            all_point_y = [bbox_for_unique_line[1], bbox_for_unique_line[1], bbox_for_unique_line[3], bbox_for_unique_line[3], bbox_for_unique_line[1]]

            polygone = [(x, y) for x, y in zip(all_point_x, all_point_y)]
            polygone = [p for x in polygone for p in x]
            polygone = [polygone]
            #logging.info('The unique line segmentation coordinates are successfully extracted.')
            return polygone
        else:
            return None

    def process_first_case_constraints(self, block: dict, bbox: list, area: float, subtype: str, polygone: list[list])-> dict:
        """
        This function is responsible to handle the constraints in the first case. Which means that we have many elements in a given file.
        Extracts the segmentation of the element inside the bounding box, which can represent various types such as lines, tables, images, or equations.

        Args:
            - block: dict
                The block dictionary.
            - bbox: list
                The bounding box coordinates.
            - area: float
                The area of the bounding box.
            - subtype: str
                The subtype of the bounding box.
            - polygone: list
                The polygone coordinates.
        Returns:
        dict: dictionary containing the following
            -bbox: list
                The bounding box coordinates. Such as [x, y, width, height].
            -area: float
                The area of the bounding box.
            -subtype: str
                The subtype of the bounding box.
            -segmentation: list
                The segmentation coordinates.

        """

        if 'line' in block.keys():
            # CASE OF MULTIPLE LINES INSIDE THE BLOCK. (Text or listes)
            if isinstance(block['line'], list):
                segmentation_coords_for_all_lines = self.get_multiple_line_segmentation_coords(block=block)
                final_dict_for_block = {"bbox": bbox,
                                        "area": area,
                                        "subtype": subtype,
                                        "segmentation": segmentation_coords_for_all_lines,
                                        "iscrowd": 0}

            # CASE OF JUST ONE LINE INSIDE THE BLOCK. (TEXT OR LISTE)
            elif isinstance(block['line'], dict):
                segmenetation_for_unique_line = self.get_unique_line_segmentation_coords(block=block)
                final_dict_for_block = {"bbox": bbox,
                                        "area": area,
                                        "subtype": subtype,
                                        "segmentation": segmenetation_for_unique_line,
                                        "iscrowd": 0}

            else:
                raise ValueError('The value of line should be either list or dict.')

        # THIS PART MEANS THAT I JUST HAVE AN IMAGE, TABLE, EQUATION ...ETC
        else:
                final_dict_for_block = {"bbox": bbox,
                                        "area": area,
                                        "subtype": subtype,
                                        "segmentation": polygone,
                                        "iscrowd": 0}
        #logging.info('The first case constraints are successfully processed.')
        return final_dict_for_block
    
    def process_second_case_constraints(self, block: dict, bbox: list, area: float, subtype: str, polygone: list[list])-> dict:
        """
        This function is responsible to handle the constraints in the second case. Which means that we have one element in a given file.
        Extracts the segmentation of the element inside the bounding box, which can represent various types such as lines, tables, images, or equations.

        Args:
            block: dict
                The block dictionary.
            bbox: list
                The bounding box coordinates.
            area: float
                The area of the bounding box.
            subtype: str
                The subtype of the bounding box.
            polygone: list
                The polygone coordinates.
        Returns:
        dict: dictionary containing the following
            bbox: list
                The bounding box coordinates. Such as [x, y, width, height].
            area: float
                The area of the bounding box.
            subtype: str
                The subtype of the bounding box.
            segmentation: list
                The segmentation coordinates.
        """
        #logging.info('Processing the second case constraints...')
        if 'line' in block.keys():
            if isinstance(block['line'], dict):
                segmenetation_for_unique_line = self.get_unique_line_segmentation_coords(block=block)
                final_dict_for_block = {"bbox": bbox,
                                        "area": area,
                                        "subtype": subtype,
                                        "segmentation": segmenetation_for_unique_line,
                                        "iscrowd": 0}

            elif isinstance(block['line'], list):
                segmentation_coords_for_all_lines = self.get_multiple_line_segmentation_coords(block=block)
                final_dict_for_block = {"bbox": bbox,
                                        "area": area,
                                        "subtype": subtype,
                                        "segmentation": segmentation_coords_for_all_lines,
                                        "iscrowd": 0}

            else:
                raise ValueError('The value of line should be either list or dict.')
        else:
            final_dict_for_block = {"bbox": bbox,
                                    "area": area,
                                    "subtype": subtype,
                                    "segmentation": polygone,
                                    "iscrowd": 0}
        #logging.info('The second case constraints are successfully processed.')
        return final_dict_for_block
    
    def process_xml_file(self, xml_list_path: list[str])-> list[str]:
        """"
        This method is used to process the xml files. This processing basically consists of extracting the bounding 
        box coordinates, area, subtype, and segmentation coordinates of the elements inside the xml files.

        Args:
            xml_list_path: list[str]
                The list of xml files paths.

        Returns:
            list[dict]: list containing the readable format of the xml files.
        """
    
        self.logger.info('Processing the xml files...')
        dir_name = os.path.dirname(xml_list_path[0])+'_processed_file'

        self.manage_diretories([dir_name])

        for xml_file_path in xml_list_path:
            with open(xml_file_path, 'r') as file:
                data_dict = xmltodict.parse(file.read())

            for val in data_dict.values():
                for sub_values in val.values():
                    # FIRST CASE MEANS THAT IT'S CASE OF MUTIPLE ELEMENT WITHIN THE DOC (example : 5 bbox within the file)
                    if isinstance(sub_values, list):
                        temporal_list = []

                        for _, block in enumerate(sub_values):
                            if isinstance(block, dict):
                                bbox, area, subtype, polygone = self.get_general_bbox_coords(block=block)
                                final_dict_for_block = self.process_first_case_constraints(block=block, 
                                                                                            bbox=bbox, 
                                                                                            area=area, 
                                                                                            subtype=subtype, 
                                                                                            polygone=polygone)
                                
                            temporal_list.append(final_dict_for_block)
                        temporal_dict = {os.path.basename(xml_file_path).split('.')[0]: temporal_list}
                        with open(os.path.join(dir_name, os.path.basename(xml_file_path).split('.')[0])+'.json', 'w') as file:
                            json.dump(temporal_dict, file)
                            #path_first_case.append(os.path.join(dir_name, os.path.basename(xml_file_path).split('.')[0])+'.json')

                    # SECOND CASE MEANS THAT IT'S CASE OF ONE ELEMENT WITHIN THE DOC (example : 01 bbox within the pdf)
                    else:
                        temporal_list = []
                        bbox, area, subtype, polygone = self.get_general_bbox_coords(block=sub_values)
                        final_dict_for_block = self.process_second_case_constraints(block=sub_values, 
                                                                                    bbox=bbox, 
                                                                                    area=area, 
                                                                                    subtype=subtype, 
                                                                                    polygone=polygone)

                        temporal_list.append(final_dict_for_block)
                        temporal_dict = {os.path.basename(xml_file_path).split('.')[0]: temporal_list}
                        with open(os.path.join(dir_name, os.path.basename(xml_file_path).split('.')[0])+'.json', 'w') as file:
                            json.dump(temporal_dict, file)

        self.logger.info(f'Dear user ! all the processed files are saved in the directory : {dir_name}')    
        self.logger.info('The xml files are successfully processed.')
        return glob(os.path.join(dir_name, '*.json'))         

    def get_image_metas(self, image_dir_path: list[str], indx)-> list[dict]:
        """
        This method is used to retrieve the image metada in a given image path."""
        
        self.logger.info('Getting the image metas...')
        images_metas = []

        for i, img_path in enumerate(image_dir_path):
            file_name = os.path.basename(img_path)
            im = Image.open(img_path)
            width, height = im.size

            meta = {"licence": "ica2024@copyrigth",
                    "file_name": file_name,
                    "coco_url": "None",
                    "height": height,
                    "width": width,
                    "date_captured": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "flickr_url": "None",
                    "id": indx + i}
            images_metas.append(meta)
        self.logger.info('The image metas are successfully extracted.')
        return images_metas

    def process_xml_to_coco_format(self, processed_annotation: list[str], 
                        images_metas: list[str], 
                        categories_list_dict: list[dict], 
                        start_indx: int)-> tuple[list[dict], list[dict]]:
        """
        This method is used to put the processed xml files on COCO format.

        Args:
            processed_annotation: list[str]
                The list of processed annotation.
            images_metas: list[dict]
                The list of images metas.
            categories_list_dict: list[dict]
                The list of categories
            start_indx: int
                The starting index.
        """
        self.logger.info('Processing the xml files to COCO format...')
        id_counter = start_indx
        total_file_dataset = []
        list_of_categories = [each_dict['name'] for each_dict in categories_list_dict]
        categories_dict = {categories:i+1 for i, categories in enumerate(list_of_categories)}

        for file_path in processed_annotation:
            with open(file_path, 'r') as file:
                data = json.load(file)

            result_list = []
            for meta in images_metas:
                filename = os.path.basename(meta["file_name"]).split('.')[0]
                image_id = None
                if filename in data.keys():
                    for value in data.values():
                        image_meta = meta["id"]
                        for block in value:
                            if 'segmentation' in block.keys():
                                new_dict = {"id": id_counter,
                                            "image_id": image_meta,
                                            "category_id": categories_dict[block['subtype']],
                                            "area": block['area'],
                                            "bbox": block['bbox'],
                                            "segmentation": block['segmentation'],
                                            'iscrowd': 0}
                            else:
                                raise ValueError('The key segmentation is not in the block keys. Take a look at the block format.')
                            id_counter += 1
                            result_list.append(new_dict)

            total_file_dataset.extend(result_list)
        categories_list = [{"id": category_id, "name": name, "supercategory": "None"} for name, category_id in categories_dict.items()]            
        self.logger.info('The xml files are successfully processed to COCO format.')
        return total_file_dataset, categories_list

    def convert_to_json(self, name: str, dataset_dict: dict)-> None:
        """
        This method is used to convert the dataset to json format.
        
        Args:
            name: str
                The name to give to the json file.
            dataset_dict: dict
                The dataset dictionary.
        """

        self.logger.info(f'Converting the dataset name {name} into the json format...')
        with open(name + '.json', 'w') as file:
            json.dump(dataset_dict, file)

    def split_dataset(self)-> tuple[list[dict], list[dict], list[dict]]:
        """
        This method is used to split the dataset into training, validation, and test datasets. Also it will create the directories for the training, validation, and test datasets
        and fill them with the splitted dataset.
        By default, the method will split the dataset into training and validation datasets with 80% and 20% respectively.

        Args:
            train_percentage: float
                The percentage of the training dataset.
            val_percentage: float
                The percentage of the validation dataset.
            shuffle_data: bool
                If True, the data will be shuffled.
            **kwargs: dict
                The test percentage.
        Returns:
            list: list containing the splitted dataset.
        """

        self.logger.info(f'Splitting the dataset with the flag how_many_data_split set to {self.how_many_data_split}...')
        image_path = glob(os.path.join(self.images_path, '*.png'))
        annotation_path = glob(os.path.join(self.xmls_path, '*.xml'))

        if self.how_many_data_split == 1:
            self.logger.info('The dataset is not splitted. The cause is due to the fact that the value of how_many_data_split is set to 1.')
            raise ValueError('The value of how_many_data_split should be greater than 1.')

        elif self.how_many_data_split == 2:
            Train_data = os.path.join(self.output_path, 'Training_dataset')
            Val_data = os.path.join(self.output_path, 'Validation_dataset')
            Train_data_annotation = os.path.join(self.output_path, 'Training_annotation')
            Val_data_annotation = os.path.join(self.output_path, 'Validation_annotation')

            train_images, val_images  = train_test_split(image_path,
                                                        train_size=self.train_percentage,
                                                        test_size=self.val_percentage,
                                                        random_state=self.random_state,
                                                        shuffle=self.shuffle_data)

            self.manage_diretories([Train_data, 
                                    Val_data,
                                    Train_data_annotation, 
                                    Val_data_annotation])
            
            self.get_correct_annotation_file(train_images, annotation_path, Train_data_annotation)
            self.get_correct_annotation_file(val_images, annotation_path, Val_data_annotation)

            self.logger.info(f'Dear User! after splitting the dataset, the training dataset contains {len(train_images)} images '
                        f'{len(glob(os.path.join(Train_data_annotation, "*.xml")))} annotations. '
                        f'And the validation dataset contains {len(val_images)} images '
                        f'{len(glob(os.path.join(Val_data_annotation, "*.xml")))} annotations.')

            Train_data=self.copy_files(train_images, Train_data)
            Val_data=self.copy_files(val_images, Val_data)

            self.logger.info('The dataset is successfully splitted onto training and validation datasets.')
            return Train_data, Val_data, glob(os.path.join(Train_data_annotation, "*.xml")), glob(os.path.join(Val_data_annotation, "*.xml"))

        elif self.how_many_data_split == 3:
            Train_data = os.path.join(self.output_path, 'Training_dataset')
            Val_data = os.path.join(self.output_path, 'Validation_dataset')
            Test_data = os.path.join(self.output_path, 'Test_dataset')
            Train_data_annotation = os.path.join(self.output_path, 'Training_annotation')
            Val_data_annotation = os.path.join(self.output_path, 'Validation_annotation')
            Test_data_annotation = os.path.join(self.output_path, 'Test_annotation')
            
            train_images, remaining_images = train_test_split(image_path,
                                                        train_size=self.train_percentage,
                                                        test_size=self.val_percentage + self.test_percentage,
                                                        random_state=self.random_state,
                                                        shuffle=self.shuffle_data)

            val_images, test_images = train_test_split(remaining_images,
                                                        train_size=0.8,
                                                        test_size=0.2,
                                                        random_state=self.random_state,
                                                        shuffle=self.shuffle_data)

            self.manage_diretories([Train_data, 
                                    Val_data, 
                                    Test_data, 
                                    Train_data_annotation,
                                    Val_data_annotation,
                                    Test_data_annotation])

            self.get_correct_annotation_file(train_images, annotation_path, Train_data_annotation)
            self.get_correct_annotation_file(val_images, annotation_path, Val_data_annotation)
            self.get_correct_annotation_file(test_images, annotation_path, Test_data_annotation)

            self.logger.info(f'Dear User! after splitting the dataset, the training dataset contains {len(train_images)} images '
                            f'{len(glob(os.path.join(Train_data_annotation, "*.xml")))} annotations. '
                            f'The validation dataset contains {len(val_images)} images '
                            f'{len(glob(os.path.join(Val_data_annotation, "*.xml")))} annotations. '
                            f'And finally, the test dataset contains {len(test_images)} images '
                            f'{len(glob(os.path.join(Test_data_annotation, "*.xml")))} annotations.')
            Train_data=self.copy_files(train_images, Train_data)
            Val_data=self.copy_files(val_images, Val_data)
            Test_data=self.copy_files(test_images, Test_data)
            return Train_data, Val_data, Test_data, glob(os.path.join(Train_data_annotation, "*.xml")), glob(os.path.join(Val_data_annotation, "*.xml")), glob(os.path.join(Test_data_annotation, "*.xml"))

        else:
            raise ValueError('The value of how_many_data_split should be either 2 or 3.')

    def manage_diretories(self, directories: list[str])-> None:
        """
        This method is used to manage the directories. Such as create or recreate the directories.
        """

        self.logger.info('Managing the directories...')
        for directory in directories:
            if os.path.exists(directory):
                self.logger.info(f'Dear user the folder {directory} already exists. I will remove it and create a new one.')
                shutil.rmtree(directory)
            os.makedirs(directory, exist_ok=True)
        self.logger.info('The directories are successfully managed.')

    def copy_files(self, source: list[str], destination: list[str])-> None:
        """
        This method is used to copy the files from source to destination.
        """
        self.logger.info('Copying the files...')
        copied_files = []
        for file in source:
            shutil.copy(file, destination)
            copied_files.append(os.path.join(destination, os.path.basename(file)))
        self.logger.info('The files are successfully copied.')
        return copied_files 

    def map_on_coco_format(self):
        """
        This method is used to map on COCO format.  
        """

        if self.config["Post_process_to_coco_format"]["should_perform"]:
            self.images_path = self.config["Post_process_to_coco_format"]["parameters"]["document_image_path"]
            self.xmls_path = self.config["Post_process_to_coco_format"]["parameters"]["annotation_xml_path"]
            self.width = self.config["Post_process_to_coco_format"]["parameters"]["image_witdh"]
            self.height = self.config["Post_process_to_coco_format"]["parameters"]["image_height"]
            self.how_many_data_split = self.config["Post_process_to_coco_format"]["parameters"]["how_many_data_split"]
            self.train_percentage = self.config["Post_process_to_coco_format"]["parameters"]["training_percentage"]
            self.val_percentage = self.config["Post_process_to_coco_format"]["parameters"]["validation_percentage"]
            self.test_percentage = self.config["Post_process_to_coco_format"]["parameters"]["test_percentage"]
            self.shuffle_data = self.config["Post_process_to_coco_format"]["parameters"]["should_shuffle_data"]
            self.random_state = self.config["Post_process_to_coco_format"]["parameters"]["random_seed"]
            self.which_segmentation = self.config["Post_process_to_coco_format"]["parameters"]["which_segmentation_method"]
            self.categories_list_dict = self.config["Post_process_to_coco_format"]["parameters"]["category_list_dict"]
            self.vis_image = self.config["Post_process_to_coco_format"]["parameters"]["should_visualize_image"]
            self.output_path = self.config["Post_process_to_coco_format"]["parameters"]["process_output_path"]
            self.logger.info('Starting the mapping on COCO format process from the configuration file {self.config_path} and by setting the flag should_perform to True in the configuration.')

            if self.vis_image:
                self.visualize_image(rows=3, cols=3, random_choice=9, should_save_plot=True)

            if self.how_many_data_split == 2:
                Train_data, Val_data, Train_data_annotation, Val_data_annotation = self.split_dataset()

                train_images_metas = self.get_image_metas(Train_data, indx=1)
                val_images_metas = self.get_image_metas(Val_data, indx=len(train_images_metas)+1)
                processed_train_annotations = self.process_xml_file(Train_data_annotation)
                processed_val_annotations = self.process_xml_file(Val_data_annotation)

                train_dataset_coco_format, categories_list = self.process_xml_to_coco_format(processed_annotation=processed_train_annotations,
                                                                        images_metas=train_images_metas,
                                                                        categories_list_dict=self.categories_list_dict,
                                                                        start_indx=1)

                val_dataset_coco_format, _ = self.process_xml_to_coco_format(processed_annotation=processed_val_annotations,
                                                                        images_metas=val_images_metas,
                                                                        categories_list_dict=self.categories_list_dict,
                                                                        start_indx=len(train_dataset_coco_format)+1)

                train_coco_document = {"info": "Training dataset",
                                    "images": train_images_metas,
                                    "annotations": train_dataset_coco_format,
                                    "categories": categories_list}

                val_coco_document = {"info": "Validation dataset",
                                    "images": val_images_metas,
                                    "annotations": val_dataset_coco_format,
                                    "categories": categories_list}

                self.convert_to_json('train_coco_document', train_coco_document)
                self.convert_to_json('val_coco_document', val_coco_document)
                shutil.move('train_coco_document.json', os.path.join(self.output_path, 'train_coco_document.json'))
                shutil.move('val_coco_document.json', os.path.join(self.output_path, 'val_coco_document.json'))
                self.logger.info('The mapping on COCO format is successfully performed.')

            elif self.how_many_data_split == 3:
                Train_data, Val_data, Test_data, Train_data_annotation, Val_data_annotation, Test_data_annotation = self.split_dataset()

                train_images_metas = self.get_image_metas(Train_data, indx=1)
                val_images_metas = self.get_image_metas(Val_data, indx=len(train_images_metas)+1)
                test_images_metas = self.get_image_metas(Test_data, indx=len(val_images_metas)+1)
                processed_train_annotations = self.process_xml_file(Train_data_annotation)
                processed_val_annotations = self.process_xml_file(Val_data_annotation)
                processed_test_annotations = self.process_xml_file(Test_data_annotation)

                train_dataset_coco_format, categories_list = self.process_xml_to_coco_format(processed_annotation=processed_train_annotations,
                                                                        images_metas=train_images_metas,
                                                                        categories_list_dict=self.categories_list_dict,
                                                                        start_indx=1)

                val_dataset_coco_format, _ = self.process_xml_to_coco_format(processed_annotation=processed_val_annotations,
                                                                        images_metas=val_images_metas,
                                                                        categories_list_dict=self.categories_list_dict,
                                                                        start_indx=len(train_dataset_coco_format)+1)

                test_dataset_coco_format, _ = self.process_xml_to_coco_format(processed_annotation=processed_test_annotations,
                                                                        images_metas=test_images_metas,
                                                                        categories_list_dict=self.categories_list_dict,
                                                                        start_indx=len(val_dataset_coco_format)+1)

                train_coco_document = {"info": "Training dataset",
                                    "images": train_images_metas,
                                    "annotations": train_dataset_coco_format,
                                    "categories": categories_list}

                val_coco_document = {"info": "Validation dataset",
                                    "images": val_images_metas,
                                    "annotations": val_dataset_coco_format,
                                    "categories": categories_list}

                test_coco_document = {"info": "Test dataset",
                                    "images": test_images_metas,
                                    "annotations": test_dataset_coco_format,
                                    "categories": categories_list}

                self.convert_to_json('train_coco_document', train_coco_document)
                self.convert_to_json('val_coco_document', val_coco_document)
                self.convert_to_json('test_coco_document', test_coco_document)
                shutil.move('train_coco_document.json', os.path.join(self.output_path, 'train_coco_document.json'))
                shutil.move('val_coco_document.json', os.path.join(self.output_path, 'val_coco_document.json'))
                shutil.move('test_coco_document.json', os.path.join(self.output_path, 'test_coco_document.json'))
        else:
            warnings.warn('The mapping on COCO format is not performed. Please set the flag should_perform to True in the configuration file.')

    def zipper(self, path: str)-> None:
        """
        This method is used to zip the files.
        """
        #TO DO: Implement the zip method.

    def get_correct_annotation_file(self, meta_splitted_data: list[str], annotation_folder: list[str], destination: str)-> None:
        """
        This method is used to check the consistency between the image and annotation files befor copying the files.
        Args:
            meta_splitted_data: list[str]
                The list of meta splitted data. Either training, validation, or test data.
            annotation_folder: list[str]
                The list of annotation folder. Ps: The annotation folder should contain the xml files and represent the whole dataset.
            destination: str
                The destination for the copied files.
        """
        self.logger.info('Checking the consistency between the image and annotation files before splitting the dataset...')

        meta_splitted_file_names = self.get_file_names_without_extension(meta_splitted_data)
        for file_path in annotation_folder:
            current_file_name = ".".join(os.path.basename(file_path).split('.')[:-1])
            if current_file_name in meta_splitted_file_names:
                self.copy_simple_file(file_path, destination)
            else:
                pass

    def get_file_names_without_extension(self, paths)-> list[str]:
        """
        This method is used to get the file names without extension and return them as a list.
        """
        return [".".join(os.path.basename(path).split('.')[:-1]) for path in paths]
    
    def copy_simple_file(self, source: str, destination: str)-> None:
        """
        This method is used to copy a simple file.
        """
        shutil.copy(source, destination)