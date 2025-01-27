import os, random
from datetime import datetime as date
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config, Size
from src.Synthetic_document_pipeline.content_generator.content_src.generator import ContentGenerator
from src.Synthetic_document_pipeline.content_generator.content_src.utils.block_utils import get_blocks_from_json



input_path = "/petrobr/parceirosbr/buscaict/share/content_generator/block_xmls_1/"
input_path = "src/temp/block_xmls_1/"
output_path = "src/temp/"
config_path = "/petrobr/parceirosbr/buscaict/share/content_generator/config.json"
config_path = "src/config.json"


output_folder = os.path.join(output_path)
Config(config_path, output_folder)
content_list = [os.path.splitext(file)[0] for file in os.listdir(input_path) 
                if os.path.splitext(file)[1] == ".json"]
# random.shuffle(content_list)

for file in content_list[1:]:
    for i in range(1):
        print("{} de {}".format(i, 100), end="\r")
        output_file = os.path.join(output_folder, file + ".png")
        output_file = os.path.join(output_folder, "0001.png")
        block_list = get_blocks_from_json(os.path.join(input_path, file + ".json"))
        page_size = Config.page_size
        ContentGenerator.generate(block_list, page_size, image_path=output_file, save_blocks=True)

"""
{
  "bodymodule": [
    [ [ 0.15, 0.05, 0.85, 0.10 ], "title" ],
    [ [ 0.2, 0.11, 0.8, 0.16 ], "subtitle" ],
    [ [ 0.1, 0.17, 0.9, 0.25 ], "paragraph" ],
    [ [ 0.25, 0.27, 0.75, 0.37 ], "table" ],
    [ [ 0.1, 0.40, 0.5, 0.60 ], "list" ]
  ],
  "footermodule": [
    [[0.46, 0.91, 0.54, 0.9400000000000001], "pagenumber"]
  ]
}

"""