from math import floor
from random import choice
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import DEFAULTFONT, TEXTSIZEMODIFIERS
from src.Synthetic_document_pipeline.content_generator.content_src.utils.text_utils import generate_font, get_text_size
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import random_number, random_str


class TextConfig():
    def __init__(self, subtype=None, text_size=None, font=DEFAULTFONT, modifiers=None, block_height=None) -> None:
        """
        This function initialize the TextConfig class using the available values in setting.py
        
        Args:
        - self: refers to an instance of the TextConfig class itself
        - subtype: is the kind of type (paragraph, title, subtitle, subsubtitle, note, pagenumber....etc)
        - text_size: refers to the return of the function get_text_size (see this one to get more informations)  
        - font: is the default font (arial in this case)
        - modifiers: refers to the choice of a given list or tuple of type style available in the file setting.py
        - block_height: block_height: refers to the height of the bbox, bringing its normalized coordinates up to actual scale.
        """
        text_config = TEXTSIZEMODIFIERS.get(subtype, TEXTSIZEMODIFIERS['paragraph'])

        size_config = text_config["size"]

        #print(size_config[0])
        default_size = random_number(Config.text.size, ndigits=1)

        self.text_size = get_text_size(text_config, Config.size_increase, Config.size_reduce, 
                                                default_size) if text_size is None else text_size
        
        if modifiers is None:
            self.modifier = random_str(text_config["modifier"])
        else:
            self.modifier = random_str(modifiers)

        if subtype in ["title", "subtitle", "pagenumber"]:
            self.text_size = block_height*0.92
        
        self.font = generate_font(Config.fonts_folder, floor(self.text_size), font, self.modifier)
        #self.line_height = self.font.getsize('hg')[1]
        self.line_height = self.font.getbbox('hg')[3]-self.font.getbbox('hg')[1]
        


