from collections import defaultdict
from datetime import datetime as date
import math
import os
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import beta_rdist, gauss_rdist
from PIL import Image, ImageDraw


def make_file_basename(model_name, page_size) -> str:
    time_format =  date.now().strftime(r"%d/%m/%Y_%H:%M:%S:%f")
    page_format = page_size.join("_")
    return f'{model_name}_{time_format}_{page_format}'

def perc_to_float(val, total=100):
    return val/total

def generate_random_heights(no_blocks, col_height, min_height, header_height):
    block_height = []
    for _ in range(no_blocks - 1):
        left_space = col_height - sum(block_height)
        if left_space <= min_height/100: break
        block_width = beta_rdist(min_height/100.0, left_space, ndigits=5)
        block_height.append(block_width)
    final_left_space = col_height - sum(block_height)
    if final_left_space <= min_height/100:
        block_height[-1] += final_left_space
    else:
        block_height.append(final_left_space)

    block_coords = []
    full_height = header_height
    for i, height in enumerate(block_height):
        block_coords.append([full_height, full_height + height])
        full_height += height
    return block_coords

def generate_preset_heights(config, col_height, default_min_height, header_height, block_subtypes):
    blocks_height = []
    size_per_line = (config.get('interline_space', 1.5) + config.get('font_size', 1.5)) / 100
    for i, block_subtype in enumerate(block_subtypes[:-1]):
        content_config = config.get('content')[i]
        par_config = content_config.get('paragraph', [0, {}])[1]
        left_space = col_height - sum(blocks_height)
        min_height = get_min_height(block_subtype, size_per_line, default_min_height)

        if left_space <= min_height: break
        mean_lines = par_config.get('mean_lines', None)
        std_lines = par_config.get('std_lines', None)

        if block_subtype in ['title', 'subtitle', 'subsubtitle']:
            block_height = config["text_type_multiplier"].get(block_subtype, 1) * config.get('font_size', 1.5) / 100
        elif block_subtype == 'paragraph':
            mean = mean_lines * size_per_line
            std = std_lines * size_per_line
            
            if left_space <= size_per_line: break
            block_height = (beta_rdist(min_height, left_space, ndigits=5) // size_per_line) * size_per_line
        else:
            block_height = beta_rdist(min_height, left_space, ndigits=5)

        blocks_height.append(block_height)
    final_left_space = col_height - sum(blocks_height)
    last_block = block_subtypes[-1]

    min_height = get_min_height(last_block, size_per_line, default_min_height)
    block_height = config["text_type_multiplier"].get(last_block, 1) * config.get('font_size', 1.5) / 100
    if final_left_space > min_height:
        if block_height < min_height and block_subtypes[-1] in ['title', 'subtitle']:
            blocks_height.append(block_height)
        else:
            blocks_height.append(final_left_space)

    block_coords = []
    full_height = header_height
    for i, height in enumerate(blocks_height):
        block_coords.append([full_height, full_height + height])
        full_height += height
    return block_coords


def get_min_height(block_subtype, size_per_line=None, default_min_height=10):
    if block_subtype in ['image', 'table']:
        return 0.35
    elif block_subtype == 'paragraph' and size_per_line is not None:
        return size_per_line/100
    else:
        return default_min_height/100


def rotate_around_point_highperf(xy: type= tuple , radians: type= float or int , origin: tuple= (0, 0)):
    """
    This functions help to do the rotation bidimentionnal. 
    Rotate a point around a given point.

    I call this the "high performance" version since we're caching some
    values that are needed >1 time. It's less readable than the previous
    function but it's faster.
    """
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy

def get_all_images(images_path: type= str):

    """This function return a default dictionary (set as list) of all images available in images_path

    Args:
    image_path: type = string: must receive the path of where are the images

    Ex of result: defaultdict(<class 'list'>, {'figures': [<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1694x641 at 0x7B5097C1BA90>, <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1803x690 at 0x7B5097CAB040>,<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1526x937 at 0x7B5097CAB280>,  <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1288x934 at 0x7B5097CAB220>, <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=1685x683 at 0x7B5097CABD30>, <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=809x736 at 0x7B5097CAB2B0>]})
    """
    images_dict = defaultdict(list)
    

    for folder in os.listdir(images_path):
        for file in os.listdir(os.path.join(images_path, folder)):
            file_path = os.path.join(images_path, folder, file)
            if os.path.isdir(file_path): continue
            images_dict[folder].append(Image.open(file_path))
    return images_dict

def get_all_texts(texts_path: type= str, language='portuguese'):
    
    """This function return the list of text by specifiying the path of the texts and languages.
    
        Args: 
        texts_path: type= string: must receive the path of where are the texts
        language: type= string: must receive the name of the language.
    NB: Language by default is portuguese
    """
    text_list = []
    text_by_language_path = os.path.join(texts_path, language)
    for file in os.listdir(text_by_language_path):
        with open(os.path.join(text_by_language_path, file), 'r', encoding='utf-8') as f:
            text_list.extend(f.readlines())
    return text_list