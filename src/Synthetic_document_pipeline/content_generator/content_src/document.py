import os
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET


from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config, Size
from src.Synthetic_document_pipeline.content_generator.content_src.config.enums import FigureType
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import TYPESDICT
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import get_random_image_file
from copy import copy as copy

class Document():
    def __init__(self, image_path, size: Size, color='white', save_mask=False):
        path = os.path.splitext(image_path)[0]
        self.im_path = image_path
        self.xml_path = path + ".xml"
        self.size = size
        self.save_mask = save_mask
        self.image = Image.new('RGBA', size.to_tuple(), color)
        self.draw = ImageDraw.Draw(self.image)
    
    def save(self, blocks):
        self.generate_xml(blocks, self.xml_path)
        self.image.save(self.im_path)
    
    def paste(self, coords, figure_type: FigureType, image=None):
        """
        This function pastes a randomly chosen image, or the provided image, inside a specified bounding box (bbox).

        Args:
        - coords (BoundingBox): The bounding box coordinates where the image will be pasted.
        - figure_type (FigureType): The type of figure to determine the image to be pasted.
        - image (PIL.Image.Image, optional): The image to be pasted. If not provided, a random image will be selected.

        Returns:
        BoundingBox: The updated bounding box coordinates after pasting the image.
        """
        if image is None:
            image = get_random_image_file(Config.image_dict, figure_type.name.lower())

        coords=(coords)
        
        resized_figure = image.resize((int(coords.width-1) , int(coords.height-1)))
        self.image.paste(resized_figure, (int(coords.x0+1), int(coords.y0+1)))
        return coords
    
    @staticmethod
    def generate_xml(blocks: list, xml_fullpath:str):
        doc = ET.Element("doc")
        blocks_for_xml = {i: [block.x0, block.y0, block.x1, block.y1, block.subtype, {}]\
                            if block.type != "text" else \
                            [block.x0, block.y0, block.x1, block.y1, block.subtype, block.text_dictionary] \
                            for i, block in enumerate(blocks)}
        for x0, y0, x1, y1, bsubtype, text_dictionary in blocks_for_xml.values():
            btype = TYPESDICT.get(bsubtype, '')
            block_subelement = ET.SubElement(doc, "block", type=btype, subtype=bsubtype, 
                                            x0=str(x0), y0=str(y0), x1=str(x1), y1=str(y1))
            for line, textitem in text_dictionary.items():
                line_subelement = ET.SubElement(block_subelement, "line", 
                                                    x0=str(textitem['x0']), y0=str(textitem['y0']), 
                                                    x1=str(textitem['x1']), y1=str(textitem['y1']))
                line_subelement.text = textitem['bullet_out_of_line'] + textitem['text']
                

        tree = ET.ElementTree(doc)
        tree.write(xml_fullpath)
        return xml_fullpath
        