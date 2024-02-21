import numpy

def classify_image(image: numpy.ndarray, model: str, threshold: float = 0.7):
    if model == "YOLOv8":
        from yolo.YOLO import YOLOv8_cls
        from resources.label_list import image_net

        class_ids, confindence = YOLOv8_cls("models/YOLOv8-cls.onnx", threshold)(image)
        if len(class_ids) == 0:
            return None
        class_names = [image_net[class_id][1] for class_id in class_ids]
        dict_result = dict(zip(class_names, confindence))
        return dict_result
