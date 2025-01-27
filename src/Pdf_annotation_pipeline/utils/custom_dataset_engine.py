
import os
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class CustomDatasetEngine(Dataset):
    """
    This class is used to create a custom dataset for the images.
    By calling this Custom_Dataset, user creates an instance of this class.
    It receives the image paths and the transform to perform, opens each image, 
    extracts the name of the image, converts it to RGB, applies the transform on it,
    and returns a tuple containing the transformed image and its name.

    Attributes:
        image_path_list (list): is the list of images path.
        transform (object): is the object of the transform class.

    Methods:
    
        __init__(self, image_list, transform=None): This function initializes the class.
        __len__(self): This function returns the length of the image list.
        __getitem__(self, idx): This function returns the transformed image and its name.
    
    Returns:
        image (tuple): is the tuple containing the transformed image and its name.
    """
    @staticmethod
    def transform_image(shape_resize: tuple):
        transform = transforms.Compose([
            transforms.Resize(shape_resize),
            transforms.CenterCrop(shape_resize[0]),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        return transform

    def __init__(self, image_list, shape_resize: tuple =(224,224), transform=None):
        self.image_list = image_list
        self.shape_resize = shape_resize

        if transform is None:
            self.transform = self.transform_image(self.shape_resize)
        else:
            self.transform = transform

    def __len__(self):
        return len(self.image_list)

    def __getitem__(self, index):
        image_path = self.image_list[index]
        image_name = os.path.basename(image_path).split('.')[0]
        image = Image.open(image_path).convert('RGB')
        image_normalized = self.transform(image)
        return image_normalized, image_name

