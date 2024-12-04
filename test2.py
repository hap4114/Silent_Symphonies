import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
from tensorflow.keras.utils import get_custom_objects
from tensorflow.keras.layers import DepthwiseConv2D  # Import DepthwiseConv2D

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

# Define a custom DepthwiseConv2D if necessary
def custom_depthwise_conv2d(*args, **kwargs):
    if 'groups' in kwargs:
        del kwargs['groups']  # Ignore the 'groups' argument
    return DepthwiseConv2D(*args, **kwargs)

get_custom_objects().update({'DepthwiseConv2D': custom_depthwise_conv2d})

classifier = Classifier(r"C:\Users\himan\OneDrive\Desktop\Silent Symphonies Dynamic\keras_model_n.h5", 
                        r"C:\Users\himan\OneDrive\Desktop\Silent Symphonies Dynamic\labels_n.txt")

offset = 20
imgSize = 300
counter = 0

labels = ["0","1","2","3","4","5","6","7","8","9"]

while True:
    success, img = cap.read()
    imgOutput = img.copy()
    hands, img = detector.findHands(img)
    
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)*255

        imgCrop = img[y-offset:y + h + offset, x-offset:x + w + offset]
        imgCropShape = imgCrop.shape

        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize-wCal)/2)
            imgWhite[:, wGap: wCal + wGap] = imgResize
            prediction , index = classifier.getPrediction(imgWhite, draw= False)
            print(prediction, index)

        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hCal) / 2)
            imgWhite[hGap: hCal + hGap, :] = imgResize
            prediction , index = classifier.getPrediction(imgWhite, draw= False)

        cv2.rectangle(imgOutput,(x-offset,y-offset-70),(x -offset+400, y - offset+60-50),(0,255,0),cv2.FILLED)  
        cv2.putText(imgOutput,labels[index],(x,y-30),cv2.FONT_HERSHEY_COMPLEX,2,(0,0,0),2) 
        cv2.rectangle(imgOutput,(x-offset,y-offset),(x + w + offset, y+h + offset),(0,255,0),4)   

        cv2.imshow('ImageCrop', imgCrop)
        cv2.imshow('ImageWhite', imgWhite)

    cv2.imshow('Image', imgOutput)
    cv2.waitKey(1)