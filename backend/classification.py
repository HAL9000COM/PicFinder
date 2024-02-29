# -*- coding: utf-8 -*-

from PIL.Image import Image


def classify(image: Image, model: str, threshold: float = 0.7):
    if model == "YOLOv8":
        from resources.label_list import image_net
        from yolo.YOLO import YOLOv8_cls

        class_ids, confidence = YOLOv8_cls(
            "../models/YOLOv8-cls.onnx", conf_thres=threshold
        )(image)
        if len(class_ids) == 0:
            return None

        class_names = [image_net[class_id][1] for class_id in class_ids]
        result = [
            (class_name, confidence[class_names.index(class_name)])
            for class_name in class_names
        ]
        return result
