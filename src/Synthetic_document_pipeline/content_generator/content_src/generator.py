from src.Synthetic_document_pipeline.content_generator.content_src.blocks.block import Block
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Size
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import TYPESDICT
from src.Synthetic_document_pipeline.content_generator.content_src.document import Document
from src.Synthetic_document_pipeline.content_generator.content_src.utils.block_utils import generate_block_type, get_block_values


class ContentGenerator:

    @staticmethod
    def generate(block_list: list, page_size= Size, image_path: str ="./data/image.png", save_blocks: bool =True): 
        '''
        The list input is actually a list with multiple types:
            [[x0, y0, x1, y1], type]
                or
            [x0, y0, x1, y1, type]
        '''
        block_list = [get_block_values(block) for block in block_list]
        image = Document(image_path, page_size)
        resized_list = []
        for [x0, y0, x1, y1], subtype in block_list:
            new_block = Block(x0, x1, y0, y1, TYPESDICT.get(subtype, 'text'), subtype)
            new_block = generate_block_type(new_block)
            new_block = new_block.draw(image, save_blocks=save_blocks)
            resized_list.append(new_block)
        image.save(resized_list)