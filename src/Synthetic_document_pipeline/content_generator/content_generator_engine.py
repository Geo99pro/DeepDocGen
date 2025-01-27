import os
import sys
import tqdm
import yaml
import logging
import warnings
from statistics import mean
from time import perf_counter as time
from datetime import datetime as date
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(project_root)
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config, Size
from src.Synthetic_document_pipeline.content_generator.content_src.generator import ContentGenerator
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import TESTINPUT, TESTOUTPUT
from src.Synthetic_document_pipeline.content_generator.content_src.utils.block_utils import get_blocks_from_json

class ContentGeneratorEngine:
    """
    This class is used to generate the realistic images of documents and their annotations.
    By calling this DatasetGenerator, user creates an instance of this class.

    Attributes:

    Methods:
    """

    def __init__(self, config_path: str):

        self.config_path = config_path
        self.config = self.load_config()
        
        self.content_gen_config_path = self.config["Content_generator_process"]["Parameters"]["config_path"]
        self.input_path = self.config["Content_generator_process"]["Parameters"]["input_path"]
        self.output_path = self.config["Content_generator_process"]["Parameters"]["output_path"]
        self.test_mode = self.config["Content_generator_process"]["Parameters"]["test_mode"]
        self.verbose = self.config["Content_generator_process"]["Parameters"]["verbose"]

    def load_config(self):
        """
        Load the configuration file in yaml format.
        """

        with open(self.config_path, "r") as file:
            self.config = yaml.safe_load(file)
            return self.config
        
    def dataset_generator(self) -> None:
        """
        This method is used to generate the dataset of images and their annotations.
        """
        if self.config["Content_generator_process"]["should_perform"]:
            
            output_folder = os.path.join(self.output_path, "dataset_{}".format(date.now().strftime(r"%d_%m_%Y")))

            try:
                os.makedirs(output_folder, exist_ok=True)
                print(f'output_folder directory created successfully as : {output_folder}')
            except OSError as error:
                print(f'output_folder directory can not be created')
            
            if self.test_mode:
                """Input path has the configurations of the differente content available in the image.

                Ex: Title, subtitle, paragraph, table, list, image, pagenumber.... etc
                
                """
                input_path = TESTINPUT
                print(f'input_path diretory is : {input_path}')

                output_folder = TESTOUTPUT
                print(f'output_path diretory is : {output_folder}')

                log_folder = os.path.join(self.output_path, "{}_log.log".format(os.path.basename(output_folder)))
            
            log_folder = os.path.join(self.output_path, "{}_log.log".format(os.path.basename(output_folder)))       
            logging.basicConfig(filename=log_folder, format="[%(levelname)s] (%(asctime)s) %(message)s ", level="INFO", filemode='w')
            logging.info(f"Starting configurations from file {self.content_gen_config_path}...")
            Config(self.content_gen_config_path, output_folder)
            logging.info("Completed!")
            logging.info("Initiatizating block extraction...")

            #Start time
            t0 = time()

            #Content list: He takes the values of the blocks inside each files json, part of content of input_path
            content_list = [get_blocks_from_json(os.path.join(self.input_path, file)) for file in os.listdir(self.input_path)
                            if os.path.splitext(file)[1] == ".json"]
            
            #Time spended to take the blocks coordinate
            time_to_load_blocks = time() - t0

            logging.info("All blocks extracted!")

            #Another time
            t1 = time()
            time_dict = {}

            for i, (png_file, blocks) in tqdm.tqdm(enumerate(content_list), "Adding components to documents..."):
                t2 = time()
                file_basename = os.path.basename(png_file)
                output_file = os.path.join(output_folder, file_basename)
                if os.path.exists(output_file) and not self.test_mode: 
                    continue
                page_size = Size(width=Config.page_size.width, height=Config.page_size.height)
                try:
                    ContentGenerator.generate(block_list= blocks, page_size= page_size, image_path=output_file, save_blocks=True)
                except Exception as exc:
                    logging.error("error on file {} ->\n {}".format(file_basename, exc))
                    raise exc
                time_per_doc = time() - t2

                logging.info("time to run file: {} -> ({}s)".format(file_basename, time_per_doc))
                time_dict[png_file] = time_per_doc
                total_time_for_now = time() - t1
                logging.info("Total time for now: {}s".format(total_time_for_now))
                logging.info("Mean time for now:  {}s".format(total_time_for_now/(i+1)))
            total_time = time() - t0

            if len(time_dict) != 0:
                time_to_generate_blocks = time() - time_to_load_blocks
                mean_time_per_doc = mean(time_dict.values())
                max_time_doc = max(time_dict)
                logging.info(f"Total time            -> {total_time}")
                logging.info(f"Time loading files    -> {time_to_load_blocks}")
                logging.info(f"Time generating files -> {time_to_generate_blocks}")
                logging.info(f"Mean time per file    -> {mean_time_per_doc}")
                logging.info(f"Max time file         -> {max_time_doc} ({time_dict[max_time_doc]}s)")
            else:
                logging.warning("No files found in selected path.")

        else:
            warnings.warn(f"Dear user, the process of content generator is disabled. Please, enable by setting the flag 'should_perform' to True in the configuration file.")