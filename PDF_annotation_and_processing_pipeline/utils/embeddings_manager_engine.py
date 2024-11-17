import pickle

class EmbeddingsManagerEngine:
    """
    This class is responsible for managing the embeddings. It can save and load the embeddings.
    By calling this EmbeddingsManagerEngine, user creates an instance of this class.

    Attributes:

        path (str): is the path to save or load the embeddings.
        element (any): is the element to be saved or loaded.

    Methods:

        save_embeddings(self): Saves the embeddings to the path
        load_embeddings(self): Loads the embeddings from the path
    """

    def __init__(self, path: str, element: any):
        self.path = path
        self.element = element

    def save_embeddings(self):
        with open(f'{self.path}.pkl', 'wb') as file:
            pickle.dump(self.element, file)

    def load_embeddings(self):
        with open(f'{self.path}.pkl', 'rb') as file:
            self.element = pickle.load(file)
        return self.element