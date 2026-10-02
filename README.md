# CIPHER AI2 Final Submission (AM3)

Computer Vision-Driven Two-Stage Instance Segmentation of Post-Harvest Surface Defects in Apple and Tomato Using YOLO26

Group CIPHER: Ralph Kevin G. Morales, Alexander Jann P. Espia, Deangelo James P. Largueza, Niel Francis M. Arligue
Adviser: Dr. Lysa V. Comia, Mapúa University

| Folder | Deliverable |
|---|---|
| `1_Documentation_IEEE/` | IEEE paper (.docx) |
| `2_Python_Notebook/` | Training and evaluation notebook (.ipynb) |
| `3_Logs_and_Training_Artifacts/` | `runs/` metrics, curves, confusion matrices and final test results, `models/` six checkpoints, `reports/` figures, `colab_raw_notebooks/` executed Colab notebooks |
| `4_Web_Deployment_Source/` and `4_Web_Deployment_Source.zip` | Streamlit app source |
| `5_PPT_Presentation/` | Final defense slides (.pptx) |
| `6_Dataset/` | Apple, tomato and combined datasets with README |

## Results (mask metrics, unseen test set)

| Model | Test mAP50 | Test precision | Test recall |
|---|---:|---:|---:|
| Apple, two-stage YOLO26l (Runs 21, 22) | 0.613 | 0.718 | 0.597 |
| Tomato, two-stage YOLO26l (Runs 23, 24) | 0.393 | 0.732 | 0.375 |
| One model for both, apple test (Runs 25, 26) | 0.586 | 0.769 | 0.591 |
| One model for both, tomato test (Runs 25, 26) | 0.352 | 0.533 | 0.416 |

## Links

- App source repository: https://github.com/deangg/instancesegmentation (branch `final-defense`)
- Full Colab run folders: Google Drive `MyDrive/YOLOv26/runs/`

## Run the app locally

```bash
cd 4_Web_Deployment_Source
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../3_Logs_and_Training_Artifacts/models/*.pt models/
streamlit run streamlit_app.py
```
