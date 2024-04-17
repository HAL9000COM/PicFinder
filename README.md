# PicFinder

A simple windows application to search for images in a directory.

## Features

* Search for text in images using OCR. Tested with English, Traditional Chinese, Simplified Chinese, Japanese.
* Search for objects in images using YOLOv8. Labels from COCO or Open Image V7.
* Search for images using its class. Labels from ImageNet.
* Supported image formats: bmp, jpg, jpeg, j2k, jp2, jpx, png, gif, tiff, tif, webp, ico.

## Usage

1. Download the latest release
2. Run the application
3. Select the directory to Index using models (only required once)
4. Search

If you clone the repository:

1. Install the required packages using Poetry.
2. Put the ONNX format YOLOv8 models in the `models` directory.

### Note

 The first time you run the application, it will take some time to index the images in the directory.

 Only YOLOv8n and YOLOv8n COCO models are included in the minimal release. For more models, download the ONNX format models and put them in the `models` directory.

## EXE creation

1. Using cx_Freeze

    ```bash
    python dist.py build
    ```

2. Using Nuitka

    ```bash
    python -m nuitka main.py --standalone --enable-plugin=pyside6  --include-data-dir=./backend/libsimple-windows-x64=lib/backend/libsimple-windows-x64 --include-data-files=./backend/libsimple-windows-x64/simple.dll=lib/backend/libsimple-windows-x64/simple.dll --include-data-dir=./models=models --disable-console
    ```

## Details

* OCR is done using [RapidOCR](https://github.com/RapidAI/RapidOCR)
* Object detection adapted from [ONNX-YOLOv8-Object-Detection](https://github.com/ibaiGorordo/ONNX-YOLOv8-Object-Detection)
* Search tokenizer from [Simple](https://github.com/wangfenjin/simple)
* Object detection and image classification model from [YOLOv8](https://github.com/ultralytics/ultralytics)
