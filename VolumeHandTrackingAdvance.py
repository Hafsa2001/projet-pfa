import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


################################
wCam, hCam = 640, 480   #1200, 720
################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
previousTime = 0

detector = htm.handDetector(detectionconf=0.7, maxHands=1)   #htm handtrackingmodule

devices = AudioUtilities.GetSpeakers()    #pour accéder au volume de l'ordi
interface = devices.Activate(
IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()   #volume range ca varie d'un ordi à un autre (print it)
#print(volRange)     #egal à (-63.5, 0.0, 0.5)
#volume.SetMasterVolumeLevel(-20.0, None)    #to conntrol the level of the volume in out sys
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)
while True:
    success, img = cap.read()

    #Find Hand
    img = detector.findHands(img)
    Lmlist, bbox = detector.findPosition(img, draw=True)  #false bc we don't want the circles and true if we want them, #bounding box, declared in htm
    if len(Lmlist) != 0:

        #filter based on size
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) // 100
        print(area)
        if 250 < area < 1000:    #it only detect volume when the hand is in this specific area

            #Find the distance bw the inedx and the thump
            length, img, lineinfo = detector.findDistance(4, 8, img)
            #print(length)

            #Convert volume
            # print(int(length), vol)
            volBar = np.interp(length, [50, 200], [400, 150])  # vol de la barre
            volPer = np.interp(length, [50, 200], [0, 100])  # le pourcentage du volume dans la barre

            #reduce resolution to make it smoother
            smoothness = 5           #we choose to increment by 5 percent
            volPer = smoothness * round(volPer / smoothness)

            #Check which finger is up
            fingers = detector.fingersUp()
            #print(fingers)

            #Check if pinky finger is down set the volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer/100, None)
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 10, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)

            #Drawings
            if length < 50:
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 10, (0, 255, 0), cv2.FILLED)

            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)
            currentVolume =int(volume.GetMasterVolumeLevelScalar()*100)
            cv2.putText(img, f'Vol Set: {int(currentVolume)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 2, colorVol,
                        3)

    # Frame rate
    currentTime = time.time()  # gives us the time
    if currentTime - previousTime != 0:
        fps = 1 / (currentTime - previousTime)
        previousTime = currentTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0),
                    3)

    cv2.imshow("img", img)
    cv2.waitKey(1)