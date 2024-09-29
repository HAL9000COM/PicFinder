import argparse
import os
import shutil
from pathlib import Path

from ultralytics import YOLO

if __name__ == "__main__":
    # get full or minimal models
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Download full models")
    args = parser.parse_args()
    if args.full:
        model_names = [
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
    else:
        model_names = [
            "yolov8n.pt",
            "yolov8n-cls.pt",
        ]
    os.makedirs(Path(__file__).parent.parent / "models", exist_ok=True)
    for model_name in model_names:
        model = YOLO(model_name)  # load a pretrained model (recommended for training)
        path = model.export(
            format="onnx", dynamic=True
        )  # export the model to ONNX format.
        shutil.move(
            path,
            f"{Path(__file__).parent.parent}/models/{model_name.replace('.pt','.onnx')}",
        )
