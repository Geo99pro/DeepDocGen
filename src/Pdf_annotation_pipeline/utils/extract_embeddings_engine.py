import os
import torch
from tqdm import tqdm
from torch.utils.data import DataLoader
from src.Pdf_annotation_pipeline.utils.embeddings_manager_engine import EmbeddingsManagerEngine
from src.Pdf_annotation_pipeline.utils.embeddings_manager_engine import EmbeddingsManagerEngine


class ExtractEmbeddingsEngine:
    """
    This class is used to extract the embeddings from the model.
    By calling this ExtractEmbeddingsEngine, user creates an instance of this class.

    Attributes:

        - dataset (object): is the object of the PDFImageEngine class.
        - model (object): is the object of the PrepareModelEngine class.
        - batch_size (int): is the batch size to use for the dataloader.
        - shuffle_dataloader (bool): is the boolean value to shuffle the dataloader.
        - save_embedding_extracted (bool): is the boolean value to save the extracted embeddings.
        - device (str): is the device to use for the model.
        - kwargs (dict): is the dictionary containing the path to save the embeddings.


    Methods:
        - extract_embeddings(self): This method extracts the embeddings from the model.
    """

    def __init__(self,
                 dataset, model,
                 batch_size: int,
                 shuffle_dataloader: bool,
                 save_embedding_extracted: bool,
                 device: str,
                 **kwargs)-> None:
        self.dataset = dataset
        self.model = model
        self.batch_size = batch_size
        self.shuffle_dataloader = shuffle_dataloader
        self.save_embedding_extracted = save_embedding_extracted
        self.device = device
        self.kwargs = kwargs

    def extract_embeddings(self):
        self.data_loader = DataLoader(self.dataset, batch_size=self.batch_size, shuffle=self.shuffle_dataloader)

        embedding_extracted_dict = {'embeddings_extracted': [], 'embeddings_names': []}
        self.model.to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            for image, name in tqdm(self.data_loader):
                image = image.to(self.device)

                embedding_extracted = self.model(image).squeeze().detach().cpu().numpy()
                embedding_extracted_dict['embeddings_extracted'].append(embedding_extracted)
                embedding_extracted_dict['embeddings_names'].append(name[0])

        if self.save_embedding_extracted:
            embeddings_path = os.path.join(self.kwargs.get('path_to_save_embeddings'), 'embeddings_extracted_with_model')
            embeddings_manager = EmbeddingsManagerEngine()
            embeddings_manager.save_embeddings(embeddings_path, embedding_extracted_dict)
            return embedding_extracted_dict
        else:
            return embedding_extracted_dict
        
