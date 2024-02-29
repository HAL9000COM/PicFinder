# -*- coding: utf-8 -*-


def OCR(img_file, model: str):
    if model == "RapidOCR":
        from rapidOCR import process

        result = process(img_file)

        if result is None or len(result) == 0:
            return None

        res = [(i[1], i[2]) for i in result]

        return res
