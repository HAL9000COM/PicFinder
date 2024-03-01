# -*- coding: utf-8 -*-

import io
from multiprocessing import Pool
from pathlib import Path

import xxhash
from PIL import Image


def classify(image: Image.Image, model: str, threshold: float = 0.7):
    if model == "YOLOv8":
        from backend.resources.label_list import image_net
        from backend.yolo.YOLO import YOLOv8_cls

        YOLOv8_cls_path = (
            Path(__file__).resolve().parent.parent / "models" / "YOLOv8-cls.onnx"
        )
        class_ids, confidence = YOLOv8_cls(YOLOv8_cls_path, conf_thres=threshold)(image)
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
    if model == "YOLOv8":
        from backend.resources.label_list import coco
        from backend.yolo import YOLOv8

        YOLOv8_COCO_path = (
            Path(__file__).resolve().parent.parent / "models" / "YOLOv8.onnx"
        )

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

    elif model == "YOLOv8-oiv7":
        from backend.resources.label_list import open_images_v7
        from backend.yolo import YOLOv8

        YOLOv8_OIV7_path = (
            Path(__file__).resolve().parent.parent / "models" / "YOLOv8-oiv7.onnx"
        )
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
        from backend.rapidOCR import process

        result = process(img_file)

        if result is None or len(result) == 0:
            return None

        res = [(i[1], i[2]) for i in result]

        return res
    else:
        return None


# %%
def read_img(
    img_path: Path,
    classification_model="YOLOv8",
    classification_threshold=0.7,
    object_detection_model="YOLOv8",
    object_detection_conf_threshold=0.7,
    object_detection_iou_threshold=0.5,
    OCR_model="RapidOCR",
):

    with open(img_path, "rb") as file:
        img_file = file.read()
        img_hash = xxhash.xxh3_64_hexdigest(img_file)

    # read image with pillow
    try:
        img = Image.open(io.BytesIO(img_file))
    except Exception as e:
        return {"error": str(e)}

    res_dict = {}
    res_dict["path"] = img_path
    res_dict["hash"] = img_hash

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


def read_folder(folder_path: Path, **kwargs):
    # list all files in the folder and subfolders
    file_list = folder_path.rglob("*")
    input_list = [[file, kwargs] for file in file_list if file.is_file()]
    p = Pool()
    res = p.starmap(read_img, input_list)
    p.close()
    return res
