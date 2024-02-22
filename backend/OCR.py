
def OCR(img_file, model: str) -> dict[str, str | float]:
    if model == "RapidOCR":
        from rapidOCR import process

        result = process(img_file)

        if result is None or len(result) == 0:
            return {"text": "", "confidence": 0.0}

        texts = [i[1] for i in result]
        confidences = [i[2] for i in result]

        text = " ".join(texts)
        confidence = sum(confidences) / len(confidences)

    return {
        "text": text,
        "confidence": confidence,
    }  # avoid same key if text is same
