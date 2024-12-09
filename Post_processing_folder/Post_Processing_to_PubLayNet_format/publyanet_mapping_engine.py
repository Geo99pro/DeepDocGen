import os
import json

class PublaynetMappingEngine:
    """
    This class maps the output of VoTT software to the PubLayNet format.

    Attributes:
        vott_json_path (str): Path to the VoTT JSON file.
        image_meta_id (int): Starting image ID.
        annotation_id_start (int): Starting annotation ID.
        path_to_save (str): Path to save the PubLayNet JSON file.
        desired_name (str): Desired name for the output file.
        kwargs (dict): Additional options (e.g., normalize_coords).

    Methods:
        load_vott_json(): Loads the VoTT JSON file.
        save_publaynet_json(): Saves the PubLayNet JSON file.
        extract_vott_categories(): Extracts categories from VoTT metadata.
        extract_image_metas(): Processes and appends image metadata.
        extract_blocks_coordinates(): Extracts block coordinates and updates annotations.
        map_vott_to_publaynet(): Maps VoTT output to PubLayNet format.
    """

    def __init__(self, vott_json_path: str, image_meta_id: int, annotation_id_start: int, path_to_save: str, desired_name: str, **kwargs):
        self.vott_json_path = vott_json_path
        self.image_meta_id = image_meta_id
        self.annotation_id_start = annotation_id_start
        self.path_to_save = path_to_save
        self.desired_name = desired_name
        self.kwargs = kwargs

    def load_vott_json(self):
        """
        Loads the VoTT JSON file.

        Returns:
            dict: Parsed VoTT JSON data.
        """
        with open(self.vott_json_path) as files:
            self.vott_data = json.loads(files.read())
        return self.vott_data

    def save_publaynet_json(self, publaynet_data: dict):
        """
        Saves the data in PubLayNet format as a JSON file.

        Args:
            publaynet_data (dict): Data in PubLayNet format.
        """
        file_name = os.path.basename(self.vott_json_path).split('.')[0]
        with open(f"{self.path_to_save}{self.desired_name}_publyanet.json", 'w') as files:
            json.dump(publaynet_data, files, indent=4)
            print(f'Conversion to PubLayNet format has been successfully completed for the file : {file_name}.\n'
                f'The conversion is saved in {self.path_to_save} with the name {self.desired_name}_publyanet.json')

    def extract_vott_categories(self, general_values: list[dict])-> list[dict]:
        """
        Extracts categories from VoTT metadata.

        Args:
            general_values (list[dict]): Metadata tags from VoTT.

        Returns:
            list[dict]: List of categories in PubLayNet format.
        """

        categories = []

        for idx, element in enumerate(general_values, start=1):
            category_dict = {'supercategory': None,
                            'id': idx,
                            'name': element['name']}
            categories.append(category_dict)
        return categories

    def extract_image_metas(self, 
                            meta_keys: dict.keys, 
                            sub_meta_values: dict.values, 
                            image_meta_list: list, 
                            image_id_start: int)-> list[dict]:
        """
        Processes annotated image metadata and appends it to the image_meta_list.

        Args:
            meta_keys (str): Key of the current metadata entry.
            sub_meta_values (dict): Metadata values for the current entry.
            image_meta_list (list): List to store processed image metadata.
            image_id_start (int): Starting ID for images.

        Returns:
            tuple: Updated image_meta_list and the processed image metadata.
        """

        if meta_keys == sub_meta_values['id']:
            #print(f'Good matching between keys. Well done Buddy !')
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
        Extracts block coordinates and updates annotation metadata.

        Args:
            sub_meta_values (list[dict]): Block metadata.
            annotation_meta_list (list): List to store annotation metadata.
            annotation_id_start (int): Starting ID for annotations.
            categories (list[dict]): Categories extracted from metadata.
            image_id (int): ID of the associated image.
            annotated_image_meta_dict (dict): Metadata for the annotated image.

        Returns:
            list: Updated annotation metadata.
        """
        
        for block_info in sub_meta_values:
            tags = ''.join(block_info['tags']) # type of block
            category_id = next((category['id'] for category in categories if tags == category['name']), None)

            x0, y0 = block_info['boundingBox']['left'], block_info['boundingBox']['top']
            width, height = block_info['boundingBox']['width'], block_info['boundingBox']['height']
            x1, y1 = x0 + width, y0 + height
     
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
            vott_data (dict): A dictionary containing the output of VoTT software.

        Returns:
            None. However, it saves the PubLayNet json file.
        """

        general_image_meta, general_annotation_meta = [], []    
        
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

        publaynet_data = {'images': image_meta_output, 
                            'categories': categories_in_annotations,
                            'annotations': general_annotation_meta}

        self.save_publaynet_json(publaynet_data)
