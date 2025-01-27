from src.Synthetic_document_pipeline.content_generator.content_src.blocks.block import Block
from src.Synthetic_document_pipeline.content_generator.content_src.config.color import Color
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config

# include classes
from src.Synthetic_document_pipeline.content_generator.content_src.generators.tables_samples import *

class TableBlock(Block):
    def __init__(self, x0, x1, y0, y1, subtype, **kwargs):
        super().__init__(x0, x1, y0, y1, 'table', subtype)
    
    def draw(self, image, save_blocks=False):
        doc_coords = self * image.size

        coords = (doc_coords)
        width = int(doc_coords.width)
        height = int(doc_coords.height)
        table_config = {
            "size":[width, height],
            "font_name":Config.text.fonts,

            "font_style":"regular",
            "font_size":[10,11],
            "bg_color":[Config.background.default_color],
            }
        
        box = (int(coords.x0), int(coords.y0), int(coords.x1), int(coords.y1))

        random_value = random.random()
        #print(random_value)
        if random_value > 0.3:
            #print(True)
            table_img = table_format_1(table_config)
        else:
            #print(False)
            table_img = table_format_2(table_config)

        table_img.document= table_img.document.resize(((box[2] - box[0])-1, (box[3] - box[1]-1)))

        image.image.paste(table_img.document, (int(coords.x0+1), int(coords.y0+1)))

        if save_blocks:
            box = box
            color = Color.from_subtype(self.subtype)
            #image.draw.rectangle(box, outline=color.outline, width=2)
        # image.paste(doc_coords, figure_type=FigureType.TABLES)

        return self