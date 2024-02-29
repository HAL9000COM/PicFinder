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

        cls_res = classification.classify(img, "YOLOv8", 0.2)
        res_dict["classification"] = cls_res
    if object_detection:
        # Perform object detection
        import object_detection

        obj_res = object_detection.object_detection(img, "YOLOv8", 0.7, 0.5)
        res_dict["object_detection"] = obj_res
    if OCR:
        # Perform OCR
        import OCR

        OCR_res = OCR.OCR(img_file, "RapidOCR")
        res_dict["OCR"] = OCR_res

    return res_dict
