from src.Synthetic_document_pipeline.content_generator.content_src.blocks.block import Block
from src.Synthetic_document_pipeline.content_generator.content_src.config.color import Color
from src.Synthetic_document_pipeline.content_generator.content_src.config.enums import FigureType
from src.Synthetic_document_pipeline.content_generator.content_src.generators.Plotgen import create_plot_text
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import random_enable

class ImageBlock(Block):
    def __init__(self, x0, x1, y0, y1, subtype, **kwargs):
        super().__init__(x0, x1, y0, y1, 'image', subtype)
    
    def draw(self, image, save_blocks=False):
        doc_coords = (self * image.size)
        plot_doc = None
        if random_enable(30) and False:
            config = {'test':True, 'output_path':"src/temp", 'type_plot':"line", 'size':[round(doc_coords.height), round(doc_coords.width)]}
            plot = create_plot_text(config)
            plot_doc = plot.document
        if save_blocks:
            box = (int(doc_coords.x0), int(doc_coords.y0), int(doc_coords.x1), int(doc_coords.y1))
            color = Color.from_subtype(self.subtype)
            image.draw.rectangle(box, outline=color.outline, width=4)
        image.paste(doc_coords, figure_type=FigureType.FIGURES, image=plot_doc)
        return self
