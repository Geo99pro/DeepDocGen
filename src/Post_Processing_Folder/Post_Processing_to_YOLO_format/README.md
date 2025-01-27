# Post Processing to YOLO format 🤹

The ```Post Processing to YOLO Format``` tool is designed to streamline the pre-processing of annotated images (including document images or others) that are already in [COCO format](https://cocodataset.org/#home), converting them into the [YOLO format](https://docs.ultralytics.com/fr/datasets/detect/) for training YOLO models. This tool offers the following functionalities:

- ```Convert annotations from COCO format to YOLO format```
- ```Split datasets into training, validation, and test sets```
- ```Manage files and folders to streamline dataset preparation```

## Features
1. **Convert COCO to YOLO:**
   - Converts document annotations from COCO format to YOLO format while normalizing bounding boxes and adjusting category IDs.

2. **Dataset Splitting:**
   - Splits datasets into train, validation, and test subsets with user-defined proportions.

## How it works ❓

### 1. Convert COCO to YOLO

Use the `convert_coco_to_yolo` function to convert document annotations **(or others)**:

```python
from src.Post_Processing_Folder.Post_Processing_to_YOLO_format.yolo_mapping_engine import convert_coco_to_yolo

convert_coco_to_yolo(annotations_folder_path="path/to/coco/annotations",
                    output_folder_path="path/to/output",
                    desired_folder_name="yolo_annotations")
```

### 2. Split Dataset

Use the `split_dataset` function to split your dataset **(can be before converting to YOLO format or after)**:

```python
from src.Post_Processing_Folder.Post_Processing_to_YOLO_format.yolo_mapping_engine import split_dataset

split_dataset(images_folder_path="path/to/images",
              annotations_folder_path="path/to/yolo/annotations", #"path/to/coco/annotations"
              output_folder_path="path/to/output",
              desired_folder_name="split_dataset",
              test_size=0.2,
              random_state=42)
```

## Folder Structure
Ensure your dataset follows this structure:

```
project/
│
├── images/
│   ├── image1.jpg
│   ├── image2.png
│
├── annotations/
│   ├── annotation1.json
│   ├── annotation2.json
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contribution
Feel free to contribute by submitting issues or pull requests. For major changes, please open an issue to discuss your proposal.

## Author
Loick Geoffrey Hodonou

For inquiries, contact me at: lhodonou349@gmail.com.