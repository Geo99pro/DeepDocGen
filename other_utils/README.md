<p align="center">
<a href="mailto: lhodonou349@gmail.com">
   <img alt="emal" src="https://img.shields.io/badge/contact_me-email-red">
</a>
</p>

# 1. Document Dataset Regions Cropper 🪚
The function `crop_regions` from `document_dataset_region_cropper.py` crops the regions of the images based on the annotation files. It's designed to work with the following datasets:

1. **PublyaNet** : A dataset for document layout analysis. [Paper](https://arxiv.org/abs/1908.07836) | [Repo](https://github.com/ibm-aur-nlp/PubLayNet) | [Download](https://developer.ibm.com/exchanges/data/all/publaynet/)
2. **DoclyaNet** : A dataset for document layout analysis. [Paper](https://arxiv.org/abs/2206.01062) | [Repo](https://github.com/DS4SD/DocLayNet) | [Download](https://developer.ibm.com/exchanges/data/all/doclaynet/) 
3. **DocBank** : A comprehensive dataset for document understanding. [Paper](https://arxiv.org/abs/2206.01062) | [Repo](https://github.com/DS4SD/DocLayNet) | [Download](https://developer.ibm.com/exchanges/data/all/doclaynet/) 

## How it works 🧮
To use this function, ensure that you have the appropriate annotation files for the datasets mentioned above. The function will process these files and crop the specified regions from the images.

## Example
Here is an example of how to use the `crop_regions` function from the ``document_dataset_region_cropper.py`` :

```python
from document_dataset_region_cropper import crop_regions

images_folder_path = 'path_to_images_folder'
annotation_folder_path = 'path_to_annotations_folder'
path_to_save_cropped_images = 'path_to_save_cropped_images'
which_public_dataset = 'publyanet'
crop_regions(images_folder_path,
            annotation_folder_path,
            path_to_save_cropped_images, 
            which_public_dataset)
```

# 2. SwinTransformer fine-tuner
The function `fine_tune_swin_transformer` from `swinTransformer_fine_tune.py` is used to fine tune the [Swin-T](https://github.com/microsoft/Swin-Transformer) model so that it can be used as an embedding extractor or classifier. 

## How it works 🧮
Here is an example of how to use the `fine_tune_swin_transformer` function from the ``swinTransformer_fine_tune.py`` :

```python

from swinTransformer_fine_tune import fine_tune_swin_transformer

# Combination of transformations required
transform = transforms.Compose([transforms.Resize((224, 224))
                                transforms.ToTensor(),
                                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
train_dataset_path = 'path_to_train_images_folder'
val_dataset_path = 'path_to_val_images_folder'
transform = transform
model_weights_path = 'path_to_model_weights'
lr = 0.001
which_scheduler = 'StepLR'
num_epoch = 30
batch_size = 32
path_to_save_fine_tuned_model = str,
desired_model_name = str,
step_size = 8
gamma = 0.1
fine_tune_swin_transformer(train_dataset_path, val_dataset_path,
                           transform, model_weights_path,
                           lr, which_scheduler,
                           num_epochs, batch_size,
                           path_to_save_fine_tuned_model, step_size, gamma)
```


## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For any questions or issues, please open an issue on the GitHub repository.
