# -*- coding: utf-8 -*-

import hashlib
import io
import logging
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

from backend.rapidOCR import process as rapidOCRprocess
from backend.resources.label_list import coco, open_images_v7
from backend.yolo import YOLOv8

is_nuitka = "__compiled__" in globals()

if is_nuitka or getattr(sys, "frozen", False):
    models_dir = Path(sys.argv[0]).parent / "models"
else:
    models_dir = Path(__file__).resolve().parent.parent / "models"


def classify(image: np.ndarray, model: str, threshold: float = 0.7):
    from backend.resources.label_list import image_net
    from backend.yolo.YOLO import YOLOv8Cls

    match model:
        case "YOLOv8n":
            YOLOv8_path = models_dir / "yolov8n-cls.onnx"
        case "YOLOv8s":
            YOLOv8_path = models_dir / "yolov8s-cls.onnx"
        case "YOLOv8m":
            YOLOv8_path = models_dir / "yolov8m-cls.onnx"
        case "YOLOv8l":
            YOLOv8_path = models_dir / "yolov8l-cls.onnx"
        case "YOLOv8x":
            YOLOv8_path = models_dir / "yolov8x-cls.onnx"
        case _:
            return None
    class_ids, confidence = YOLOv8Cls(YOLOv8_path, conf_thres=threshold)(image)
    if len(class_ids) == 0:
        return None
    class_names = [image_net[class_id][1] for class_id in class_ids]
    result = [
        (class_name, confidence[class_names.index(class_name)])
        for class_name in class_names
    ]
    return result


def object_detection(
    image: np.ndarray,
    model: str,
    conf_threshold: float = 0.7,
    iou_threshold: float = 0.5,
):
    match model:
        case "YOLOv8n COCO":
            YOLOv8_path = models_dir / "yolov8n.onnx"
            class_name_list = coco

        case "YOLOv8s COCO":
            YOLOv8_path = models_dir / "yolov8s.onnx"
            class_name_list = coco

        case "YOLOv8m COCO":
            YOLOv8_path = models_dir / "yolov8m.onnx"
            class_name_list = coco

        case "YOLOv8l COCO":
            YOLOv8_path = models_dir / "yolov8l.onnx"
            class_name_list = coco

        case "YOLOv8x COCO":
            YOLOv8_path = models_dir / "yolov8x.onnx"
            class_name_list = coco

        case "YOLOv8n Open Images v7":
            YOLOv8_path = models_dir / "yolov8n-oiv7.onnx"
            class_name_list = open_images_v7

        case "YOLOv8s Open Images v7":
            YOLOv8_path = models_dir / "yolov8s-oiv7.onnx"
            class_name_list = open_images_v7

        case "YOLOv8m Open Images v7":
            YOLOv8_path = models_dir / "yolov8m-oiv7.onnx"
            class_name_list = open_images_v7

        case "YOLOv8l Open Images v7":
            YOLOv8_path = models_dir / "yolov8l-oiv7.onnx"
            class_name_list = open_images_v7

        case "YOLOv8x Open Images v7":
            YOLOv8_path = models_dir / "yolov8x-oiv7.onnx"
            class_name_list = open_images_v7

        case _:
            return None

    _, scores, class_ids = YOLOv8(YOLOv8_path, conf_threshold, iou_threshold)(image)
    if len(class_ids) == 0:
        return None
    class_names = [class_name_list[class_id] for class_id in class_ids]
    result = [
        (class_name, scores[class_names.index(class_name)])
        for class_name in class_names
    ]
    return result


def OCR(img, model: str):
    if model == "RapidOCR":

        result = rapidOCRprocess(img)

        if result is None or len(result) == 0:
            return None

        res = [(i[1], i[2]) for i in result]

        return res
    else:
        return None


# %%
def read_img(
    img_path: Path,
    classification_model="YOLOv8n",
    classification_threshold=0.7,
    object_detection_model="YOLOv8n COCO",
    object_detection_conf_threshold=0.7,
    object_detection_iou_threshold=0.5,
    OCR_model="RapidOCR",
    **kwargs,
):
    try:

        with open(img_path, "rb") as file:
            img_file = file.read()
            # get md5 hash of image
            img_hash = hashlib.md5(img_file).hexdigest()

        # read image with cv2
        try:
            img = cv2.imread(img_path.as_posix())
        except Exception as e:
            return {"error": str(e)}

        res_dict = {}
        res_dict["hash"] = img_hash
        res_dict["path"] = img_path.as_posix()

        if classification_model != "None":
            cls_start = time.perf_counter()

            cls_res = classify(img, classification_model, classification_threshold)
            res_dict["classification"] = cls_res

            cls_end = time.perf_counter()
            logging.debug(
                f"Image:{img_path.as_posix()},Classification Time: {cls_end-cls_start}"
            )

        if object_detection_model != "None":
            obj_start = time.perf_counter()

            obj_res = object_detection(
                img,
                object_detection_model,
                object_detection_conf_threshold,
                object_detection_iou_threshold,
            )
            res_dict["object_detection"] = obj_res

            obj_end = time.perf_counter()
            logging.debug(
                f"Image:{img_path.as_posix()},Object Detection Time: {obj_end-obj_start}"
            )

        if OCR_model != "None":
            OCR_start = time.perf_counter()

            OCR_res = OCR(img, OCR_model)
            res_dict["OCR"] = OCR_res

            OCR_end = time.perf_counter()
            logging.debug(f"Image:{img_path.as_posix()},OCR Time: {OCR_end-OCR_start}")

        return res_dict
    except Exception as e:
        logging.error(f"Exception:{e},Img_path:{img_path}", exc_info=True)
        return {"error": str(e)}


def read_img_warper(args: tuple):
    path, kwargs = args
    return read_img(path, **kwargs)
