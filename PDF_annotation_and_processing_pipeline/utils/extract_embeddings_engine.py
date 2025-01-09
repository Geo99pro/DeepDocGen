import torch
import torch.nn as nn
from tqdm import tqdm
from torch.utils.data import DataLoader
from PDF_annotation_and_processing_pipeline.utils.embeddings_manager_engine import EmbeddingsManagerEngine


class ExtractEmbeddingsEngine:
    """
    This class is used to extract the embeddings from the model.
    By calling this ExtractEmbeddingsEngine, user creates an instance of this class.

    Methods:
    
        - extract_embeddings(self): This method extracts the embeddings from the model.
    """

    def extract_embeddings(self,
                           dataset, 
                           model: nn.Module, 
                           batch_size: int, 
                           shuffle_dataloader: bool, 
                           save_embedding_extracted: bool, 
                           device: str, 
                           **kwargs):
        """
        The method extracts the embeddings from the model.

        Args:

            - dataset: Dataset object.
            - model: Model object.
            - batch_size: Batch size.
            - shuffle_dataloader: Whether to shuffle the dataloader.
            - save_embedding_extracted: Whether to save the extracted embeddings. It's highly recommended to save the embeddings in the case where the embeddings are to be used later or if the dataset is large.
            - device: Device to run the model on.
            - **kwargs: Additional arguments. Such as : path_to_save_embeddings.
        """
        data_loader = DataLoader(dataset, 
                                 batch_size=batch_size, 
                                 shuffle=shuffle_dataloader)

        embedding_extracted_dict = {'embeddings_extracted': [], 'embeddings_names': []}
        model.to(device)
        
        model.eval()
        with torch.no_grad():
            for image, name in tqdm(data_loader):
                image = image.to(device)

                embedding_extracted = model(image).squeeze().detach().cpu().numpy()
                embedding_extracted_dict['embeddings_extracted'].append(embedding_extracted)
                embedding_extracted_dict['embeddings_names'].append(name[0])

        if save_embedding_extracted:
            embeddings_manager = EmbeddingsManagerEngine(f'{kwargs.get("path_to_save_embeddings")}embeddings_extracted_with_model', embedding_extracted_dict)
            embeddings_manager.save_embeddings()
            return embedding_extracted_dict
        else:
            return embedding_extracted_dict
        
