#!/usr/bin/env python

import cv2
import gpiozero
from time import sleep
from signal import pause

# GPIO pin number for the relay
thisrelay = 15

# Set up the relay
relay = gpiozero.OutputDevice(thisrelay, active_high=False, initial_value=False)

# Load class names
classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

# Paths for the configuration and weights files
configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

# Load the detection model
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(100, 100)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def getObjects(img, thres, nms, draw=True, objects=[]):
    # Detect objects in the image
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)

    if len(objects) == 0:
        objects = classNames

    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box, className])
                if draw:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, classNames[classId - 1].upper(), 
                                (box[0] + 10, box[1] + 30), 
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), 
                                (box[0] + 200, box[1] + 30), 
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                # Trigger the relay
                relay.on()
                sleep(0.2)
                relay.off()

    return img, objectInfo

if __name__ == "__main__":
    # Capture video from the webcam
    cap = cv2.VideoCapture(0)
    # cap.set(3, 640)
    # cap.set(4, 480)
    # cap.set(10, 70)

    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img, 0.45, 0.2, objects=['bird'])
        # print(objectInfo)
        cv2.imshow("Output", img)
        cv2.waitKey(1)
