import cv2
import mediapipe as mp
import time
import math


class handDetector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionconf=0.5, trackingconf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionconf = detectionconf
        self.trackingconf = trackingconf

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionconf, self.trackingconf )  # Hand is a function already declared
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    #convert BGR to RGB bc the class hand only use RGB
        self.results = self.hands.process(imgRGB)      #function exist in the model of hand
        #print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
             for handLms in self.results.multi_hand_landmarks:    #the import thing, c'est la boucle qui désigne les 21 landmarks for each hand
                 if draw:
                     self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)  # method provided by mediapipe

        return img


    def findPosition(self, img, handNo=0, draw = True):    #handNo to precise the number of the hand
        xList = []
        yList = []
        bbox = []
        self.Lmlist = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                #print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                xList.append(cx)
                yList.append(cy)
                #print(id, cx, cy)
                self.Lmlist.append([id, cx, cy])
                #if id == 4:
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255,0,255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0]-20,bbox[1]-20), (bbox[2]+20,bbox[3]+20), (0, 255, 0), 2)

        return self.Lmlist, bbox


    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.Lmlist[p1][1], self.Lmlist[p1][2]
        x2, y2 = self.Lmlist[p2][1], self.Lmlist[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

    def fingersUp(self):
        self.tipIds = [4, 8, 12, 16, 20]
        fingers = []   #if it's 0 it's down if it' 1 it's up
        # Thumb
        if self.Lmlist[self.tipIds[0]][1] > self.Lmlist[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4Fingers
        for id in range(1, 5):
            if self.Lmlist[self.tipIds[id]][2] < self.Lmlist[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers









def main():
    previousTime = 0
    currentTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)     #on peut ajouter draw=False ds les arg si on veut pas dessiner
        Lmlist = detector.findPosition(img)
        if len(Lmlist)!=0:
            print(Lmlist[4])

        currentTime = time.time()  # gives us the time
        fps = 1 / (currentTime - previousTime)
        previousTime = currentTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255),
                    3)  # (10, 70) la position, 3 est l'épaisseur

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()

