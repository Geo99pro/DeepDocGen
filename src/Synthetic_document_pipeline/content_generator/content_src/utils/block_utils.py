import json
import os
from random import randint
import xml.etree.ElementTree as ET
from src.Synthetic_document_pipeline.content_generator.content_src.blocks.coords import Coords
from src.Synthetic_document_pipeline.content_generator.content_src.blocks.imageblock import ImageBlock

from src.Synthetic_document_pipeline.content_generator.content_src.blocks.tableblock import TableBlock
from src.Synthetic_document_pipeline.content_generator.content_src.blocks.textblock import TextBlock
from src.Synthetic_document_pipeline.content_generator.content_src.config.color import Color
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config
from PIL import Image, ImageDraw, ImageFont

from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import TYPESDICT

def draw_boxes(modules: list, image_fullpath:str) -> None: 
    size = Config.page_size
    image = Image.new('RGBA', size.to_tuple(), color='white')
    draw = ImageDraw.Draw(image)
    
    linewidth = 4
    for module in modules:
        for block in module.blocks:
            box = (size.width*block.x0, size.height*block.y0, size.width*block.x1, size.height*block.y1)
            color = Color.from_subtype(block.subtype)
            tfont = ImageFont.truetype("arial.ttf", 20)

            block.draw(image, size)

            draw.rectangle(box, outline=color.outline, width=linewidth)#, fill=color.fill)
            # draw.text((box[0], box[1]), block.subtype, font=tfont, fill=color.text_color, width=linewidth, anchor="lt")
    image.save(image_fullpath)


def get_column_coords(midpage_coords, no_cols):
    return [Coords(i/no_cols, (i+1)/no_cols, midpage_coords.y0, midpage_coords.y1) for i in range(no_cols)]


def add_more_blocks_from_type(block_type_list:list, no_items, btype='image'):
    while block_type_list.count(btype) < no_items:
        random_index = randint(0, len(block_type_list) - 1)
        block_type_list[random_index] = btype
    return block_type_list

def generate_block_type(block):
    TYPEDICT = {
        'text': TextBlock,
        'image': ImageBlock,
        'table': TableBlock
    }
    return TYPEDICT.get(block.type, TYPEDICT['text'])(block.x0, block.x1, block.y0, block.y1, block.subtype)

def get_blocks_from_xml(xml_path):
    '''
    The output is a list of objects with type [[x0, y0, x1, y1], type]
    '''
    tree = ET.parse(xml_path)
    doc = tree.getroot()
    blocks = [[[float(block.attrib['x0']), float(block.attrib['y0']), float(block.attrib['x1']), float(block.attrib['y1'])], block.attrib['subtype']] 
                for module in doc for block in module]
    return blocks

def get_blocks_from_json(json_path):

    """
    This functions return extension .png and the blocks informations by taking a json path
    """
    with open(json_path, 'r') as file:
        doc = json.load(file)
    blocks = [block for module, blocks in doc.items() for block in blocks]

    """
    blocks = [block for module, blocks in doc.items() for block in blocks]
    blocks = []
    doc = {"image": "[0]", "text": "[1]", "equation": "[2]", "Liste": "[3]"}
    for module, block_list in doc.items():
        for block in block_list:
            blocks.append(block)
    """
    
    return os.path.splitext(json_path)[0] + ".png", blocks


def generate_xml(blocks: list, xml_fullpath:str):
    doc = ET.Element("doc")
    for x0, y0, x1, y1, bsubtype in blocks:
        btype = TYPESDICT.get(bsubtype, '')
        ET.SubElement(doc, "block", type=btype, subtype=bsubtype, 
                    x0=str(x0), y0=str(y0), x1=str(x1), y1=str(y1))
    tree = ET.ElementTree(doc)
    tree.write(xml_fullpath)
    return xml_fullpath

def get_block_values(block):
    if len(block) == 2:
        return block[0], block[1]
    elif len(block) == 5:
        return block
    else:
        raise ValueError('Innapropriate block type.')
