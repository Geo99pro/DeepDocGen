import os
import cv2
import json
import shutil
from glob import glob

def crop_regions(images_folder_path: str,
                 annotation_folder_path: str,
                 path_to_save_cropped_images: str,
                 which_public_dataset: str)-> None:
    """
    This function crops the regions of the images based on the annotation files.
    Basically, in this case the datasets used for this purpose are :
    1- PublyaNet
    2- DoclyaNet
    3- DocBank

    NB: Actually this funtion only considers the 4 classes which are: 
    1- text
    2- title
    3- list 
    4- table 
    5- figure

    Args:
        - images_folder_path (str): The path to the folder containing the images.
        - annotation_folder_path (str): The path to the folder containing the annotations.
        - path_to_save_cropped_images (str): The path to save the cropped images.
        - which_public_dataset (str): The public dataset name. It can be either 'publyanet', 'doclyanet', or 'docbank'.

    Returns:
        - None. However, it saves the cropped images in the path provided by the user in the ImageNet format.
    """
    
    list_images_paths = sorted(glob(os.path.join(images_folder_path, '*.png')))
    list_annotation_paths = sorted(glob(os.path.join(annotation_folder_path, '*.json')))

    manage_folder(path_to_save_cropped_images)

    if which_public_dataset == 'publyanet':
        subtypes_paths = {
            1: os.path.join(path_to_save_cropped_images, 'text'),
            2: os.path.join(path_to_save_cropped_images, 'title'),
            3: os.path.join(path_to_save_cropped_images, 'list'),
            4: os.path.join(path_to_save_cropped_images, 'table'),
            5: os.path.join(path_to_save_cropped_images, 'figure'),
        }
    elif which_public_dataset == 'doclyanet':
        subtypes_paths = {
            10: os.path.join(path_to_save_cropped_images, 'text'),
            11: os.path.join(path_to_save_cropped_images, 'title'),
            4: os.path.join(path_to_save_cropped_images, 'list'),
            9: os.path.join(path_to_save_cropped_images, 'table'),
            7: os.path.join(path_to_save_cropped_images, 'figure'),
        }
    elif which_public_dataset == 'docbank':
        #TO DO
        pass
    else:
        raise ValueError('The public dataset name is not valid. It should be either "publyanet", "doclyanet", or "docbank".')
    
    i = 1
    for image_path, annotation_path in zip(list_images_paths, list_annotation_paths):
        list_coordinates = []
        list_subtypes = []

        with open(annotation_path, 'r') as file:
            coords = json.load(file)
            name = [key for key in coords.keys()]

            for data in coords[name[0]]:
                list_coordinates.append(data['bbox'])
                list_subtypes.append(data['category_id'])
        
        image = cv2.imread(image_path)
        if image is None:
            print(f'Error: Impossible to load/read the image {image_path}. Please check the path.')
            continue

        height, width = image.shape[:2]

        for coord, subtype in zip(list_coordinates, list_subtypes):
            x, y, w, h = (int(round(coord[0])),
                            int(round(coord[1])),
                            int(round(coord[2])),
                            int(round(coord[3])))
            x_end, y_end = x + w, y + h
            x, y = max(0, x), max(0, y)
            x_end, y_end = min(width, x_end), min(height, y_end)

            if x >= x_end or y >= y_end:
                print(f'Error: Invalid crop for the picture {image_path} with the coordinates ({x}, {y}, {w}, {h}).')
                continue
            
            crop = image[y:y_end, x:x_end]

            if subtype not in subtypes_paths:
                print(f'Error: The subtype {subtype} is not in the list of subtypes.')
                continue

            image_name = os.path.splitext(os.path.basename(image_path))[0]
            write_image(i, image_name, subtypes_paths[subtype], crop)
            i += 1

def manage_folder(path: str)-> None:
    """
    This function manages the folder by deleting it if it already exists and creating a new one.

    Args:
        - path (str): The path to the folder.

    Returns:
        - None. However, it creates a folder.
    """
    if os.path.exists(path):
        print(f'Dear User, The folder {path} already exists. I will delete it and create a new one.')
        shutil.rmtree(path)
    os.makedirs(path)

def write_image(i: int,
                image_name: str,
                path: str,
                crop)-> None:
    """
    This function writes the image in the specified folder.

    Args:
        - i (int): The index of the image.
        - image_name (str): The name of the image.
        - path (str): The path to the folder.
        - crop (np.array): The cropped image.

    Returns:
        - None. However, it saves the cropped image.
    """
    cv2.imwrite(os.path.join(path, f'{image_name}_{i}.png'), crop)