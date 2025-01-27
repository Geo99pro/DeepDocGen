import os, random
from datetime import datetime as date
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config, Size
from src.Synthetic_document_pipeline.content_generator.content_src.generator import ContentGenerator
from src.Synthetic_document_pipeline.content_generator.content_src.utils.block_utils import get_blocks_from_json



input_path = "/temp_jer/dataset_14_12_2022_17_729215/"
output_path = "/temp_jer/dataset_14_12_2022_17_729215/output/"
config_path = "src/config.json"

os.makedirs(output_path, exist_ok=True)


output_folder = os.path.join(output_path)
Config(config_path, output_folder)
content_list = [os.path.splitext(file)[0] for file in os.listdir(input_path) 
                if os.path.splitext(file)[1] == ".json"]

for f, file in enumerate(content_list):
    print("{} de {}".format(f, len(content_list)), end="\r")
    output_file = os.path.join(output_folder, file + ".png")
    block_list = get_blocks_from_json(os.path.join(input_path, file + ".json"))
    page_size = Config.page_size
    ContentGenerator.generate(block_list, page_size, image_path=output_file, save_blocks=True)
