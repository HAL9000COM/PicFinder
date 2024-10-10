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
            "yolo11n.pt",
            "yolo11s.pt",
            "yolo11m.pt",
            "yolo11l.pt",
            "yolo11x.pt",
            "yolo11n-cls.pt",
            "yolo11s-cls.pt",
            "yolo11m-cls.pt",
            "yolo11l-cls.pt",
            "yolo11x-cls.pt",
        ]
    else:
        model_names = [
            "yolo11n.pt",
            "yolo11n-cls.pt",
        ]
    os.makedirs(Path(__file__).parent.parent / "models", exist_ok=True)
    for model_name in model_names:
        model = YOLO(model_name)  # load a pretrained model (recommended for training)
        path = model.export(
            format="onnx", dynamic=False
        )  # export the model to ONNX format.
        shutil.move(
            path,
            f"{Path(__file__).parent.parent}/models/{model_name.replace('.pt','.onnx')}",
        )
