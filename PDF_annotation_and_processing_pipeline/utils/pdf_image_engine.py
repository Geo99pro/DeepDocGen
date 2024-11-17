import os
import PyPDF2
import timeit
import shutil
from tqdm import tqdm
from glob import glob
from pdf2image import convert_from_path

class PDFImageEngine:
    """
    This class is used to convert the pdfs to images and save them in the specified folder path.

    Attributes:
        pdf_folder_path (str): is the path to the folder containing the pdfs.
        save_images_dir (str): is the path to the folder to save the images.
        desired_image_format (str): is the desired format of the images. It can be either jpg or png. By default, it is set to png.

    Methods:

        convert_pdf_to_image(self): This function converts the pdfs to images and save them in the specified given folder path.
        get_pdfs_metadata(self): This function gets the metadata of the pdf files. Such as the pdf file name, the number of pages in the pdf file.
    
    """
    def __init__(self, pdf_folder_path: str, save_image_path: str, desired_image_format: str):
        self.pdf_folder_path = pdf_folder_path
        self.save_image_path = save_image_path
        self.desired_image_format = desired_image_format

    def convert_pdf_to_image(self):
        """
        This function converts the pdfs to images and save them in the specified given folder path.

        Args:
            pdf_folder_path (str): is the path to the folder containing the pdfs.
            save_images_dir (str): is the path to the folder to save the images.
            desired_image_format (str): is the desired format of the images. It can be either jpg or png.
        
        Returns:
            image_list_for_embedding_extractor (list): is the list of images path, which will be used by the embedding extractor.
        """

        start = timeit.default_timer()
        if not os.path.exists(self.save_image_path):
            os.makedirs(self.save_image_path)
        else:
            print(f'Dear User, The folder with the name {self.save_image_path} already exists. I will delete it and create a new one.')
            shutil.rmtree(self.save_image_path)
            os.makedirs(self.save_image_path)

        list_of_pdf_path = glob(os.path.join(self.pdf_folder_path, '*.pdf'))

        for pdf_path in tqdm(list_of_pdf_path):
            pdf_name = os.path.basename(pdf_path).split('.')[0]
            images = convert_from_path(pdf_path)

            for i, image in enumerate(images):
                if self.desired_image_format == 'jpg':
                    image.save(os.path.join(self.save_image_path, f'{pdf_name}_{i}.jpg'), 'JPEG')
                elif self.desired_image_format == 'png':
                    image.save(os.path.join(self.save_image_path, f'{pdf_name}_{i}.png'), 'PNG')
                else:
                    raise ValueError('The desired image format should be either jpg or png.')

        stop = timeit.default_timer()
        #print(f'Time taken to convert pdfs to images is {(stop-start):.2f} seconds.')

        image_list_for_embedding_extractor = glob(os.path.join(self.save_image_path, f'*.{self.desired_image_format}'))
        return image_list_for_embedding_extractor

    def get_pdfs_metadata(self):
        """
        This function gets the metadata of the pdf files.
        Such as the pdf file name, the number of pages in the pdf file.

        Args:
            pdf_folder_path (str): is the path to the folder containing the pdfs.
        
        Returns:
            pdf_metadata (list): is the list of dictionaries containing the metadata of the pdf files.
        """

        list_of_pdf_path = glob(os.path.join(self.pdf_folder_path, '*.pdf'))
        pdf_metadata = []

        for pdf_path in list_of_pdf_path:
            file = open(pdf_path, 'rb')
            reader = PyPDF2.PdfReader(file)

            pdf_metadata.append({'pdf_name': os.path.basename(pdf_path).split('.')[0],
                                'total_pages': len(reader.pages)})
        return pdf_metadata