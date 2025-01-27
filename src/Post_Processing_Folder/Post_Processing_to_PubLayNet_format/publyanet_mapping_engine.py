import os
import json

class PublaynetMappingEngine:
    """
    This class is used to map the output of VoTT software to the PubLayNet format.
    By using this class, you can map the output of VoTT software to the PubLayNet format.

    Attributes:
        - vott_json_path (str): The path to the VoTT json file.
        - image_meta_id (int): The starting image id.
        - annotation_id_start (int): The starting annotation id.
        - path_to_save (str): The path to save the PubLayNet json file.
        - kwargs (dict): Additional keyword arguments. Such as desired_name for puand normalize_coords.

    Methods:

        - load_vott_json: Load the VoTT json file.
        - save_publaynet_json: Save the PubLayNet json file.
        - extract_vott_categories: Extract categories from the VoTT metadata.
        - extract_image_metas: Process annotated image metadata and append it to the images_meta_list.
        - extract_blocks_coordinates: Extract block coordinates from sub_meta_values and update annotation_meta_list.
        - map_vott_to_publaynet: Map the output of VoTT software to the PubLayNet format.
    """

    def __init__(self,
                 vott_json_path: str,
                 image_meta_id: int,
                 annotation_id_start: int,
                 path_to_save: str,
                 desired_name: str,
                 **kwargs):
        self.vott_json_path = vott_json_path
        self.image_meta_id = image_meta_id
        self.annotation_id_start = annotation_id_start
        self.path_to_save = path_to_save
        self.desired_name = desired_name
        self.kwargs = kwargs

    def load_vott_json(self):
        with open(self.vott_json_path) as files:
            self.vott_data = json.loads(files.read())
        return self.vott_data

    def save_publaynet_json(self, publaynet_data: dict):
        file_name = os.path.basename(self.vott_json_path).split('.')[0]
        with open(f"{self.path_to_save}{self.desired_name}_publyanet.json", 'w') as files:
            json.dump(publaynet_data, files, indent=4)
            #print(f'Conversion to PubLayNet format has been successfully completed for the file : {file_name}.\n'
                #f'The conversion is saved in {self.path_to_save} with the name {self.desired_name}_publyanet.json')

    def extract_vott_categories(self, general_values: list[dict])-> list[dict]:
        """
        This functions extracts categories from the VoTT metadata.

        Args:
            - general_values (list[dict]): A list of dictionaries containing categories.

        Returns:
            - categories (list[dict]): A list of dictionaries containing categories.
        """

        categories = []
        id_category = 1

        for element in general_values:
            category_dict = {'supercategory': None,
                            'id': id_category,
                            'name': element['name']}
            id_category += 1
            categories.append(category_dict)
        return categories

    def extract_image_metas(self, 
                            meta_keys: dict.keys, 
                            sub_meta_values: dict.values, 
                            image_meta_list: list, 
                            image_id_start: int)-> list[dict]:
        """
        This functions processes annotated image metadata and appends it to the images_meta_list.
        
        Args:
            - meta_keys: A list of keys in the metadata.
            - sub_meta_values: A list of values in the metadata.
            - image_meta_list: A list of dictionaries containing metadata.
            - image_id_start: The starting image id.

        Returns:

            - image_meta_list (list[dict]): Updated images_meta_list containing the appended image metadata dictionaries.
            - annotated_image_meta_dict (dict): A dictionary containing the annotated image metadata.
        """

        if meta_keys == sub_meta_values['id']:
            annotated_image_meta_dict = {'file_name': sub_meta_values['name'],
                                        'width': sub_meta_values['size']['width'],
                                        'height': sub_meta_values['size']['height'],
                                        'id': image_id_start}

            image_meta_list.append(annotated_image_meta_dict)

        return image_meta_list, annotated_image_meta_dict

    def extract_blocks_coordinates(self, sub_meta_values: list[dict], 
                                annotation_meta_list: list, 
                                annotation_id_start: int, 
                                categories: list[dict], 
                                image_id: int, 
                                annotated_image_meta_dict: dict)-> list[dict]:
        """
        This functions extracts block coordinates from sub_meta_values and updates annotation_meta_list.

        Args:
            sub_meta_values (list[dict]): A list of dictionaries containing block informations
            annotation_meta_list (list): A list of dictionaries containing annotation metadata.
            annotation_id_start (int): The starting annotation id.
            categories (list[dict]): A list of dictionaries containing categories.
            image_id (int): The image id on which the blocks is associated.

        Returns:
            annotation_meta_list (list): Updated annotation_meta_list containing the appended annotation metadata dictionaries.
        """
        for block_info in sub_meta_values:
            #print((block_info))
            tags = ''.join(block_info['tags']) # type of block
            #print(tags)
            for category in categories:
                if tags == category['name']:
                    category_id = category['id']
                    break
            else:
                category_id = None
            x0 = block_info['boundingBox']['left']
            y0 = block_info['boundingBox']['top']
            x1 = block_info['boundingBox']['width'] + x0
            y1 = block_info['boundingBox']['height'] + y0
            width = block_info['boundingBox']['width']
            height = block_info['boundingBox']['height']

            all_points_x = [x0, x1, x1, x0, x0]
            all_points_y = [y0, y0, y1, y1, y0]
            polygone = [(x, y) for x, y in zip(all_points_x, all_points_y)]
            polygone = [p for x in polygone for p in x]
            polygone = [polygone]

            if self.kwargs.get('normalize_coords'):
                n_x0 = x0 / annotated_image_meta_dict['width']
                n_y0 = y0 / annotated_image_meta_dict['height']
                n_width = width / annotated_image_meta_dict['width']
                n_height = height / annotated_image_meta_dict['height']
                n_all_points_x = [x / annotated_image_meta_dict['width'] for x in all_points_x]
                n_all_point_y = [y / annotated_image_meta_dict['height'] for y in all_points_y]
                n_polygone = [(x, y) for x, y in zip(n_all_points_x, n_all_point_y)]
                n_polygone = [p for x in n_polygone for p in x]
                n_polygone = [n_polygone]

                block_meta = {'id': annotation_id_start,
                            'image_id': image_id - 1,
                            'bbox': [n_x0, n_y0, n_width, n_height],
                            'segmentation': n_polygone,
                            'module': None,
                            'category_id': category_id,
                            'area': n_width * n_height,
                            'iscrowd': 0}
                annotation_meta_list.append(block_meta)
                annotation_id_start += 1

            else :
                block_meta = {'id': annotation_id_start,
                            'image_id': image_id - 1,
                            'bbox': [x0, y0, width, height],
                            'segmentation': polygone,
                            'module': None,
                            'category_id': category_id,
                            'area': width * height,
                            'iscrowd': 0}

                annotation_meta_list.append(block_meta)
                annotation_id_start += 1

        return annotation_meta_list

    def map_vott_to_publaynet(self):
        """
        This functions maps the output of VoTT software to the PubLayNet format.

        Args:
            - vott_data (dict): A dictionary containing the output of VoTT software.

        Returns:
            - None. However, it saves the PubLayNet json file.
        """

        general_image_meta = []
        general_annotation_meta = []    
        
        vott_data = self.load_vott_json()
        for general_keys, general_values in vott_data.items():

            if general_keys == 'tags':
                categories_in_annotations = self.extract_vott_categories(general_values=general_values)
            
            if general_keys == 'assets':
                self.image_meta_id = self.image_meta_id
                self.annotation_id_start = self.annotation_id_start

                for meta_keys, meta_values in general_values.items():
                    #print(f'I am in the in PDF -> {meta_keys}')

                    for sub_meta_keys, sub_meta_values in meta_values.items():
                        if sub_meta_keys == 'asset':
                            image_meta_output, annotated_image_meta_dict = self.extract_image_metas(meta_keys=meta_keys,
                                                                                                    sub_meta_values=sub_meta_values,
                                                                                                    image_meta_list=general_image_meta,
                                                                                                    image_id_start=self.image_meta_id)
                            self.image_meta_id += 1

                        if sub_meta_keys == 'regions':
                            annotation_meta_output = self.extract_blocks_coordinates(sub_meta_values=sub_meta_values,
                                                                                    annotation_meta_list=general_annotation_meta,
                                                                                    annotation_id_start=self.annotation_id_start,
                                                                                    categories=categories_in_annotations,
                                                                                    image_id=self.image_meta_id,
                                                                                    annotated_image_meta_dict=annotated_image_meta_dict)
                            
                            self.annotation_id_start = annotation_meta_output[-1]['id'] + 1
                        #break #-> uncomment this line to test the code with only one image.

        final_dictionary = {'images': image_meta_output, 
                            'categories': categories_in_annotations,
                            'annotations': general_annotation_meta}

        self.save_publaynet_json(final_dictionary)