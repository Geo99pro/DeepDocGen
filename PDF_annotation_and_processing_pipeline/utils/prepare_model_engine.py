import os
import torch 
import torch.nn as nn
import torchvision.models as models
from torchinfo import summary

os.environ["OMP_NUM_THREADS"] = "1"

class PrepareModelEngine:
    """
    This class is used to prepare the model for the embedding extraction.
    By calling this PrepareModelEngine, user creates an instance of this class.

    Methods:
        - prepare_model: prepares the model for the embedding extraction. The model is downloaded from torchvision.models (No prior knowledge on document is known by the model)
        - use_fine_tuned_model: uses the fine-tuned model for the embedding extraction. The mpdel is loaded from the path provided by the user. (Prior knowledge on document is known by the model)
    """

    def prepare_model(self, 
                      path_to_download_model: str, 
                      model_name: str, model_weights: str, 
                      shape_resize: tuple, 
                      batch_size: int, 
                      num_channels: int, 
                      device)-> nn.Module:
        """
        The method prepares the model for the embedding extraction.

        Args:

            - path_to_download_model (str): is the path where the model will be downloaded
            - model_name (str): is the name of the model to use from torchvision.models
            - model_weights (str): is the name of the model weights to use from torchvision.models
            - shape_resize (tuple): is the shape to resize the input image
            - batch_size (int): is the batch size
            - num_channels (int): is the number of channels in the input image
            - device: is the device to run the model on (e.g., 'cpu' or 'cuda')
        """

        os.environ['TORCH_HOME'] = path_to_download_model
        print(f'Dear User, the model will be downloaded to the following path: {path_to_download_model}. Check it out !')

        model_download = getattr(models, model_name)(weights=model_weights, progress = True).to(device)
        model_without_last_layer = nn.Sequential(*list(model_download.children())[:-1])

        for param in model_without_last_layer.parameters():
            param.requires_grad = False

        get_model_summary = summary(model_without_last_layer, 
                                    input_size = (batch_size, num_channels, shape_resize[0], shape_resize[1]),
                                    col_names = ["input_size", "output_size", "num_params", "trainable"], col_width = 30,
                                    row_settings=["var_names"])

        print(f"Dear User, the model has been prepared for the embedding extraction. The model summary is as follows:\n {get_model_summary}")
        return model_without_last_layer
    
    def use_fine_tuned_model(self, 
                             model_path, 
                             shape_resize: tuple, 
                             batch_size: int, 
                             num_channels: int, 
                             device)-> nn.Module:
        """
        The method uses the fine-tuned model for the embedding extraction.
        
        Args:
        
            - model_path (str): is the path where the fine-tuned model is located
            - shape_resize (tuple): is the shape to resize the input image
            - batch_size (int): is the batch size
            - num_channels (int): is the number of channels in the input image
            - device: is the device to run the model on (e.g., 'cpu' or 'cuda')
            """
        model = torch.load(model_path)
        model_without_last_layer = nn.Sequential(*list(model.children())[:-1])
        model_without_last_layer.to(device)
        
        for param in model_without_last_layer.parameters():
            param.requires_grad = False

        get_model_summary = summary(model_without_last_layer,
                                    input_size = (batch_size, num_channels, shape_resize[0], shape_resize[1]),
                                    col_names = ["input_size", "output_size", "num_params", "trainable"], col_width = 30,
                                    row_settings=["var_names"])
        print(f"Dear User, the fine-tuned model has been loaded. The model summary is as follows:\n {get_model_summary}")
        return model_without_last_layer