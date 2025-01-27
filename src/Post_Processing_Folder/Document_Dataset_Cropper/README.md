# Document Dataset Region Cropper 🪚

This project provides a utility for cropping regions in document dataset images according to their respective annotations and subsequently saving them in a structured folder format. The cropped images are organized into sub-folders according to their type, representing the IMAGENET format.

## Supported Document Dataset 🧮

- [PublyaNet](https://github.com/ibm-aur-nlp/PubLayNet)
- [DocLayNet](https://github.com/DS4SD/DocLayNete)
- [DocBank](https://github.com/doc-analysis/DocBank)

## How it works ❓

To use the dataset region cropper, you need to call the ```crop_regions``` function from ```dataset_region_cropper.py``` with the appropriate arguments. Here is an example:

```python
from src.Post_Processing_Folder.Dataset_Cropper.dataset_region_cropper import crop_regions

crop_regions(dataset_name='publaynet',
            image_folder_path='/path/to/images',
            image_extension='jpg',
            annotation_folder_path='/path/to/annotations',
            output_folder_path='/path/to/output',
            desired_output_folder_name='cropped_images')
```