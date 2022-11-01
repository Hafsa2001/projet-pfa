import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


################################
wCam, hCam = 1200, 720   #640, 480
################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
previousTime = 0

detector = htm.handDetector(detectionconf=0.7)   #htm handtrackingmodule

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


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    Lmlist = detector.findPosition(img, draw=False)  #false bc we don't want the circles and true if we want them
    if len(Lmlist) != 0:
        #print(Lmlist[4], Lmlist[8])

        x1, y1 = Lmlist[4][1], Lmlist[4][2]
        x2, y2 = Lmlist[8][1], Lmlist[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # to draw the circle in the middle of 4 and 8

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)  # 5 c'est le rayon du cercle
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # start point, ens point, color, thikness(épaisseur)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)  # distance entre 4 et 8 i need to print it
        #print(length)

        #Hand range   50 - 300
        #Volume range -63.5 - 0

        vol = np.interp(length, [50, 300], [minVol, maxVol])  #convert length to volume
        print(int(length), vol)
        volBar = np.interp(length, [50, 300], [400, 150])  #vol de la barre
        volPer = np.interp(length, [50, 300], [0, 100])    #le pourcentage du volume dans la barre
        #volPer = np.interp(length, [50, 300], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)
        #volume.SetMasterVolumeLevel(0, None)     cad le max de volume devient 0= 100, l'ordi devient 100


        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)


    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    currentTime = time.time()  # gives us the time
    if currentTime - previousTime != 0:
        fps = 1 / (currentTime - previousTime)
        previousTime = currentTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0),
                    3)

    cv2.imshow("img", img)
    cv2.waitKey(1)
