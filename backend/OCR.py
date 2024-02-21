import numpy


def OCR(img: numpy.ndarray, model: str):
    if model == "RapidOCR":
        from rapidOCR import process

        result = process(img)

        if result is None or len(result) == 0:
            return None

        texts = [i[1] for i in result]
        confidences = [i[2] for i in result]

        text = " ".join(texts)
        confidence = sum(confidences) / len(confidences)

        return {"text": text, "confidence": confidence}
