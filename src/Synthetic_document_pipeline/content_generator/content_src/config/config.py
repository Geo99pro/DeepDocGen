from dataclasses import dataclass, field
import json
import os
from src.Synthetic_document_pipeline.content_generator.content_src.utils.generator_utils import get_all_images, get_all_texts
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import random_number, random_str

"""
Basicaly the config.py file, in function of the values available in the config.json file set the diferent parameters of the class available.
- Blur
- Size
- Background
- TextData
- Config
"""



@dataclass
class Size:
    width:float = 0
    height:float = 0

    def to_tuple(self):
        """
        This function return the tuple of width and height by a given widht and height

        Args: the class itself

        Ex: size = Size(width=800, height=600)
            size.to_tuple() = (800, 600)
        """
        return (self.width, self.height)
    

    @classmethod
    def from_list(cls, sizelist: type= tuple):

        """This function return a instance of the Size class by a given tuple value (value, height).

        Args: the class itself
              sizelist: must be tuple of width and height

        Ex of return: Size(width=800, height=600)
        """
        if not len(sizelist) == 2:
            raise Exception("The page size must have width and length.")
        return cls(width=sizelist[0], height=sizelist[1])
    

    def join(self, sep="_"):
        """
        This function return the str of the class Size

        Args: the class itself

        Ex: size = taille.join()
            size = 800_600
        """
        return str(self.width) + sep + str(self.height)


@dataclass
class Background:
    """This class is content of the parameters of the background such as:
    - probability 
    - save_file
    - orange
    - default_color
    - colors
    """
    probability: int = 0
    save_file: bool = False
    orange: int = 0
    default_color: str = "white"
    colors: list = field(default_factory=list)


@dataclass
class TextData:
    """This class is content of the parameters of the text format such as for example: 
    - fonts = ["arial", "courier", "opensans", "raleway", "roboto", "times"]
    - modifiers = ["regular", "italic", "bold"]
    - size = [0.7, 1.5]
    - random_thickness = [1, 2]
    - random_space = [0.1, 1.2]
    """
    fonts: list = field(default_factory=list)
    modifiers: list = field(default_factory=list) # bold, italic, normal
    size: list = field(default_factory=list)
    random_thickness: list = field(default_factory=list)
    random_space: list = field(default_factory=list)

  
    @property
    def font(self):
        """
        This function return a random choice of font ("arial", "courier", "opensans",) based on a given fonts.
        
        Args:
        fonts: type str or list of str or tuple of str of 2 or more policy
        Ex of modifiers = ["regular", "italic", "bold"]
        """
        return random_str(self.fonts)
    
    @property
    def modifier(self):
        """
        This function return a random choice of font-styles (regular, bold or italic) based on a given modifiers.
        
        Args:
        modifier: type str or list of str or tuple of str of 2 or more policy
        Ex of modifiers = ["regular", "italic", "bold"]
        """
        return random_str(self.modifiers)
    
    @property
    def text_size(self):
        """
        This function returns a beta distribution value that represents the font-size (how small or large the text will appear) as a function of a given size.

        Args: 
        - size type int or float or tuple or list
        - ndigits: type int, represent the number of float value after the comma
        """
        return random_number(self.size, ndigits=5)
    
    @property
    def text_thickness(self):
        """
        This function returns a beta distribution value that represents the font-weight (how thin or thick the text will appear) as a function of a given random_number.

        Args: 
        - size type int or float or tuple or list
        - ndigits: type int, represent the number of float value after the comma
        """
        return random_number(self.random_thickness, ndigits=5)


@dataclass
class Blur:
    enable: bool = False
    probability: int = 0
    max_pixel: int = 3

class Config:
    output_folder:str
    images_folder:str
    texts_folder:str
    fonts_folder:str

    text_list:list
    image_dict:list
    
    test_document:bool
    boxes:bool
    enable_mask:bool
    
    background: Background
    rotation_probability: int
    set_original: bool
    set_original_box: bool
    
    blur: Blur
    join_docs: bool
    
    page_size:Size
    size_increase: list
    size_reduce: list
    interline_space: list

    text:TextData
    language: list
    symbols: list
    markers: list
    margins: list #top, right, bottom, left

    _CONFIG_FILE = None
    _CONFIG = None

    def __init__(self, config_file=None, output_folder=None):
        """
        This function initializes the config class (its various attributes) using the values available in a given config.json file.
        Args:
        - self: refers to an instance of the Config class itself
        - config_file: must be the file "config.json" with the various parameters
        - output_folder: represents the output folder
        """
        if config_file is None:
            
            config_file = Config.get_required_env_var("CONFIG_FILE")
            
        if not os.path.exists(config_file):
            raise FileNotFoundError("Configuration file not found.")

        Config.output_folder = output_folder
        
        os.makedirs(output_folder, exist_ok=True)

        name_by_class = {
            "BLUR": Blur,
            "BACKGROUND": Background,
            "TEXT": TextData
        }

        Config._CONFIG_FILE = config_file

        with open(config_file, 'r') as f:
            Config._CONFIG = json.load(f)

        for key, value in Config._CONFIG.items():
            #lkey = lower key
            lkey = key.lower()
            if lkey == 'page_size':
                setattr(Config, lkey, Size.from_list(value))
            elif not isinstance(value, dict):
                setattr(Config, lkey, value)
            data = name_by_class.get(key, None)
            if data is not None:
                setattr(Config, lkey, data(**{k.lower():v for k, v in value.items()}))
        
        Config.image_dict = get_all_images(Config.images_folder)
        Config.image_dict_lengths = {k: len(v) for k,v in Config.image_dict.items()}
        Config.text_list = get_all_texts(Config.texts_folder)
        Config.text_list_length = len(Config.text_list)

    @staticmethod
    def get_config_file():
        return Config._CONFIG_FILE

    @staticmethod
    def get_required_env_var(envvar: str):
        """
        This function searches for the environment variable on the machine by a given specification.

        Args:
        envvar: type str
        """
        
        if envvar not in os.environ:
            raise Exception(f"Please set the {envvar} environment variable")
        return os.environ[envvar]