# Dataset

Three YOLO instance segmentation datasets used for the final models. Each folder has `data.yaml`, `manifest.json`
(one row per image with split, source and capture group), `audit.json` and `train`, `valid`, `test` and
`test_reserve` folders with `images` and `labels`.

| Folder | Used by | Train | Valid | Test | Reserve |
|---|---|---:|---:|---:|---:|
| `apple-sep30-fruit9` | Apple Runs 21 and 22 | 2,110 | 215 | 79 | 63 |
| `tomato-sep29-source-oct01` | Tomato Runs 23 and 24 | 1,313 | 132 | 95 | 39 |
| `apple-tomato-source-oct01` | Combined Runs 25 and 26 | 3,423 | 347 | 174 | 102 |

The combined set is the apple and tomato sets merged without reshuffling. No image changes split.

## Classes

`apple` or `tomato` (whole fruit, Stage 1) and `bruise_discoloration`, `rot_mold_decay`, `surface_damage`
(defects, Stage 2). The Colab notebook derives the Stage 1 and Stage 2 label views from these source folders without
changing images or polygons.

## Labels and sources

- Every pixel mask was drawn and reviewed by the team in Roboflow.
- Apple images: AFruitDB grading photos (Mojumdar et al. 2025, Data in Brief 59, 111380), the Lab2Wild apple rot set
  by S. Nesteruk on Kaggle (CC BY-NC-SA 4.0) and team photos. AFruitDB grade folders are image-level labels and were
  not used as targets.
- Tomato images: AFruitDB grading photos (Mojumdar et al. 2025). Grade folders were not used as targets.
- Derived masks on Lab2Wild images follow its CC BY-NC-SA 4.0 license.

## Splits and leakage

- Splits are by capture group. Roboflow training exports hold up to three augmented variants of a photo so file
  counts are not counts of distinct photos.
- `test_reserve` was never used for training, selection or testing.

## Checksums

| Folder | Archive SHA-256 used in Colab |
|---|---|
| `apple-sep30-fruit9` | `779e8d8cb90aa25b4a83b2a6be99b0fc6ea6417426f3cc58488a4850ac0ac85e` |
| `tomato-sep29-source-oct01` | `0f7093ee63dffe610ee837a332d75613375af217b513a43ffe317be0a3df9155` |
| `apple-tomato-source-oct01` | `1bc76dc6eb6db1eedfe5bdf439cc8409b1eb6f8d62f76ea659a3753397e8e5d2` |
