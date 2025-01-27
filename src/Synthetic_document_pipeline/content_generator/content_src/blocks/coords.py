from src.Synthetic_document_pipeline.content_generator.content_src.config.enums import Align
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import get_perc_value
from copy import deepcopy


class Coords:
    x0: float
    x1: float
    y0: float
    y1: float

    def __init__(self, x0, x1, y0, y1) -> None:
        self.x0 = min(x0, x1)
        self.x1 = max(x0, x1)
        self.y0 = min(y0, y1)
        self.y1 = max(y0, y1)


    @property
    def width(self):
        """This function return the widht of the object Coords by substracting x0 from x1
        """
        return self.x1 - self.x0
    
    @property
    def height(self):
        """This function return the height of the object Coords by substracting y0 from y1
        """
        return self.y1 - self.y0
    
    def change_size(self, height_percentage= None, width_percentage= None, halign= 'left', valign= 'top'):
        """This function return a new copy of the modified values of ocject coords
        """
        new_copy = self.change_height(height_percentage, valign)\
                        .change_width(width_percentage, halign)
        return new_copy
    
    
    def change_height(self, height_percentage, valign='top'):

        """This function return """
        ''' Percentage range from 0 to 100. '''
        new_coords = deepcopy(self)
        if height_percentage is None: return new_coords
        height = height_percentage/100
        if height > self.height: return
        if valign == Align.TOP:
            new_coords.y1 = new_coords.y0 + height
        elif valign == Align.CENTER:
            mid_y = (new_coords.y0 + new_coords.y1) / 2
            new_coords.y0 = mid_y - height / 2
            new_coords.y1 = mid_y + height / 2
        elif valign == Align.BOTTOM:
            new_coords.y0 = new_coords.y1 - height
        return new_coords


    def change_width(self, width_percentage, halign:Align='left'):
        ''' Percentage range from 0 to 100. '''
        new_coords = deepcopy(self)
        if width_percentage is None: return new_coords

        width = width_percentage/100
        if width > self.width: return

        if halign == Align.LEFT:
            new_coords.x1 = new_coords.x0 + width
        elif halign == Align.CENTER:
            mid_x = (new_coords.x0 + new_coords.x1) / 2
            new_coords.x0 = mid_x - width / 2
            new_coords.x1 = mid_x + width / 2
        elif halign == Align.RIGHT:
            new_coords.x0 = new_coords.x1 - width
        return new_coords

    
    
    def cut_middle_height(self, top_percentage, bottom_percentage):
        new_coords = deepcopy(self)
        header_height = top_percentage/100
        footer_height = bottom_percentage/100
        new_coords.y0 += header_height
        new_coords.y1 -= footer_height
        return new_coords
    
    def cut_middle_width(self, left_percentage, right_percentage):
        new_coords = deepcopy(self)
        left_width = get_perc_value(new_coords.x1 - new_coords.x0, left_percentage)
        right_width = get_perc_value(new_coords.x1 - new_coords.x0, right_percentage)
        new_coords.x0 += left_width
        new_coords.x1 -= right_width
        return new_coords
        
    def adjust_margin(block, margins=None):
        if margins is None: 
            return block
        return block.cut_middle_width(margins.left, margins.right).cut_middle_height(margins.top/2, margins.bottom/2) 