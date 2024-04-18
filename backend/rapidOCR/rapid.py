# -*- coding: utf-8 -*-

from rapidocr_onnxruntime import RapidOCR


def process(img):
    engine = RapidOCR()

    result, elapse = engine(img, use_det=True, use_cls=True, use_rec=True)
    return result
