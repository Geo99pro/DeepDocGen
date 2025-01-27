import os
import torch
import shutil
import torch.nn as nn
from torchinfo import summary
import torchvision.models as models

os.environ["OMP_NUM_THREADS"] = "1"

class PrepareModelEngine:
    """
    This class is used to prepare the model for the embedding extraction.
    By calling this PrepareModelEngine, user creates an instance of this class.

    Methods:
        - prepare_model: prepares the model for the embedding extraction. The model is downloaded from torchvision.models (No prior knowledge on document domain is known by the model)
        - use_fine_tuned_model: uses the fine-tuned model for the embedding extraction. The model is loaded from the path provided by the user. (Prior knowledge on document domain is known by the model)
    """
    
    def prepare_model(self, 
                      path_to_download_model: str,
                      desired_folder_name: str,
                      model_name: str, model_weights: str, 
                      shape_resize: tuple, 
                      batch_size: int, 
                      num_channels: int, 
                      device,
                      display_model_summary: bool)-> nn.Module:
        """
        The method prepares the model for the embedding extraction.

        Args:

            - path_to_download_model (str): is the path where the model will be downloaded
            - desired_folder_name (str): is the name of the folder where the model will be downloaded
            - model_name (str): is the name of the model to use from torchvision.models
            - model_weights (str): is the name of the model weights to use from torchvision.models
            - shape_resize (tuple): is the shape to resize the input image
            - batch_size (int): is the batch size
            - num_channels (int): is the number of channels in the input image
            - device: is the device to run the model on (e.g., 'cpu' or 'cuda')
            - display_model_summary (bool): is a boolean to display the model summary
        
        Returns:
        
            - model_without_last_layer (nn.Module): is the model without the last layer
        """
        folder_path = os.path.join(path_to_download_model, desired_folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        os.makedirs(folder_path)
        os.environ['TORCH_HOME'] = folder_path

        model_download = getattr(models, model_name)(weights=model_weights, progress = True).to(device)
        model_without_last_layer = nn.Sequential(*list(model_download.children())[:-1])

        for param in model_without_last_layer.parameters():
            param.requires_grad = False

        if display_model_summary:
            get_model_summary = summary(model_without_last_layer, 
                                        input_size = (batch_size, num_channels, shape_resize[0], shape_resize[1]),
                                        col_names = ["input_size", "output_size", "num_params", "trainable"], col_width = 30,
                                        row_settings=["var_names"])

        return model_without_last_layer, get_model_summary
    
    def use_fine_tuned_model(self,
                             model_name: str,
                             model_weights_path: str, 
                             shape_resize: tuple, 
                             batch_size: int, 
                             num_channels: int, 
                             device,    
                             display_model_summary: bool)-> nn.Module:
        """
        The method uses the fine-tuned model for the embedding extraction.
        
        Args:
        
            - model_name (str): is the name of the model to use from torchvision.models
            - model_weights_path (str): is the path to the fine-tuned model weights
            - shape_resize (tuple): is the shape to resize the input image
            - batch_size (int): is the batch size
            - num_channels (int): is the number of channels in the input image
            - device: is the device to run the model on (e.g., 'cpu' or 'cuda')
            - display_model_summary (bool): is a boolean to display the model summary
        
        Returns:

            - model_without_last_layer (nn.Module): is the model without the last layer
        """
 
        fine_tuned_model = getattr(models, model_name)(weights=None).to(device)
        fine_tuned_model.head = nn.Linear(fine_tuned_model.head.in_features, 5)
        model_weights = torch.load(model_weights_path, map_location=device, weights_only=True)
        fine_tuned_model.load_state_dict(model_weights)
        model_without_last_layer = nn.Sequential(*list(fine_tuned_model.children())[:-1])
                  
        for param in model_without_last_layer.parameters():
            param.requires_grad = False
            
        get_model_summary = None
        if display_model_summary:
            get_model_summary = summary(model_without_last_layer,
                                    input_size = (batch_size, num_channels, shape_resize[0], shape_resize[1]),
                                    col_names = ["input_size", "output_size", "num_params", "trainable"], col_width = 30,
                                    row_settings=["var_names"])
            
        return model_without_last_layer, get_model_summary