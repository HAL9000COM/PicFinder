# -*- coding: utf-8 -*-

import hashlib
import io
import logging
import sys
from multiprocessing import Pool
from pathlib import Path

from PIL import Image

from backend.rapidOCR import process as rapidOCRprocess
from backend.resources.label_list import coco, open_images_v7
from backend.yolo import YOLOv8


def classify(image: Image.Image, model: str, threshold: float = 0.7):
    if model == "yolov8":
        from backend.resources.label_list import image_net
        from backend.yolo.YOLO import YOLOv8Cls

        YOLOv8_cls_path = Path(sys.argv[0]).parent / "models" / "yolov8-cls.onnx"

        class_ids, confidence = YOLOv8Cls(YOLOv8_cls_path, conf_thres=threshold)(image)
        if len(class_ids) == 0:
            return None

        class_names = [image_net[class_id][1] for class_id in class_ids]
        result = [
            (class_name, confidence[class_names.index(class_name)])
            for class_name in class_names
        ]
        return result
    else:
        return None


def object_detection(
    image: Image.Image,
    model: str,
    conf_threshold: float = 0.7,
    iou_threshold: float = 0.5,
):
    if model == "yolov8":

        YOLOv8_COCO_path = Path(sys.argv[0]).parent / "models" / "yolov8.onnx"

        _, scores, class_ids = YOLOv8(YOLOv8_COCO_path, conf_threshold, iou_threshold)(
            image
        )

        if len(class_ids) == 0:
            return None

        class_names = [coco[class_id] for class_id in class_ids]
        result = [
            (class_name, scores[class_names.index(class_name)])
            for class_name in class_names
        ]

        return result

    elif model == "yolov8-oiv7":

        YOLOv8_OIV7_path = Path(sys.argv[0]).parent / "models" / "yolov8-oiv7.onnx"
        _, scores, class_ids = YOLOv8(YOLOv8_OIV7_path, conf_threshold, iou_threshold)(
            image
        )

        if len(class_ids) == 0:
            return None

        class_names = [open_images_v7[class_id] for class_id in class_ids]
        result = [
            (class_name, scores[class_names.index(class_name)])
            for class_name in class_names
        ]
        return result
    else:
        return None


def OCR(img_file, model: str):
    if model == "RapidOCR":

        result = rapidOCRprocess(img_file)

        if result is None or len(result) == 0:
            return None

        res = [(i[1], i[2]) for i in result]

        return res
    else:
        return None


# %%
def read_img(
    img_path: Path,
    classification_model="yolov8",
    classification_threshold=0.7,
    object_detection_model="yolov8",
    object_detection_conf_threshold=0.7,
    object_detection_iou_threshold=0.5,
    OCR_model="RapidOCR",
):
    try:

        with open(img_path, "rb") as file:
            img_file = file.read()
            # get md5 hash of image
            img_hash = hashlib.md5(img_file).hexdigest()

        # read image with pillow
        try:
            img = Image.open(io.BytesIO(img_file))
        except Exception as e:
            return {"error": str(e)}

        res_dict = {}
        res_dict["hash"] = img_hash
        res_dict["path"] = img_path.as_posix()

        cls_res = classify(img, classification_model, classification_threshold)
        res_dict["classification"] = cls_res

        obj_res = object_detection(
            img,
            object_detection_model,
            object_detection_conf_threshold,
            object_detection_iou_threshold,
        )
        res_dict["object_detection"] = obj_res

        OCR_res = OCR(img_file, OCR_model)
        res_dict["OCR"] = OCR_res

        return res_dict
    except Exception as e:
        logging.error(f"Exception:{e},Img_path:{img_path}", exc_info=True)
        return {"error": str(e)}


def read_img_warper(args: tuple):
    path, kwargs = args
    return read_img(path, **kwargs)
