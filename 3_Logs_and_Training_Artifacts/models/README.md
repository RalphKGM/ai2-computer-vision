# Checkpoints

| File | Run | Source checkpoint |
|---|---|---|
| `apple_stage1.pt` | 21 | `best.pt`, YOLO26l-seg whole apple |
| `apple_stage2.pt` | 22 | `best.pt`, YOLO26l-seg three defects (tested checkpoint) |
| `tomato_stage1.pt` | 23 | `best.pt`, YOLO26l-seg whole tomato |
| `tomato_stage2.pt` | 24 | `best.pt` with the optimizer state removed (Ultralytics `strip_optimizer`). Same weights and predictions as the tested checkpoint |
| `apple_tomato_stage1.pt` | 25 | `best.pt`, YOLO26l-seg apple and tomato |
| `apple_tomato_stage2.pt` | 26 | `best.pt`, YOLO26l-seg three defects on both fruits (tested checkpoint) |

The original Run 24 `best.pt` with optimizer state (252 MB) is in Google Drive under
`MyDrive/YOLOv26/runs/tomato-stage2-defects-oct01/run24_20261001_115350/weights/best.pt`.
