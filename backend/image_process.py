# %%

import io

import xxhash
from PIL import Image


# %%
def read_img(img_path, classification=True, object_detection=True, OCR=True, **kwargs):

    with open(img_path, "rb") as file:
        img_file = file.read()
        img_hash = xxhash.xxh3_64_hexdigest(img_file)

    # read image with pillow

    img = Image.open(io.BytesIO(img_file))

    res_dict = {}
    res_dict["hash"] = img_hash
    if classification:
        # Perform classification
        import classification

        class_dict = classification.classify(img, "YOLOv8", 0.2)
        if class_dict is None:
            res_dict["classification"] = ""
        else:
            res_dict["classification"] = " ".join(class_dict.keys())
    if object_detection:
        # Perform object detection
        import object_detection

        obj_dict = object_detection.object_detection(img, "YOLOv8", 0.7, 0.5)
        if obj_dict is None:
            res_dict["object_detection"] = ""
        else:
            res_dict["object_detection"] = " ".join(obj_dict.keys())
    if OCR:
        # Perform OCR
        import OCR

        OCR_dict = OCR.OCR(img_file, "RapidOCR")
        res_dict["OCR"] = OCR_dict["text"]

    return res_dict
