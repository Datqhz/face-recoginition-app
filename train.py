import os
from matplotlib import pyplot as plt
import cv2

from ultralytics import YOLO
# Load a model
model = YOLO("runs/detect/train/weights/best.pt")  # build a new model from scratch

results = model.train(data="config.yaml", epochs=10)  # train the model

print(results)