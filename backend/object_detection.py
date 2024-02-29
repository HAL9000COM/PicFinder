import numpy
from PIL.Image import Image


def object_detection(
    image: Image,
    model: str,
    conf_threshold: float = 0.7,
    iou_threshold: float = 0.5,
):
    if model == "YOLOv8":
        from resources.label_list import coco
        from yolo.YOLO import YOLOv8

        _, scores, class_ids = YOLOv8(
            "../models/YOLOv8.onnx", conf_threshold, iou_threshold
        )(image)

        if len(class_ids) == 0:
            return None

        class_names = [coco[class_id] for class_id in class_ids]
        result = [
            (class_name, scores[class_names.index(class_name)])
            for class_name in class_names
        ]

        return result

    elif model == "YOLOv8-oiv7":
        from resources.label_list import open_images_v7
        from yolo.YOLO import YOLOv8

        _, scores, class_ids = YOLOv8(
            "../models/YOLOv8-oiv7.onnx", conf_threshold, iou_threshold
        )(image)

        if len(class_ids) == 0:
            return None

        class_names = [open_images_v7[class_id] for class_id in class_ids]
        result = [
            (class_name, scores[class_names.index(class_name)])
            for class_name in class_names
        ]
        return result
