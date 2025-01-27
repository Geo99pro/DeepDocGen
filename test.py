# Decomment the lines 2 and 3 when using Jupyter Notebook to allow the autoreload of the modules.
# %load_ext autoreload
# %autoreload 2

import logging
from src.Pdf_annotation_pipeline.run_process import PDFAnnotationPipeline
from src.Post_Processing_Folder.Post_Processing_to_COCO_format.coco_mapping_engine import CocoMappingEngine
from src.Synthetic_document_pipeline.content_generator.content_generator_engine import ContentGeneratorEngine
from src.Post_Processing_Folder.Post_Processing_to_remove_document_overlap.remove_overlap_engine import RemoveOverlapEngine
from src.Synthetic_document_pipeline.IA_Models.Document_Layout_Generator_Models.LayoutTransformer.utils.inference_engine import InferenceEngine

def setup_logger(name, log_file, level=logging.INFO):
    """
    Function allowing the user to setup as many loggers as needed.
    from : https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings

    Args:
        - name (str): The name of the logger.
        - log_file (str): The path to the log file.
        - level (int): The level of logging.

    Returns:
        - logger (logging.Logger): The logger.
    """
    handler = logging.FileHandler(log_file)        
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

config_path = "D:/Meus_codigos_de_mestrado/Synthetic_document_pipeline/pipeline_config.yaml"
pdf_selector = PDFAnnotationPipeline(config_path=config_path, setup_logger=setup_logger)
layout_inference = InferenceEngine(config_path=config_path)
remove_overlap = RemoveOverlapEngine(config_path=config_path)
content_generator = ContentGeneratorEngine(config_path=config_path)
coco_mapping = CocoMappingEngine(config_path=config_path, setup_logger=setup_logger)

pdf_selector.choose_pdf_per_group()
pdf_selector.convert_annotations_to_publyanet_format()
layout_inference.run_inference()
correct_overlap = remove_overlap.remove_overlap()
content_generator.dataset_generator()
coco_mapping.map_on_coco_format()