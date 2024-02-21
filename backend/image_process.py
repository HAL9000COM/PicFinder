#%%

import numpy
import cv2
import xxhash
#%%
def read_img(img_path,classification=True,object_detection=True,OCR=True,**kwargs):

    with open (img_path, 'rb') as file:
        img_hash=xxhash.xxh3_64_hexdigest(file.read())

    # Read the image with OpenCV
    img = cv2.imread(img_path)
    # Convert the image from BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    res_dict={}
    res_dict["hash"]=img_hash
    if classification:
        # Perform classification
        import classification
        class_dict=classification.classify(img, "YOLOv8", 0.2)
        res_dict["classification"]=class_dict
    if object_detection:
        # Perform object detection
        import object_detection
        obj_dict=object_detection.object_detection(img, "YOLOv8", 0.7, 0.5)
        res_dict["object_detection"]=obj_dict
    if OCR:
        # Perform OCR
        import OCR
        OCR_dict=OCR.OCR(img, "RapidOCR")
        res_dict["OCR"]=OCR_dict
    
    return res_dict