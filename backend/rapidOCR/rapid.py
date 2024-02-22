from rapidocr_onnxruntime import RapidOCR


def process(img_file):
    engine = RapidOCR()

    result, elapse = engine(img_file, use_det=True, use_cls=True, use_rec=True)
    return result
