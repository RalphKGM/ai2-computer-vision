# apple-tomato-source-oct01

Classes: apple, tomato, bruise_discoloration, rot_mold_decay, surface_damage

Image bytes, polygon coordinates, and frozen split assignments retained. No new augmentations created.

Training contains Roboflow augmentation variants, not only distinct source photos. Recorded source capture groups are filename groups, not verified physical-fruit identities. Existing frozen validation/test/reserve assignments are preserved, not reshuffled to enforce a new 70/20/10 ratio. test_reserve is excluded from data.yaml.

Stage 1 includes damaged and healthy-looking fruit. Stage 2 contains defect masks and keeps empty labels as negative examples. Empty annotations do not prove the image is healthy. These are converted existing team annotations; human completeness review is still needed. Stage 2 uses complete images, not automatically cropped fruit.

Roboflow export attribution and licenses (CC BY 4.0 as declared) are included. Verify underlying image provenance before publication. Original image-level grades are distinct from team-created pixel annotations.

Extract each ZIP to its own directory. Use its data.yaml. Use new combined run IDs and initialize combined Stage 2 from a completed combined Stage 1 checkpoint of the same model architecture. Do not resume an apple-only or tomato-only run on this changed dataset. Test is reserved for final evaluation after choices are frozen.
