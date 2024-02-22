from PIL.Image import Image

def classify(image: Image, model: str, threshold: float = 0.7):
    if model == "YOLOv8":
        from yolo.YOLO import YOLOv8_cls
        from resources.label_list import image_net

        class_ids, confindence = YOLOv8_cls("../models/YOLOv8-cls.onnx", conf_thres=threshold)(
            image
        )
        if len(class_ids) == 0:
            return {}
        #turn class_ids tuple to list
        class_names = [image_net[class_id][1] for class_id in class_ids]
        dict_result = dict(zip(class_names, confindence))
        return dict_result
