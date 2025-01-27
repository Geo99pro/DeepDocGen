# Post Processing code to PubLayNet format

<p align="center">
  <img width="700"  src="https://github.com/user-attachments/assets/39e699d5-7968-4fa1-b8bf-cc9992a9022d">
</p>

# Released

- [x] PublaynetMappingEngine
  - [x] load_vott_json
  - [x] save_publaynet_json
  - [x] extract_vott_categories
  - [x] extract_image_metas
  - [x] extract_blocks_coordinates
  - [x] map_vott_to_publaynet

# How it works ❓
```python
from Post_Processing_Folder.Post_Processing_to_PubLayNet_format.publyanet_mapping_engine import PublaynetMappingEngine

PubLayNet_format = PublaynetMappingEngine(vott_json_path=vott_json_path,
                                          image_meta_id=image_meta_id,
                                          annotation_id_start=annotation_id_start,
                                          path_to_save=path_to_save,
                                          desired_name=desired_name)
```