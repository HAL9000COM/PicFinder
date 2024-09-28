# %%
!pip install ultralytics onnx
#%%
from ultralytics import YOLO
import shutil
import os
# %%
model_names=[
    "yolov8n.pt",
    "yolov8s.pt",
    "yolov8m.pt",
    "yolov8l.pt",
    "yolov8x.pt",
    "yolov8n-cls.pt",
    "yolov8s-cls.pt",
    "yolov8m-cls.pt",
    "yolov8l-cls.pt",
    "yolov8x-cls.pt",
    "yolov8n-oiv7.pt",
    "yolov8s-oiv7.pt",
    "yolov8m-oiv7.pt",
    "yolov8l-oiv7.pt",
    "yolov8x-oiv7.pt",
]
#%%
for model_name in model_names:
    model = YOLO(model_name)  # load a pretrained model (recommended for training)
    path = model.export(format="onnx",dynamic=True)  # export the model to ONNX format

# %%
#copy the models to the src/models
os.makedirs("../models",exist_ok=True)
for model_name in model_names:
    shutil.move(model_name.replace(".pt",".onnx"),f"../models/{model_name.replace('.pt','.onnx')}")
    # os.remove(model_name)
