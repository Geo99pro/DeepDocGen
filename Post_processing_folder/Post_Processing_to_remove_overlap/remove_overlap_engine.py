import os
import json
import shutil
import random
import pandas as pd
import yaml
import warnings
from glob import glob
from copy import deepcopy
from random import betavariate
from PIL import Image, ImageDraw

class RemoveOverlapEngine:
    """
    This class is used to remove the overlapped bbox from layout documents.
    By using this class, we can remove the overlapped bbox from layout documents.

    Attributes:

        layout_gen_annotation_path : str
            The path to the layout documents outputed by the layout generator.
        vmin : float
            The minimum value of the distance delta.
        vmax : float
            The maximum value of the distance delta.
        reconstruct_image_path : str
            The path to the reconstructed image.
        reconstruct_annotation_path : str
            The path to the reconstructed annotation.


    Methods:

        - load_json() -> list[dict]
            This method is used to load the json files output of the layout generator. And return a list of dictionaries.
        - create_dataframe() -> list[pd.DataFrame]
            This method is used to create a dataframe from the json files output of the layout generator.
            It returns a list of dataframes, where each dataframe corresponds to a file outputed by the layout generator.
        - generate_random_distance_delta() -> float
            This method is used to generate random distance delta between vmin and vmax.
            It returns the distance delta.
        - generate_beta_distribution() -> float
            This method is used to generate random distance delta from beta distribution.
            It returns the distance delta.
        - compute_intersection_metas(block_1: pd.Series, block_2: pd.Series) -> tuple
            This method is used to compute the intersection metas between two bboxes.
            It returns the intersection width, intersection height, intersection area, and intersection block.
        compute_bbox_area(block_1: pd.Series, block_2: pd.Series) -> float
            This method is used to compute the area of two bounding boxes.
            It returns the block_1 width, block_1 height, block_2 width, block_2 height, block_1 area, block_2 area.
        verify_overlap(block_1: pd.Series, block_2: pd.Series) -> bool
            This method is used to verify if two bounding boxes are overlapped.
        get_relative_position(block_1: pd.Series, block_2: pd.Series) -> str
            This method is used to get the relative position between two bounding boxes in 2D space.
        determine_overlap_side(block_1: pd.Series, block_2: pd.Series) -> str
            This method is used to determine the overlap side between two bboxes partially overlapped.
        treat_b1_completely_overlapping_b2(block_1_area: float, block_2_area: float, block_1: pd.Series, block_2: pd.Series) -> list
            This method is used to treat the case where block_1 is completely overlapping block_2.
        treat_b2_completely_overlapping_b1(block_1_area: float, block_2_area: float, block_1: pd.Series, block_2: pd.Series) -> list
            This method is used to treat the case where block_2 is completely overlapping block_1.
        treat_b1_partially_overlapping_b2_on_left_top_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the left top corner.
        treat_b1_partially_overlapping_b2_on_right_top_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the right top corner.
        treat_b1_partially_overlapping_b2_on_left_bottom_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the left bottom corner.
        treat_b1_partially_overlapping_b2_on_right_bottom_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the right bottom corner.
        treat_b1_partially_overlapping_b2_on_center_top_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the center top corner.
        treat_b1_partially_overlapping_b2_on_center_bottom_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the center bottom corner.
        treat_b1_partially_overlapping_b2_on_left_center_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the left center corner.
        treat_b1_partially_overlapping_b2_on_center_center_corner(block_1: pd.Series, block_2: pd.Series, intersection_area: float, intersection_width: float, intersection_height: float, block_1_area: float, block_2_area: float) -> dict
            This method is used to treat the case where block_1 is partially overlapping block_2 on the center center corner.
        create_new_block(x0, y0, x1, y1)
            This method is used to create a new block.
        choose_action_for_overlap_case(block_1: pd.Series, block_2: pd.Series)
            This method is used to correct the overlap between two bboxes.
        remove_overlapped_bbox()
            This method is used to remove the overlapped bbox from layout documents.
        reconstruct_normal_format()
            This method is used to reconstruct the layout documents in normal format.
        create_image_after_correction(reconstructed_data: pd.DataFrame, type_of_format: str)
            This method is used to create the image after correction
        convert_to_json (reconstructed_data: pd.DataFrame, type_of_format: str)
        
    """

    def __init__(self, config_path: str):
        """
        This class is used to remove the overlapped bbox from layout documents outputed by the layout generator.
        By using this class, we can remove the overlapped bbox from layout documents.

        Attributes:
            layout_gen_annotation_path : str
                The path to the layout documents outputed by the layout generator.
        
        Methods:
        ------------
        """
        self.config_path = config_path
        self.config = self.load_config()


        self.layout_gen_annotation_path = self.config["Post_process_to_remove_overlap"]["Parameters"]["layout_gener_coord_path"]
        self.vmin = self.config["Post_process_to_remove_overlap"]["Parameters"]["vmin"]
        self.vmax = self.config["Post_process_to_remove_overlap"]["Parameters"]["vmax"]
        self.reconstruct_image_path = self.config["Post_process_to_remove_overlap"]["Parameters"]["where_to_save_reconstructed_image"]
        self.reconstruct_annotation_path = self.config["Post_process_to_remove_overlap"]["Parameters"]["where_to_save_reconstructed_coords"]

    def load_config(self)-> dict:
        """
        This method is used to load the configuration file.
        """

        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        return self.config

    def load_json(self)-> list[dict]:
        """
        This method is used to load the json files output of the layout generator. And return a list of dictionaries.
        """

        data_list = []
        annotations_path = glob(os.path.join(self.layout_gen_annotation_path, '*.json'))
        for anno_path in annotations_path:
            with open(anno_path, 'r') as file:
                opened_file = json.load(file)
            data = {'corresponding_image':os.path.basename(anno_path).split('.')[0]+'.png',
                    'content': opened_file}
            data_list.append(data)
        print(f"{len(data_list)} json files output of the layout generator are loaded.")
        return data_list

    def create_dataframe(self):
        """
        This method is used to create a dataframe from the json files output of the layout generator.
        It returns a list of dataframes, where each dataframe corresponds to a file outputed by the layout generator.
        """

        dataframe_list = []
        data_list = self.load_json()
        
        for data in data_list:
            hold_new_list = []
            for k, v in data.items():
                if k == 'corresponding_image':
                    file_name = v
                elif k == 'content':
                    for sub_v in v.values():
                        for _, i in enumerate(range(len(sub_v))):
                            new_list = [sub_v[i][0], sub_v[i][1], file_name]
                            hold_new_list.append(new_list)

            corresponding_dataframe = pd.DataFrame(data=[(data[0][0], data[0][1], data[0][2], data[0][3], data[1], data[2]) for data in hold_new_list],
                                                columns=['x0', 'y0', 'x1', 'y1', 'Bbox_type', 'corresponding_image'])
            dataframe_list.append(corresponding_dataframe)
        return dataframe_list

    def generate_random_distance_delta(self):
        """
        This method is used to generate random distance delta between vmin and vmax.
        It returns the distance delta.
        """

        distance_delta = float("{:.3f}".format(random.uniform(self.vmin, self.vmax)))
        return distance_delta

    def generate_beta_distribution(self):
        """
        This method is used to generate random distance delta from beta distribution.
        It returns the distance delta.
        """
        beta_dist = betavariate(2, 2)
        return beta_dist

    def compute_intersection_metas(self, block_1: pd.Series, block_2: pd.Series)-> tuple:
        """
        This method is used to compute the intersection metas between two bboxes.

        Parameters:

            block_1 : pd.Series
                The first bbox.
            block_2 : pd.Series
                The second bbox.

        Returns:
        --------
        
        intersection_width : float
            The width of the intersection block.
        intersection_height : float
            The height of the intersection block.
        intersection_area : float
            The area of the intersection block.
        intersection_block : list
            The intersection block.
        """

        intersection_block = [max(block_1['x0'], block_2['x0']), 
                            max(block_1['y0'], block_2['y0']), 
                            min(block_1['x1'], block_2['x1']), 
                            min(block_1['y1'], block_2['y1'])]

        intersection_width = intersection_block[2] - intersection_block[0]
        intersection_height = intersection_block[3] - intersection_block[1]
        intersection_area = intersection_width * intersection_height

        return intersection_width, intersection_height, intersection_area, intersection_block

    def compute_bbox_area(self, block_1: pd.Series, block_2: pd.Series)-> float:
        """
        This method is used to compute the area of two bounding boxes.

        Returns:
        --------

        block_1_width : float
            The width of the block_1.
        block_1_height : float
            The height of the block_1.
        block_2_width : float
            The width of the block_2.
        block_2_height : float
            The height of the block_2.
        block_1_area : float
            The area of the block_1.
        block_2_area : float 
            The area of the block_2.
        """
        
        block_1_width = block_1['x1'] - block_1['x0']
        block_1_height = block_1['y1'] - block_1['y0']

        block_2_width = block_2['x1'] - block_2['x0']
        block_2_height = block_2['y1'] - block_2['y0']

        block_1_area = block_1_width * block_1_height
        block_2_area = block_2_width * block_2_height
        return block_1_width, block_1_height, block_2_width, block_2_height, block_1_area, block_2_area

    def verify_overlap(self, block_1: pd.Series, block_2: pd.Series)-> bool:
        """
        This method is used to verify if two bounding boxes are overlapped.
        """

        is_overlap = not(block_1['x1'] < block_2['x0'] or 
                    block_1['x0'] > block_2['x1'] or 
                    block_1['y1'] < block_2['y0'] or 
                    block_1['y0'] > block_2['y1'])
        return is_overlap
    
    def get_relative_position(self, block_1: pd.Series, block_2: pd.Series)-> str:
        """
        This method is used to get the relative position between two bounding boxes in 2D space.
        """

        is_overlap = self.verify_overlap(block_1, block_2)

        if not is_overlap:
            return "no overlap"

        else:
            if block_1['x0'] <= block_2['x0'] and block_1['x1'] >= block_2['x1'] and block_1['y0'] <= block_2['y0'] and block_1['y1'] >= block_2['y1']:
                return "b1 completely overlapping b2"

            elif block_2['x0'] <= block_1['x0'] and block_2['x1'] >= block_1['x1'] and block_2['y0'] <= block_1['y0'] and block_2['y1'] >= block_1['y1']:
                return "b2 completely overlapping b1"

            elif block_1['x1'] >= block_2['x0'] and block_1['x0'] <= block_2['x1'] and block_1['y1'] >= block_2['y0'] and block_1['y0'] <= block_2['y1']:
                return "b1 partially overlapping b2"

    def determine_overlap_side(self, block_1: pd.Series, block_2: pd.Series)-> str:
        """
        This method is used to determine the overlap side between two bboxes partially overlapped.
        """

        block_1_center = [(block_1['x0'] + block_1['x1'])/2, (block_1['y0'] + block_1['y1'])/2]
        block_2_center = [(block_2['x0'] + block_2['x1'])/2, (block_2['y0'] + block_2['y1'])/2]

        position = self.get_relative_position(block_1, block_2)
        if position == "no overlap":
            return "no overlap"

        if position == "b1 partially overlapping b2":
            if block_1_center[0] < block_2_center[0]:
                position_in_x = "left"

            elif block_1_center[0] > block_2_center[0]:
                position_in_x = "right"

            else:
                position_in_x = "center"
            
            if block_1_center[1] < block_2_center[1]:
                position_in_y = "top"

            elif block_1_center[1] > block_2_center[1]:
                position_in_y = "bottom"

            else:
                position_in_y = "center"
                                        
            return f"b1 partially overlapping b2 on {position_in_x} {position_in_y} corner"

        elif position == "b1 completely overlapping b2":
            return "b1 completely overlapping b2"
        
        elif position == "b2 completely overlapping b1":
            return "b2 completely overlapping b1"
        
        else:
            raise ValueError("The relative position between block_1 and block_2 is not defined. Please check the relative position between block_1 and block_2.")

    def treat_b1_completely_overlapping_b2(self, block_1_area: float, block_2_area: float, block_1: pd.Series, block_2: pd.Series)-> list:
        """
        This method is used to treat the case where block_1 is completely overlapping block_2.
        """
        
        row_to_drop = []
        if block_1_area > block_2_area:
            row_to_drop.append(block_2.name)
            return row_to_drop
        elif block_1_area < block_2_area:
            row_to_drop.append(block_1.name)
            return row_to_drop
        else:
            row_to_drop.append(block_2.name)
            return row_to_drop
        
    def treat_b2_completely_overlapping_b1(self, block_1_area: float, block_2_area: float, block_1: pd.Series, block_2: pd.Series)-> list:
        """
        This method is used to treat the case where block_2 is completely overlapping block_1.
        """
        row_to_drop = []
        if block_1_area > block_2_area:
            row_to_drop.append(block_2.name)
            return row_to_drop
        elif block_1_area < block_2_area:
            row_to_drop.append(block_1.name)
            return row_to_drop
        else:
            row_to_drop.append(block_1.name)
            return row_to_drop

    def treat_b1_partially_overlapping_b2_on_left_top_corner(self, block_1: pd.Series, 
                                                             block_2: pd.Series, 
                                                             intersection_area: float, 
                                                             intersection_width: float, 
                                                             intersection_height: float, 
                                                             block_1_area: float, 
                                                             block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the left top corner.
        """

        if intersection_area == 0:
                if block_1_area >= block_2_area:
                    distance_delta = self.generate_random_distance_delta()
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-distance_delta)}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+distance_delta, block_2['x1'], block_2['y1'])}
            
        else:
            if block_1_area >= block_2_area:
                if intersection_width >= intersection_height:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-computed_distance)}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1']-computed_distance, block_1['y1'])}
            
            else:
                if intersection_width >= intersection_height:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+computed_distance, block_2['x1'], block_2['y1'])}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_2":self.create_new_block(block_2['x0']+computed_distance, block_2['y0'], block_2['x1'], block_2['y1'])}

    def treat_b1_partially_overlapping_b2_on_right_top_corner(self, block_1: pd.Series,
                                                            block_2: pd.Series,
                                                            intersection_area: float,
                                                            intersection_width: float,
                                                            intersection_height: float,
                                                            block_1_area: float,
                                                            block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the right top corner.
        """

        if intersection_area == 0:
                if block_1_area >= block_2_area:
                    distance_delta = self.generate_random_distance_delta()
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'],  block_1['x1'], block_1['y1']-distance_delta)}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+distance_delta, block_2['x1'], block_2['y1'])}
            
        else:
            if block_1_area >= block_2_area:
                if intersection_width >= intersection_height:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-computed_distance)}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0']+computed_distance, block_1['y0'], block_1['x1'], block_1['y1'])}
            
            else:
                if intersection_width >= intersection_height:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+computed_distance, block_2['x1'], block_2['y1'])}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1']-computed_distance, block_2['y1'])}
    
    def treat_b1_partially_overlapping_b2_on_left_bottom_corner(self, block_1: pd.Series,
                                                                block_2: pd.Series,
                                                                intersection_area: float,
                                                                intersection_width: float,
                                                                intersection_height: float,
                                                                block_1_area: float,
                                                                block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the left bottom corner.
        """
        if intersection_area == 0:
            if block_1_area >= block_2_area: # block 1 is bigger than block 2
                distance_delta = self.generate_random_distance_delta()
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0']+distance_delta, block_1['x1'], block_1['y1'])}
            else: # block 2 is bigger than block 1  
                distance_delta = self.generate_random_distance_delta()
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1'], block_2['y1']-distance_delta)}
            
        else:
            if block_1_area >= block_2_area: # block 1 is bigger than block 2
                if intersection_width >= intersection_height: # intersection width is bigger than intersection height
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0']+computed_distance, block_1['x1'], block_1['y1'])}
                else: # intersection height is bigger than intersection width
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1']-computed_distance, block_1['y1'])}
            
            else: # block 2 is bigger than block 1
                if intersection_width >= intersection_height: # intersection width is bigger than intersection height
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1'], block_2['y1']-computed_distance)}
                else: # intersection height is bigger than intersection width
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0']+computed_distance, block_2['y0'], block_2['x1'], block_2['y1'])}

    def treat_b1_partially_overlapping_b2_on_right_bottom_corner(self, block_1: pd.Series,
                                                                block_2: pd.Series,
                                                                intersection_area: float,
                                                                intersection_width: float,
                                                                intersection_height: float,
                                                                block_1_area: float,
                                                                block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the right bottom corner.
        """
        if intersection_area == 0:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0']+distance_delta, block_1['x1'], block_1['y1'])}
            else:
                distance_delta = self.generate_random_distance_delta()
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1'], block_2['y1']-distance_delta)}
        else:
            if block_1_area >= block_2_area:
                if intersection_width >= intersection_height:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0'], block_1['y0']+computed_distance, block_1['x1'], block_1['y1'])}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_1": self.create_new_block(block_1['x0']+computed_distance, block_1['y0'], block_1['x1'], block_1['y1'])}
            else:
                if intersection_width >= intersection_height:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_height + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1'], block_2['y1']-computed_distance)}
                else:
                    distance_delta = self.generate_random_distance_delta()
                    computed_distance = intersection_width + distance_delta
                    return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1']-computed_distance, block_2['y1'])}
    
    def treat_b1_partially_overlapping_b2_on_center_top_corner(self, block_1: pd.Series,
                                                                block_2: pd.Series,
                                                                intersection_area: float,
                                                                intersection_width: float,
                                                                intersection_height: float,
                                                                block_1_area: float,
                                                                block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the center top corner.
        """
        
        if intersection_area == 0:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-distance_delta)}
            else:
                distance_delta = self.generate_random_distance_delta()
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+distance_delta, block_2['x1'], block_2['y1'])}
        else:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_height + distance_delta
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-computed_distance)}
            else:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_height + distance_delta
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+computed_distance, block_2['x1'], block_2['y1'])}

    def treat_b1_partially_overlapping_b2_on_center_bottom_corner(self, block_1: pd.Series,
                                                                    block_2: pd.Series,
                                                                    intersection_area: float,
                                                                    intersection_width: float,
                                                                    intersection_height: float,
                                                                    block_1_area: float,
                                                                    block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the center bottom corner.
        """

        if intersection_area == 0:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0']+distance_delta, block_1['x1'], block_1['y1'])}
            else:
                distance_delta = self.generate_random_distance_delta()
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1'], block_2['y1']-distance_delta)}
        else:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_height + distance_delta
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0']+computed_distance, block_1['x1'], block_1['y1'])}
            else:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_height + distance_delta
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0'], block_2['x1'], block_2['y1']-computed_distance)}

    def treat_b1_partially_overlapping_b2_on_left_center_corner(self, block_1: pd.Series,
                                                                block_2: pd.Series,
                                                                intersection_area: float,
                                                                intersection_width: float,
                                                                intersection_height: float,
                                                                block_1_area: float,
                                                                block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the left center corner.
        """

        if intersection_area == 0:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1']-distance_delta, block_1['y1'])}
            else:
                distance_delta = self.generate_random_distance_delta()
                return {"block_2": self.create_new_block(block_2['x0']+distance_delta, block_2['y0'], block_2['x1'], block_2['y1'])}
        else:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_width + distance_delta
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1']-computed_distance, block_1['y1'])}
            else:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_width + distance_delta
                return {"block_2": self.create_new_block(block_2['x0']+computed_distance, block_2['y0'], block_2['x1'], block_2['y1'])}
    
    def treat_b1_partially_overlapping_b2_on_center_center_corner(self, block_1: pd.Series,
                                                                    block_2: pd.Series,
                                                                    intersection_area: float,
                                                                    intersection_width: float,
                                                                    intersection_height: float,
                                                                    block_1_area: float,
                                                                    block_2_area: float)-> dict:
        """
        This method is used to treat the case where block_1 is partially overlapping block_2 on the center center corner.
        """

        if intersection_area == 0:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-distance_delta)}
            else:
                distance_delta = self.generate_random_distance_delta()
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+distance_delta, block_2['x1'], block_2['y1'])}
        else:
            if block_1_area >= block_2_area:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_height + distance_delta
                return {"block_1": self.create_new_block(block_1['x0'], block_1['y0'], block_1['x1'], block_1['y1']-computed_distance)}
            else:
                distance_delta = self.generate_random_distance_delta()
                computed_distance = intersection_height + distance_delta
                return {"block_2": self.create_new_block(block_2['x0'], block_2['y0']+computed_distance, block_2['x1'], block_2['y1'])}  

    def create_new_block(self, x0, y0, x1, y1):
        """
        This method is used to create a new block.
        """

        new_block = {'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
        return new_block
    
    def choose_action_for_overlap_case(self, block_1: pd.Series, block_2: pd.Series):
        """
        This method is used to correct the overlap between two bboxes.
        """

        position = self.determine_overlap_side(block_1, block_2)
        #print(position)
        intersection_width, intersection_height, intersection_area, _ = self.compute_intersection_metas(block_1, block_2)
        _, _, _, _, block_1_area, block_2_area = self.compute_bbox_area(block_1, block_2)
        
        if position == "no overlap":
            return "no overlap"

        if position == "b1 completely overlapping b2":
            #print(position)
            return self.treat_b1_completely_overlapping_b2(block_1_area, block_2_area, block_1, block_2)#-> list

        elif position == "b2 completely overlapping b1":
            #print(position)
            return self.treat_b2_completely_overlapping_b1(block_1_area, block_2_area, block_1, block_2)#-> list
       
        elif position == "b1 partially overlapping b2 on left top corner":
            return self.treat_b1_partially_overlapping_b2_on_left_top_corner(block_1, 
                                                                             block_2, 
                                                                             intersection_area, 
                                                                             intersection_width, 
                                                                             intersection_height, 
                                                                             block_1_area, 
                                                                             block_2_area)

        elif position == "b1 partially overlapping b2 on right top corner":
            return self.treat_b1_partially_overlapping_b2_on_right_top_corner(block_1,
                                                                                block_2,
                                                                                intersection_area,
                                                                                intersection_width,
                                                                                intersection_height,
                                                                                block_1_area,
                                                                                block_2_area)
    
        elif position == "b1 partially overlapping b2 on left bottom corner":
            return self.treat_b1_partially_overlapping_b2_on_left_bottom_corner(block_1,
                                                                                block_2,
                                                                                intersection_area,
                                                                                intersection_width,
                                                                                intersection_height,
                                                                                block_1_area,
                                                                                block_2_area)

        elif position == "b1 partially overlapping b2 on right bottom corner":
            return self.treat_b1_partially_overlapping_b2_on_right_bottom_corner(block_1,
                                                                                block_2,
                                                                                intersection_area,
                                                                                intersection_width,
                                                                                intersection_height,
                                                                                block_1_area,
                                                                                block_2_area)
                
        elif position == "b1 partially overlapping b2 on center top corner":
            return self.treat_b1_partially_overlapping_b2_on_center_top_corner(block_1,
                                                                                block_2,
                                                                                intersection_area,
                                                                                intersection_width,
                                                                                intersection_height,
                                                                                block_1_area,
                                                                                block_2_area)
        
        elif position == "b1 partially overlapping b2 on center bottom corner":
            return self.treat_b1_partially_overlapping_b2_on_center_bottom_corner(block_1,
                                                                                    block_2,
                                                                                    intersection_area,
                                                                                    intersection_width,
                                                                                    intersection_height,
                                                                                    block_1_area,
                                                                                    block_2_area)
        
        elif position == "b1 partially overlapping b2 on center center corner":
            return self.treat_b1_partially_overlapping_b2_on_center_center_corner(block_1,
                                                                                block_2,
                                                                                intersection_area,
                                                                                intersection_width,
                                                                                intersection_height,
                                                                                block_1_area,
                                                                                block_2_area)
        
        elif position == "b1 partially overlapping b2 on left center corner":
            return self.treat_b1_partially_overlapping_b2_on_left_center_corner(block_1,
                                                                                block_2,
                                                                                intersection_area,
                                                                                intersection_width,
                                                                                intersection_height,
                                                                                block_1_area,
                                                                                block_2_area)
        
        else:
            #print(position)
            warnings.warn("The relative position between block_1 and block_2 is not defined. Please check the relative position between block_1 and block_2.")

    def remove_overlap(self):
        """
        This method is used to remove the overlap between the bboxes.
        """

        if self.config["Post_process_to_remove_overlap"]["should_perform"]:
            output_dataframe_list = []
            row_to_drop = []

            dataframe_list = self.create_dataframe()
            print(f'Removing overlap process started...')
            for dataframe in dataframe_list:
                dataframe = deepcopy(dataframe)

                for i in range(len(dataframe)):
                    block_1 = dataframe.iloc[i] #first bbox
                    for j in range(i+1, len(dataframe)):
                        block_2 = dataframe.iloc[j] #second bbox

                        new_block = self.choose_action_for_overlap_case(block_1, block_2)
                        if new_block == "no overlap":
                            continue
                        else:
                            #print(f"new_block: {new_block}")
                            if isinstance(new_block, dict):
                                for key, value in new_block.items():
                                    if key == "block_1":
                                        #print(f"block_1: {value}")
                                        #print(value)
                                        if value['x0'] >= value['x1'] or value['y0'] >= value['y1']:
                                            row_to_drop.append(i)
                                        dataframe.loc[i, ['x0', 'y0', 'x1', 'y1']] = value
                                        block_1 = dataframe.iloc[i]
                                    elif key == "block_2":
                                        #print(f"block_2: {value}")
                                        #print(value)
                                        if value['x0'] >= value['x1'] or value['y0'] >= value['y1']:
                                            row_to_drop.append(j)
                                        dataframe.loc[j, ['x0', 'y0', 'x1', 'y1']] = value
                                        block_2 = dataframe.iloc[j]
                                    else:
                                        raise ValueError("The key is not defined. Please check the key.")
                                    
                            elif isinstance(new_block, list):
                                #print(f"new_block_to_drop: {new_block}")
                                row_to_drop.extend(new_block)
                            else:
                                pass
                dataframe = dataframe.drop(row_to_drop, axis=0)
                row_to_drop = []
                        #break
                output_dataframe_list.append(dataframe)
                #break
            print(f'Removing overlap process finished...')
            reconstructed_data = self.reconstruct_normal_format(output_dataframe_list)
            self.create_image_after_correction(reconstructed_data, type_of_format='PNG')
            self.convert_to_json(reconstructed_data)
            #return output_dataframe_list    
        
        else:
            warnings.warn(f"Dear user, you have chosen not to perform the post-processing to remove the overlap between the bounding boxes by setting the should_perform parameter to False.")
    
    def reconstruct_normal_format(self, corrected_dataframe: list[pd.DataFrame]) -> list[dict]:
        """
        This method is used to reconstruct the corrected dataframe on the original format.
        Basically, the original format is a list of dictionaries. Where each dictionary is a corrected file. Layout without overlap.

        Parameters:
            corrected_dataframe : list[pd.DataFrame]
                The corrected dataframe.

        Returns:
        --------
        reconstructed_data : list[dict]
            The reconstructed data.
        """
        
        reconstructed_data = []
        for dataframe in corrected_dataframe:
            content = []
            dataframe_to_array = dataframe.values
            
            for element in dataframe_to_array:
                liste = [list(element[0:4]), element[-2]]
                content.append(liste)
            correpsonding_file_name = element[-1]
            dico = {'bodymodule': content,
                    'corresponding_file_name': correpsonding_file_name}
            reconstructed_data.append(dico)
        return reconstructed_data
    
    def create_image_after_correction (self, 
                                       reconstructed_data: list[dict],
                                       type_of_format: str):
        """
        This method is used to create new images after the correction of the overlapped bboxes.
        """
        #enter_format = self.reconstruct_normal_format
        
        path = os.path.join(self.reconstruct_image_path, f'Reconstructed_images')
        if os.path.exists(path):
            print(f"The directory {path} already exists. I will delete it and create a new one.")
            shutil.rmtree(path)
        os.makedirs(path)

        for _, dico in enumerate(reconstructed_data):
            img = Image.new('RGB', (1200, 1600), color = (255, 255, 255))
            draw = ImageDraw.Draw(img, 'RGB')
            scale_factor_x = 1200/256
            scale_factor_y = 1600/256

            for liste in dico['bodymodule']:
                x0, y0, x1, y1 = liste[0]
                type_of_bbox = liste[1]
                rectangle_coords = [x0*scale_factor_x, 
                                    y0*scale_factor_y, 
                                    x1*scale_factor_x, 
                                    y1*scale_factor_y]
                
                if type_of_bbox == "text":
                    color_to_fill = "#32CD32" # green
                elif type_of_bbox == "title":
                    color_to_fill = "#FF5733" # orange
                elif type_of_bbox == "table":
                    color_to_fill = "#C70039" # red
                elif type_of_bbox == "figure":
                    color_to_fill = "#900C3F" # purple
                elif type_of_bbox == "list":
                    color_to_fill = "#FFFF00" # yellow

                draw.rectangle(rectangle_coords, fill=color_to_fill, outline=color_to_fill)
            img.save(path + f"/{dico['corresponding_file_name']}", type_of_format)
            
            #img.save(os.path.join(self.reconstruct_image_path, dico["corresponding_file_name"]), type_of_format)

    def convert_to_json(self, reconstructed_data: list[dict]):
        """
        This method is used to convert the corrected dataframe to json files.
        This converted json files are used as input for content generator.

        Returns:
        --------
        json_files : list[str]
            The list of json files.
        """

        path = os.path.join(self.reconstruct_image_path, f'Reconstructed_json_files')
        if os.path.exists(path):
            print(f"The directory {path} already exists. I will delete it and create a new one.")
            shutil.rmtree(path)
        os.makedirs(path)

        scale_factor_x = 1200/256
        scale_factor_y = 1600/256
        for element in reconstructed_data:
            file_content = element['bodymodule']
            file_name = element['corresponding_file_name']
            holder_list = []
            
            for liste in file_content:
                if liste[1] == "figure":
                    liste[1] = "image"
                
                x0, y0, x1, y1 = liste[0]
                holder = [[(x0*scale_factor_x)/1200, 
                        (y0*scale_factor_y)/1600, 
                        (x1*scale_factor_x)/1200, 
                        (y1*scale_factor_y)/1600],
                        liste[1]]
                
                holder_list.append(holder)
            dico = {'bodymodule': holder_list}
            with open(path + f"/{file_name.split('.')[0]}.json", 'w') as json_file:
                json.dump(dico, json_file)