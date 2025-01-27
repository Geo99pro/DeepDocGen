import os
import PyPDF2
import shutil
from tqdm import tqdm
from glob import glob
from pdf2image import convert_from_path

class PDFImageEngine:
    """
    This class is used to convert the pdfs to images and save them in the specified folder path.

    Attributes:
        pdfs_folder_path (str): is the path to the folder containing the pdfs.
        save_images_dir (str): is the path to the folder to save the images.
        image_format (str): is the desired format of the images. It can be either jpg or png. By default, it is set to png.

    Methods:

        convert_pdf_to_image(self): This function converts the pdfs to images and save them in the specified given folder path.
        get_pdfs_metadata(self): This function gets the metadata of the pdf files. Such as the pdf file name, the number of pages in the pdf file.
    
    """
    def __init__(self,
                 pdfs_folder_path: str, 
                 path_to_save_image: str,
                 desired_folder_name: str, 
                 image_format: str):
        self.pdfs_folder_path = pdfs_folder_path
        self.path_to_save_image = path_to_save_image
        self.desired_folder_name = desired_folder_name
        self.image_format = image_format

    def convert_pdf_to_image(self):
        """
        This function converts the pdfs to images and save them in the specified given folder path.

        Args:
            pdfs_folder_path (str): is the path to the folder containing the pdfs.
            path_to_save_image (str): is the path to the folder where the images will be saved.
            desired_folder_name (str): is the desired folder name to save the images.
            image_format (str): is the desired format of the images. It can be either jpg or png.
        
        Returns:
            image_list_for_embedding_extractor (list): is the list of images path, which will be used by the embedding extractor.
        """
        folder_name = os.path.join(self.path_to_save_image, self.desired_folder_name)
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        os.makedirs(folder_name)

        list_of_pdf_path = glob(os.path.join(self.pdfs_folder_path, '*.pdf'))

        for pdf_path in tqdm(list_of_pdf_path):
            pdf_name = os.path.basename(pdf_path).split('.')[0]
            images = convert_from_path(pdf_path)

            for i, image in enumerate(images):
                if self.image_format == 'jpg':
                    image.save(os.path.join(folder_name, f'{pdf_name}_{i}.jpg'), 'JPEG')
                elif self.image_format == 'png':
                    image.save(os.path.join(folder_name, f'{pdf_name}_{i}.png'), 'PNG')
                else:
                    raise ValueError('The desired image format should be either jpg or png.')

        image_list_for_embedding_extractor = glob(os.path.join(folder_name, f'*.{self.image_format}'))
        return len(list_of_pdf_path), image_list_for_embedding_extractor

    def get_pdfs_metadata(self):
        """
        This function gets the metadata of the pdf files.
        Such as the pdf file name, the number of pages in the pdf file.

        Args:
            pdfs_folder_path (str): is the path to the folder containing the pdfs.
        
        Returns:
            pdf_metadata (list): is the list of dictionaries containing the metadata of the pdf files.
        """

        list_of_pdf_path = glob(os.path.join(self.pdfs_folder_path, '*.pdf'))
        pdf_metadata = []

        for pdf_path in list_of_pdf_path:
            file = open(pdf_path, 'rb')
            reader = PyPDF2.PdfReader(file)
            pdf_metadata.append({'pdf_name': os.path.basename(pdf_path).split('.')[0],
                                'total_pages': len(reader.pages)})
        return pdf_metadata