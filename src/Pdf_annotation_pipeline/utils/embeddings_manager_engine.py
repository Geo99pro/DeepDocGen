import pickle

class EmbeddingsManagerEngine:
    """
    This class is responsible for managing the embeddings. It can save and load the embeddings.
    By calling this EmbeddingsManagerEngine, user creates an instance of this class.

    Methods:
    
        - save_embeddings: Saves the embeddings to the path
        - load_embeddings: Loads the embeddings from the path
    """

    def save_embeddings(self, path: str, data: any):
        with open(f'{path}.pkl', 'wb') as file:
            pickle.dump(data, file)

    def load_embeddings(self, path: str):
        with open(f'{path}.pkl', 'rb') as file:
            data = pickle.load(file)
        return data