# -*- coding: utf-8 -*-

import time

import cv2
import numpy as np
import onnxruntime


def nms(boxes, scores, iou_threshold):
    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]

    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)

        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])

        # Remove boxes with IoU over the threshold
        keep_indices = np.where(ious < iou_threshold)[0]

        # print(keep_indices.shape, sorted_indices.shape)
        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def multiclass_nms(boxes, scores, class_ids, iou_threshold):

    unique_class_ids = np.unique(class_ids)

    keep_boxes = []
    for class_id in unique_class_ids:
        class_indices = np.where(class_ids == class_id)[0]
        class_boxes = boxes[class_indices, :]
        class_scores = scores[class_indices]

        class_keep_boxes = nms(class_boxes, class_scores, iou_threshold)
        keep_boxes.extend(class_indices[class_keep_boxes])

    return keep_boxes


def compute_iou(box, boxes):
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = np.maximum(box[0], boxes[:, 0])
    ymin = np.maximum(box[1], boxes[:, 1])
    xmax = np.minimum(box[2], boxes[:, 2])
    ymax = np.minimum(box[3], boxes[:, 3])

    # Compute intersection area
    intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)

    # Compute union area
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def xywh2xyxy(x):
    # Convert bounding box (x, y, w, h) to bounding box (x1, y1, x2, y2)
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y


class YOLO11Base:

    def initialize_model(self, path):
        self.session = onnxruntime.InferenceSession(
            path, providers=onnxruntime.get_available_providers()
        )
        # Get model info
        self.get_input_details()
        self.get_output_details()

    def get_input_details(self):
        model_inputs = self.session.get_inputs()
        self.input_names = [model_inputs[i].name for i in range(len(model_inputs))]

        self.input_shape = model_inputs[0].shape
        self.input_height = self.input_shape[2]
        self.input_width = self.input_shape[3]

    def get_output_details(self):
        model_outputs = self.session.get_outputs()
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]

    def prepare_input(self, image: np.ndarray):
        self.img_height, self.img_width = image.shape[:2]

        # Resize input image
        input_img = cv2.resize(image, (self.input_width, self.input_height))
        # input_img = image

        # Convert the image to RGB if it is in grayscale
        if len(input_img.shape) == 2:
            input_img = cv2.cvtColor(input_img, cv2.COLOR_GRAY2RGB)
        else:
            input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
        # Scale input pixel values to 0 to 1
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)

        return input_tensor

    def inference(self, input_tensor):
        outputs = self.session.run(
            self.output_names, {self.input_names[0]: input_tensor}
        )
        return outputs


class YOLO11(YOLO11Base):
    """
    YOLO11 is a class that represents the YOLO11 object detection model.
    Pre-trained on the COCO or the Open Images V7 dataset.

    Args:
        path (str): The path to the ONNX model file.
        conf_thres (float, optional): The confidence threshold for object detection. Defaults to 0.7.
        iou_thres (float, optional): The IOU threshold for non-maxima suppression. Defaults to 0.5.
    Returns:
        boxes (numpy.ndarray): The bounding boxes of the detected objects.
        scores (numpy.ndarray): The confidence scores of the detected objects.
        class_ids (numpy.ndarray): The predicted class IDs of the detected objects.
    """

    def __init__(self, path, conf_thres=0.7, iou_thres=0.5):
        self.conf_threshold = conf_thres
        self.iou_threshold = iou_thres

        # Initialize model
        self.initialize_model(path)

    def __call__(self, image):
        return self.detect_objects(image)

    def detect_objects(self, image: np.ndarray):
        """
        Detects objects in the given image using the YOLO11 model.

        Args:
            image: The input image.

        Returns:
            boxes (numpy.ndarray): The bounding boxes of the detected objects.
            scores (numpy.ndarray): The confidence scores of the detected objects.
            class_ids (numpy.ndarray): The predicted class IDs of the detected objects.
        """
        input_tensor = self.prepare_input(image)

        # Perform inference on the image
        outputs = self.inference(input_tensor)

        self.boxes, self.scores, self.class_ids = self.process_output(outputs)

        return self.boxes, self.scores, self.class_ids

    def process_output(self, output):
        predictions = np.squeeze(output[0]).T

        # Filter out object confidence scores below threshold
        scores = np.max(predictions[:, 4:], axis=1)
        predictions = predictions[scores > self.conf_threshold, :]
        scores = scores[scores > self.conf_threshold]

        if len(scores) == 0:
            return [], [], []

        # Get the class with the highest confidence
        class_ids = np.argmax(predictions[:, 4:], axis=1)

        # Get bounding boxes for each object
        boxes = self.extract_boxes(predictions)

        # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
        # indices = nms(boxes, scores, self.iou_threshold)
        indices = multiclass_nms(boxes, scores, class_ids, self.iou_threshold)

        return boxes[indices], scores[indices], class_ids[indices]

    def extract_boxes(self, predictions):
        # Extract boxes from predictions
        boxes = predictions[:, :4]

        # Scale boxes to original image dimensions
        boxes = self.rescale_boxes(boxes)

        # Convert boxes to xyxy format
        boxes = xywh2xyxy(boxes)

        return boxes

    def rescale_boxes(self, boxes):

        # Rescale boxes to original image dimensions
        input_shape = np.array(
            [self.input_width, self.input_height, self.input_width, self.input_height]
        )
        boxes = np.divide(boxes, input_shape, dtype=np.float32)
        boxes *= np.array(
            [self.img_width, self.img_height, self.img_width, self.img_height]
        )
        return boxes


class YOLO11Cls(YOLO11Base):
    """
    YOLO11Cls is a class that represents the YOLO11-cls classification model.
    Pre-trained on the ImageNet dataset.

    Args:
        path (str): The path to the ONNX model file.
        conf_thres (float, optional): The confidence threshold for classification. Defaults to 0.7.
    Returns:
        class_ids (numpy.ndarray): The predicted class IDs of the detected objects.
        confidence (numpy.ndarray): The confidence scores of the detected objects.
    """

    def __init__(self, path, conf_thres=0.7):
        self.conf_threshold = conf_thres

        # Initialize model
        self.initialize_model(path)

    def __call__(self, image):
        return self.predict(image)

    def predict(self, image: np.ndarray):
        """
        Detects objects in the given image using the YOLO11 model.

        Args:
            image (PIL.np.ndarray): The input image.

        Returns:
        class_ids: numpy.ndarray: The predicted class IDs of the detected objects.
        confidence: numpy.ndarray: The confidence scores of the detected objects.
        """
        input_tensor = self.prepare_input(image)

        # Perform inference on the image
        outputs = self.inference(input_tensor)

        class_ids, confidence = self.process_output(outputs)

        return class_ids, confidence

    def process_output(self, output):
        """
        Processes the output tensor to get the predicted class IDs of the detected objects.

        Args:
            output (numpy.ndarray): The output tensor.

        Returns:
            numpy.ndarray: The predicted class IDs of the detected objects.

        """
        predictions = np.squeeze(output[0]).T

        # Get the classes with the confidence>threshold
        class_ids = np.where(predictions > self.conf_threshold)
        class_ids = class_ids[0]

        return class_ids, predictions[class_ids]
