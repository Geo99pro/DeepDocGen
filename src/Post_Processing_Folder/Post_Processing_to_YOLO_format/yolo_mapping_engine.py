import os
import json
import shutil
from glob import glob
from sklearn.model_selection import train_test_split
from src.Post_Processing_Folder.Document_Dataset_Cropper.dataset_region_cropper import manage_folder

def convert_coco_to_yolo(annotations_folder_path: str, output_folder_path: str, desired_folder_name: str) -> None:
    """
    This function is used to convert document annotation in COCO format to YOLO format.

    Args:
        - annotations_folder_path (str): The path to the folder containing document annotations in COCO format.
        - output_folder_path (str): The path to save the converted annotations in YOLO format.
        - desired_folder_name (str): The name of the folder to save the converted annotations.
    """

    list_annotations_coco = glob(os.path.join(annotations_folder_path, "*.json"))
    _output_folder_path = os.path.join(output_folder_path, desired_folder_name)
    manage_folder(_output_folder_path)

    for doc_anno in list_annotations_coco:
        with open(doc_anno, "r") as file:
            data = json.load(file)

        if 'image' not in data or 'annotations' not in data:
            raise ValueError("The annotation file must contain 'image' and 'annotations' keys. Remember that the annotation file must be in COCO format.")

        image_metas = data['image']
        width, height = image_metas['width'], image_metas['height']
        file_name = os.path.splitext(image_metas['file_name'])[0]
        
        yolo_file_path = os.path.join(_output_folder_path, f'{file_name}.txt')
        if os.path.exists(yolo_file_path):
            os.remove(yolo_file_path)

        for anno_bloc in data['annotations']:
            #since yolo start it annotation from 0, we need to subtract 1 from the category_id if it is greater than 0
            class_id = anno_bloc['category_id'] - 1 if anno_bloc['category_id'] > 0 else 0

            bbox = anno_bloc['bbox']
            #convert the bbox to yolo format and normalize it
            center_x_norma = (bbox[0] + bbox[2] / 2) / width
            center_y_norma = (bbox[1] + bbox[3] / 2) / height
            width_norma = bbox[2] / width
            height_norma = bbox[3] / height

            with open(yolo_file_path, "a") as yolofile:
                yolofile.write(f"{class_id} {center_x_norma:.6f} {center_y_norma:.6f} {width_norma:.6f} {height_norma:.6f}\n")
    print(f"The annotations in COCO format have been successfully converted to YOLO format and saved in {output_folder_path}/{desired_folder_name}.")
    return None

def split_dataset(images_folder_path: str, annotations_folder_path, output_folder_path, desired_folder_name: str, test_size: float, random_state: int):
    """
    This function is used to split the dataset into train, validation and test datasets.

    Args:
        - images_folder_path (str): The path to the folder containing images.
        - annotations_folder_path (str): The path to the folder containing annotations in yolo format.
        - output_folder_path (str): The path to save the split datasets.
        - desired_folder_name (str): The name of the folder to save the split datasets.
        - test_size (float): The size of the test dataset.
        - random_state (int): The random state to use when shuffling the data.
    """
    list_images_path = glob(os.path.join(images_folder_path, "*.jpg")) + glob(os.path.join(images_folder_path, "*.png"))
    list_annotations_path = glob(os.path.join(annotations_folder_path, "*.json")) or glob(os.path.join(annotations_folder_path, "*.txt"))

    _output_folder_path = os.path.join(output_folder_path, desired_folder_name)
    train_folder_pictures_path = os.path.join(_output_folder_path, "train_pictures")
    train_folder_annotations_path = os.path.join(_output_folder_path, "train_annotations")
    val_folder_pictures_path = os.path.join(_output_folder_path, "val_pictures")
    val_folder_annotations_path = os.path.join(_output_folder_path, "val_annotations")
    test_folder_pictures_path = os.path.join(_output_folder_path, "test_pictures")
    test_folder_annotations_path = os.path.join(_output_folder_path, "test_annotations")

    manage_folder(train_folder_pictures_path)
    manage_folder(train_folder_annotations_path)
    manage_folder(val_folder_pictures_path)
    manage_folder(val_folder_annotations_path)
    manage_folder(test_folder_pictures_path)
    manage_folder(test_folder_annotations_path)

    train_images, remain_images = train_test_split(list_images_path,
                                                test_size=test_size,
                                                shuffle=True,
                                                random_state=random_state)
    val_images, test_images = train_test_split(remain_images,
                                            test_size=0.5,
                                            shuffle=True,
                                            random_state=random_state)
    print(f"Number of train images: {len(train_images)}")
    print(f"Number of val images: {len(val_images)}")
    print(f"Number of test images: {len(test_images)}")

    copy_multiple_files(train_images, train_folder_pictures_path)
    copy_multiple_files(val_images, val_folder_pictures_path)
    copy_multiple_files(test_images, test_folder_pictures_path)

    get_correct_annotation_file(train_images, list_annotations_path, train_folder_annotations_path)
    get_correct_annotation_file(val_images, list_annotations_path, val_folder_annotations_path)
    get_correct_annotation_file(test_images, list_annotations_path, test_folder_annotations_path)

def copy_multiple_files(data: list, destination_folder: str) -> None:
    """
    This function is used to copy multiple files to a destination folder.

    Args:
        - data (list): The list of files to copy.
        - destination_folder (str): The path to the destination folder.
    """
    for each_file in data:
        shutil.copy(each_file, destination_folder)
    return None

def copy_simple_file(file: str, destination_folder: str) -> None:
    """
    This function is used to copy a single file to a destination folder.

    Args:
        - file (str): The file to copy.
        - destination_folder (str): The path to the destination folder.
    """
    shutil.copy(file, destination_folder)
    return None

def get_file_names_without_extension(list_paths: list[str])-> list[str]:
    """
    This function is used to get the names of files without their extensions.

    Args:
        - list_paths (list[str]): The list of file paths.

    Returns:
        - list[str]: The list of file names without their extensions.
    """
    return [".".join(os.path.basename(file).split(".")[:-1]) for file in list_paths]

def get_correct_annotation_file(data: list, list_annotations: list, destination: str)-> None:
    """
    This function is used to get the correct annotation file for each image and copy it to the destination folder.
    
    Args:
        - data (list): The list of images. train_images, val_images or test_images.
        - list_annotations (list): The list of annotations.
        - destination (str): The path to the destination folder.

    Returns:
        - None.
    """

    list_data_name = get_file_names_without_extension(data)
    for each_path in list_annotations:
        current_file_name = ".".join(os.path.basename(each_path).split(".")[:-1])
        if current_file_name in list_data_name:
            copy_simple_file(each_path, destination)
        else:
            raise ValueError(f"The annotation file for the image {current_file_name} is missing.")
    return None 