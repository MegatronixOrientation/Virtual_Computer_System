import cv2
from cvzone.HandTrackingModule import HandDetector
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width property is set at value 3
cap.set(4, 720)   # Height property is set at value 4

detector = HandDetector(detectionCon=1)  # By default, it is 0.5

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", "."]]

finalText = ""
backspaceClicked = False  # Flag to track if Backspace button was clicked

def draw(img, btnList):
    for button in btnList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Define btnList before the loop
btnList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        btnList.append(Button([100 * j + 50, 100 * i + 50], key))

# Add a Backspace button
btnList.append(Button([950, 250], "<", [150, 85]))

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img)
    img = draw(img, btnList)

    if lmList:
        for button in btnList:
            x, y = button.pos
            w, h = button.size

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                if button.text == "<":
                    l, _, _ = detector.findDistance(8, 12, img, draw=False)
                    if l >= 30 and backspaceClicked:
                        continue
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText = finalText[:-1]  # Remove the last character
                    backspaceClicked = False  # Set the Backspace flag
                    time.sleep(0.1555555)
                else:
                    l, _, _ = detector.findDistance(8, 12, img, draw=False)
                    if l < 30:
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        finalText += button.text
                        backspaceClicked = False  # Reset the Backspace flag
                        time.sleep(0.1555555)

    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    if cv2.waitKey(1) == ord("e"):
        break

    cv2.imshow("Image", img)
    cv2.waitKey(1)