# tomato-sep29-source-oct01

Classes: tomato, bruise_discoloration, rot_mold_decay, surface_damage.

YOLO instance-segmentation polygons, not bounding-box labels. All selected polygon coordinates and image bytes are unchanged. Validation, test, and test_reserve assignments remain frozen from the prior project dataset. test_reserve is omitted from data.yaml and is not an active evaluation set.

Training images already include Roboflow augmentation variants. File counts are not counts of distinct original photos. Recorded capture groups are source filename groups, not independently verified physical-fruit identities.

Stage 1 retains whole-tomato masks on healthy-looking and damaged tomatoes. Stage 2 retains all three defect classes separately and keeps empty labels as negative examples. An empty label does not prove a tomato is healthy. Review annotation completeness before interpreting those examples.

Source: https://universe.roboflow.com/deangelo-largueza/post-harvest-fruit-surface-defec-2
Export declares CC BY 4.0; attribution files are included. Team-created pixel annotations are distinct from original image-level grades. Underlying image provenance must be verified for publication.

Extract each archive into its own directory, and use that directory/data.yaml. Stage 2 is a fresh training stage initialized from the completed Stage 1 best.pt of the same model size. Resume an interrupted stage from its own last.pt.
