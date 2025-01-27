#https://stackoverflow.com/questions/71998978/early-stopping-in-pytorch
"""
Simple training loop; Boilerplate that could apply to any arbitrary neural network,
so nothing in this file really has anything to do with GPT specifically.
"""
import os
import math
import logging
import wandb
import shutil
import numpy as np
import torch
from tqdm import tqdm
from torch.nn import functional as F
from torch.utils.data.dataloader import DataLoader
from src.Synthetic_document_pipeline.IA_Models.Document_Layout_Generator_Models.LayoutTransformer.utils.utils_predictor import sample, convert_to_json

logger = logging.getLogger(__name__)


class PredictorConfig:
    # Optimization parameters
    batch_size = 1
    num_workers = 0  # for DataLoader

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Predictor:
    def __init__(self, model_trained: torch.nn.Module, 
                test_dataset, 
                checkpoint_path: str, 
                config: PredictorConfig,
                device: str,
                gen_range: int, 
                top_k: int, 
                temper: float, 
                args):
        """
        The constructor of the Predictor class.
        """
        
        self.model_trained = model_trained
        self.test_dataset = test_dataset
        self.checkpoint_path = checkpoint_path
        self.config = config
        self.device = device
        self.gen_range = gen_range
        self.top_k = top_k
        self.temper = temper
        self.args = args
        self.iters = 0
        self.fixed_x = None
        self.fixed_y = None
        
        # Initialize wandb
        print('Start sending log to wandb')
        wandb.init(project=self.args["Layout_generator_process"]["name"], name=self.args["Layout_generator_process"]["Parameters"]["experience_name"])
        wandb.config.update(args)

        # Use whatever GPUs are on the system
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if torch.cuda.is_available():
            self.device = torch.cuda.current_device()
        else:
            print(f'There is no GPU device available. Will use by default the {self.device} as device.')


    def predict(self):
        """
        This method runs the inference engine of the Layout Transformer model.
        """
        # Load the trained model
        self.model_trained = self.model_trained.to(self.device)
        self.model_trained.load_state_dict(torch.load(self.checkpoint_path, weights_only=False, map_location=self.device))

        self.model_trained.eval()
        with torch.inference_mode():
            data_to_evaluate = self.test_dataset
            
            loader = DataLoader(data_to_evaluate, shuffle=False, pin_memory=True,
                                batch_size=self.config.batch_size,
                                num_workers=self.config.num_workers)
            
            for it, (x_fixed, y_fixed) in enumerate(loader):
                self.fixed_x, self.fixed_y = x_fixed, y_fixed
                x_cond = self.fixed_x.to(self.device)
                
                layouts = self.fixed_x.detach().cpu().numpy()
                input_layouts = [self.test_dataset.render(layout) for layout in layouts]
                input_images = [wandb.Image(pil, caption=f'Input {i}') for i, pil in enumerate(input_layouts)]
                wandb.log({"input_layouts": input_images})

                for i in range (1, self.gen_range+1):  
                    layout = sample(self.model_trained, x_cond[:, :6], steps=self.test_dataset.max_length,
                                    temperature=self.temper, sample=True, top_k=self.top_k).detach().cpu().numpy()
                    sample_layouts = self.test_dataset.render(layout)
                    file_name_image = f'layout_generated_{i}_{it}.jpg'
                    sample_layouts.save(os.path.join(self.args["Layout_generator_process"]["Parameters"]["generate_image_path"], file_name_image), 'JPEG')

                    generated_layout = self.test_dataset.get_bbox_coords(layout)
                    #print(f'The current layout has {len(generated_layout)} bbox ')
                    generated_layout_dico = {"bodymodule": generated_layout}
                    wandb.log({"generated_layout": wandb.Image(sample_layouts, caption=f'Generated_for_image{it}_group_1')})
                    #print(type(generated_layout_dico))
                    file_name_json = f'layout_generated_{i}_{it}.json'
                    file_name_path = os.path.join(self.args["Layout_generator_process"]["Parameters"]["generate_coords_path"], file_name_json)
                    
                    convert_to_json(path=file_name_path, dataset_dictionary=generated_layout_dico)
