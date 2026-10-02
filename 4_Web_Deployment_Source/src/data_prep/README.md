# Dataset preparation scripts

Scripts used to build the frozen apple dataset and the two label views for Stage 1 and Stage 2.
Paths inside point to the original project layout (data/raw and data/pilots).

- convert_roboflow_coco_to_yolo_seg.py: Roboflow COCO polygons to YOLO segmentation labels
- build_sep29_fruit_dataset.py: capture-group keys and the frozen validation, test and reserve splits
- build_apple_sep30.py: final apple dataset with the frozen held-out images
- prepare_two_stage_apple.py: Stage 1 apple view and Stage 2 three-defect view
