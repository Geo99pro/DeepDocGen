import os
import sys
import torch
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(project_root)
from src.Synthetic_document_pipeline.IA_Models.Document_Layout_Generator_Models.LayoutTransformer.utils.dataset_predictor import JSONLayout
from src.Synthetic_document_pipeline.IA_Models.Document_Layout_Generator_Models.LayoutTransformer.utils.model_predictor import GPT, GPTConfig
from src.Synthetic_document_pipeline.IA_Models.Document_Layout_Generator_Models.LayoutTransformer.utils.utils_predictor import set_seed
from src.Synthetic_document_pipeline.IA_Models.Document_Layout_Generator_Models.LayoutTransformer.utils.model_prediction import Predictor, PredictorConfig
import yaml


class InferenceEngine:
    """
    This class is responsible for the inference engine of the Layout Transformer model.
    By using the trained model, this class will generate the layout of a document.
    
    Attributes:
    -----------
    config_path: str
        The path to the configuration file.

    Methods:
    --------
    """

    def __init__(self, config_path: str):
        """
        The constructor of the InferenceEngine class.
        """
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """
        This method loads the configuration file.
        """
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        return self.config

    def run_inference(self):
        """
        This method runs the inference engine of the Layout Transformer model.
        """

        if self.config["Layout_generator_process"]["should_perform"]:
            self.dataset_path = self.config["Layout_generator_process"]['Parameters']['dataset_path']
            self.model_trained_path = self.config["Layout_generator_process"]['Parameters']['model_trained_path']
            self.batch_size = self.config["Layout_generator_process"]['Parameters']['batch_size']
            self.n_layer = self.config["Layout_generator_process"]['Parameters']['n_layers']
            self.n_embd = self.config["Layout_generator_process"]['Parameters']['n_embd']
            self.n_head = self.config["Layout_generator_process"]['Parameters']['n_heads']
            self.temper = self.config["Layout_generator_process"]['Parameters']['temper']
            self.top_k = self.config["Layout_generator_process"]['Parameters']['top_k']
            self.generate_image_range = self.config["Layout_generator_process"]['Parameters']['generate_image_range']
            self.generate_image_path = self.config["Layout_generator_process"]['Parameters']['generate_image_path']
            self.generate_coords_path = self.config["Layout_generator_process"]['Parameters']['generate_coords_path']
            
            set_seed(self.config["Layout_generator_process"]['Parameters']['seed'])
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"Using device: {device}.")

            test_dataset = JSONLayout(self.dataset_path)

            mconf = GPTConfig(vocab_size = 264, block_size = 517,
                        n_layer=self.n_layer, n_head=self.n_head, n_embd=self.n_embd) #264, 517  # a GPT-1
            model_trained = GPT(mconf)

            tconf = PredictorConfig(batch_size=self.batch_size,
                                sample_dir=self.generate_image_path,
                                output_dir= self.generate_coords_path)
            
            predictor = Predictor(model_trained=model_trained, 
                                test_dataset=test_dataset,
                                checkpoint_path=self.model_trained_path,
                                config= tconf,
                                device=device,
                                gen_range= self.generate_image_range,
                                top_k=self.top_k,
                                temper=self.temper,
                                args=self.config)

            predictor.predict()
        
        else:
            print(f"Dear user, you have chosen not to perform the Layout generation step by setting the should_perform parameter in the configuration file to False.\n"
                  f"This means that the Layout Transformer model will not be used to generate the layout of the document.\n")


                         
                              
                              


