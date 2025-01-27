import os
import cv2
import json
import shutil
from glob import glob

def crop_regions(dataset_name: str,
                 image_folder_path: str,
                 image_extension: str,
                 annotation_folder_path: str,
                 output_folder_path: str,
                 desired_output_folder_name: str) -> None:
    """
    This function is used to crop the regions within image and save them in a folder.
    Also it will arrange the cropped images in subfolders according to their types representing then the IMAGENET format.

    Args:
        - dataset_name (str): The dataset name. Can be either 'publaynet' , doclyanet, docbank.
        - image_folder_path (str): The path to the image folder.
        - image_extension (str): The image extension. Can be either 'jpg' or 'png'.
        - annotation_folder_path (str): The path to the annotation folder.
        - output_folder_path (str): The path to the output folder.
        - desired_output_folder_name (str): The desired output folder name.

    Returns:  
        - None. However, it saves the cropped images in the output folder.
    """

    list_images_path = sorted(glob(os.path.join(image_folder_path, f"*.{image_extension}")))
    list_annotations_path = sorted(glob(os.path.join(annotation_folder_path, '*.json')))
    _output_folder_path = os.path.join(output_folder_path, desired_output_folder_name)
    manage_folder(_output_folder_path)

    if dataset_name == 'publaynet':
        subtypes_paths = {1: os.path.join(_output_folder_path, 'text'),
                            2: os.path.join(_output_folder_path, 'title'),
                            3: os.path.join(_output_folder_path, 'list'),
                            4: os.path.join(_output_folder_path, 'table'),
                            5: os.path.join(_output_folder_path, 'figure')}
    elif dataset_name == 'doclyanet':
        subtypes_paths = {10: os.path.join(_output_folder_path, 'text'),
                            11: os.path.join(_output_folder_path, 'title'),
                            4: os.path.join(_output_folder_path, 'list'),
                            9: os.path.join(_output_folder_path, 'table'),
                            7: os.path.join(_output_folder_path, 'figure')}
    elif dataset_name == 'docbank':
        # TO DO
        pass
    else:
        raise ValueError(f'The dataset name {dataset_name} is not valid. Please provide a valid dataset name between publaynet, doclyanet and docbank.')
    
    for path in subtypes_paths.values():
        manage_folder(path)
    
    i = 1
    for img_path, ann_path in zip(list_images_path, list_annotations_path):
        list_coords = []
        list_subtypes = []

        with open(ann_path, 'r') as json_file:
            coords = json.load(json_file)
            name = [key for key in coords.keys()]

            for data in coords[name[0]]:
                list_coords.append(data['bbox'])
                list_subtypes.append(data['category_id'])

        image = cv2.imread(img_path)
        if image is None:
            raise Exception(f'The image {img_path} could not be read. Please check the image path.')
        
        height, width = image.shape[:2]
        for coord, subtype in zip(list_coords, list_subtypes):
            x, y, w, h = (int(round(coord[0])), 
                          int(round(coord[1])), 
                          int(round(coord[2])), 
                          int(round(coord[3])))
            x_end, y_end = x + w, y + h
            x, y = max(0, x), max(0, y)
            x_end, y_end = min(width, x_end), min(height, y_end)

            if x >= x_end or y >= y_end:
                print(f'The coordinates {coord} are not valid. Please check the coordinates.')
                continue
            crop = image[y:y_end, x:x_end]
            
            if subtype not in subtypes_paths:
                print(f'The subtype {subtype} is not valid. Please check the subtype.')
                continue    
            image_name = ".".join(os.path.basename(img_path).split('.')[:-1])
            write_image (i, image_name, subtypes_paths[subtype], crop)
            i += 1

def manage_folder(folder: str) -> None:
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

def write_image(i: int, image_name: str, path: str, crop) -> None:
    """
    This function is used to write the image in the folder.

    Args:
        i (int): The image index.
        image_name (str): The image name.
        path (str): The path to save the image.
        crop : The cropped image.

    Returns:
        None. However, it saves the cropped image in the folder.
    """
    cv2.imwrite(os.path.join(path, f'{image_name}_{i}.jpg'), crop)

