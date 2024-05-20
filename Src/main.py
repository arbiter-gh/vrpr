import json

import numpy as np
from ultralytics import YOLO
import cv2 as cv
import easyocr
from config import api_keys
from Utils.sort import *
from datetime import datetime



from validate import validate

cap = cv.VideoCapture("../Videos/shona2.mp4")

if not cap.isOpened():
    print("No source found!!")
    exit()

api_key = api_keys[0]
reader = easyocr.Reader(['en'])
model = YOLO("../Train/runs/detect/train/weights/best.pt")
output_file = "output.txt"
tracker = Sort()
currentId = 0

currentTime = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
fileName = f"output/vrpr_{currentTime}.txt"

while True:
    success, img = cap.read()
    if success:
        results = model(source=img, show=False, stream=True)
        detections = np.empty((0, 4))
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                currentArray = np.array([x1, y1, x2, y2])
                detections = np.vstack((detections, currentArray))

        resultTracker = tracker.update(detections)

        for result in resultTracker:
            x1, y1, x2, y2, id = result
            x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2), int(id)

            roi = img[y1:y2, x1:x2]

            cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.putText(img, f"{id}", (x1, y1 - 10), 0, 1, (0, 0, 255), 1)

            gray_roi = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
            text = reader.readtext(gray_roi)

            try:
                plate_number = text[0][1]
                if validate(plate_number) and id > currentId:
                    with open(fileName, 'w') as file:
                        file.write(f"{id}, {plate_number}\n")
                        currentId = id

            except IndexError:
                print("Plate number not found.")
   
            # cv.imshow("roi", roi)
            # cv.imshow("main", img)

    else:
        print("End")
        break

cv.destroyAllWindows()
cap.release()
