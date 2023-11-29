import os
from matplotlib import pyplot as plt
import cv2

from ultralytics import YOLO
# Load a model
model = YOLO("yolov8m.pt")  # build a new model from scratch

results = model.train(data="data.yaml", epochs=1)  # train the model

print(results)