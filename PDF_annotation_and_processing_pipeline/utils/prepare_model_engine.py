import os
import torch.nn as nn
import torchvision.models as models
from torchinfo import summary

os.environ["OMP_NUM_THREADS"] = "1"

class PrepareModelEngine:
    """
    This class is used to prepare the model for the embedding extraction.
    By calling this PrepareModelEngine, user creates an instance of this class.
    It receives the model name, the model weights name.
    It initializes the model, removes the last layer, freezes the model weights and returns the model. 


    Attributes:

        model_name (torchvision.models): is the name of the model to use from torchvision.models
        model_weights (str): is the name of the model weights to use from torchvision.models
    
    Methods:

        __init__(): initializes the class with the model name and model weights
        prepare_model(self): prepares the model for the embedding extraction
    """

    def __init__(self, path_to_download_model: str, model_name, model_weights, shape_resize: tuple, batch_size : int, num_channels : int, device):
        self.path_to_download_model = path_to_download_model
        self.model_name = model_name #resnet152
        self.model_weights = model_weights 
        self.shape_resize = shape_resize
        self.batch_size = batch_size
        self.channels = num_channels
        self.device = device


    def prepare_model(self):
        os.environ['TORCH_HOME'] = self.path_to_download_model
        print(f'Dear User, the model will be downloaded to the following path: {self.path_to_download_model}. Check it out !')

        model_download = getattr(models, self.model_name)(weights = self.model_weights, progress = True).to(self.device)
        model_without_last_layer = nn.Sequential(*list(model_download.children())[:-1])

        for param in model_without_last_layer.parameters():
            param.requires_grad = False

        get_model_summary = summary(model_without_last_layer, 
                                    input_size = (self.batch_size, self.channels, self.shape_resize[0], self.shape_resize[1]),
                                    col_names = ["input_size", "output_size", "num_params", "trainable"], col_width = 30,
                                    row_settings=["var_names"])

        print(f"Dear User, the model has been prepared for the embedding extraction. The model summary is as follows:\n {get_model_summary}")
        return model_without_last_layer