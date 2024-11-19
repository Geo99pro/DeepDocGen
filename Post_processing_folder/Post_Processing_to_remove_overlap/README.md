<p align="center">
<a href="mailto: lhodonou349@gmail.com">
   <img alt="emal" src="https://img.shields.io/badge/contact_me-email-red">
</a>
</p>

# Post Processing to remove bounding boxe overlap in 2D space 🛠️

<!--<p align="center">
  <img width="800"  src="https://github.com/user-attachments/assets/a8e31ae8-aa7a-4813-aee3-e6f7d89fb079">
</p>-->

# Released 🚀

- [x] RemoveOverlappEngine
  - [x] load_json 
  - [x] create_dataframe
  - [x] generate_random_distance_delta
  - [x] compute_intersection_metas
  - [x] compute_bbox_area
  - [x] verify_overlap
  - [x] get_relative_position
  - [x] determine_overlap_side
  - [x] treat_b1_completely_overlapping_b2
  - [x] treat_b1_partially_overlapping_b2_on_left_top_corner
  - [x] treat_b1_partially_overlapping_b2_on_right_top_corner
  - [x] treat_b1_partially_overlapping_b2_on_left_bottom_corner
  - [x] treat_b1_partially_overlapping_b2_on_right_bottom_corner
  - [x] treat_b1_partially_overlapping_b2_on_center_top_corner
  - [x] treat_b1_partially_overlapping_b2_on_center_bottom_corner
  - [x] treat_b1_partially_overlapping_b2_on_left_center_corner
  - [x] treat_b1_partially_overlapping_b2_on_center_center_corner
  - [x] create_new_block
  - [x] choose_action_for_overlap_case
  - [x] remove_overlap
  - [x] reconstruct_normal_format
  - [x] create_image_after_correction
  - [x] convert_to_json

# How it works ❓
```python 
from Post_processing_Folder.Post_Processing_to_remove_document_overlap.remove_overlap_engine import RemoveOverlapEngine 
remover = RemoveOverlapEngine(layout_gen_annotation_path="./test_folder",
                               vmin=0.4,
                               vmax=0.5,
                               reconstruct_image_path="D:/Meus_codigos_de_mestrado/Synthetic_document_pipeline/Post_Processing_Folder/Post_Processing_to_remove_document_overlap",
                               reconstruct_annotation_path="D:/Meus_codigos_de_mestrado/Synthetic_document_pipeline/Post_Processing_Folder/Post_Processing_to_remove_document_overlap")
corrected_overlap = remover.remove_overlap()
reconstructed_data = remover.reconstruct_normal_format(corrected_dataframe=corrected_overlap)
remover.create_image_after_correction(reconstructed_data=reconstructed_data, type_of_format="PNG")
remover.convert_to_json(reconstructed_data=reconstructed_data)