import tkinter as tk
from tkinter import *

# mouse to be executed when Button 1 is clicked
def button1_click():
    import cv2
    import numpy as np
    import time
    import hand_module_mouse as ht
    import autopy   # Install using "pip install autopy"

    ### Variables Declaration
    pTime = 0               # Used to calculate frame rate
    width = 640             # Width of Camera
    height = 480            # Height of Camera
    frameR = 100            # Frame Rate
    smoothening = 8         # Smoothening Factor
    prev_x, prev_y = 0, 0   # Previous coordinates
    curr_x, curr_y = 0, 0   # Current coordinates

    cap = cv2.VideoCapture(0)   # Getting video feed from the webcam
    cap.set(3, width)           # Adjusting size
    cap.set(4, height)

    detector = ht.handDetector(maxHands=1)                  # Detecting one hand at max
    screen_width, screen_height = autopy.screen.size()      # Getting the screen size
    while True:
        success, img = cap.read()
        img = detector.findHands(img)                       # Finding the hand
        lmlist, bbox = detector.findPosition(img)           # Getting position of hand

        if len(lmlist)!=0:
            x1, y1 = lmlist[8][1:]
            x2, y2 = lmlist[12][1:]


            fingers = detector.fingersUp()      # Checking if fingers are upwards
            cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255), 2)   # Creating boundary box
            if fingers[1] == 1 and fingers[2] == 0:     # If fore finger is up and middle finger is down
                x3 = np.interp(x1, (frameR,width-frameR), (0,screen_width))
                y3 = np.interp(y1, (frameR, height-frameR), (0, screen_height))

                curr_x = prev_x + (x3 - prev_x)/smoothening
                curr_y = prev_y + (y3 - prev_y) / smoothening

                autopy.mouse.move(screen_width - curr_x, curr_y)    # Moving the cursor
                cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
                prev_x, prev_y = curr_x, curr_y

            if fingers[1] == 1 and fingers[2] == 1:     # If fore finger & middle finger both are up
                length, img, lineInfo = detector.findDistance(8, 12, img)

                if length < 60:     # If both fingers are really close to each other
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()    # Perform Click

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# keyboard to be executed when Button 2 is clicked
def button2_click():
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
    

        


# volume control to be executed when Button 3 is clicked
def button3_click():
    import cv2
    import time
    import numpy as np
    import hand_module as htm
    import math
    import pycaw
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    ####################################
    wCam, hcam = 640, 480
    #####################################

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hcam)
    pTime = 0
    cTime = 0
    detector = htm.handDetector(detectioncon=0.7)

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volRange = volume.GetVolumeRange()

    minVol = volRange[0]
    maxVol = volRange[1]
    vol = 0
    volBar = 400
    volPer = 0

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPos(img, draw=False)

        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = ((x1 + x2) // 2), ((y1 + y2) // 2)

            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (144,298,144), 3) #line color
            cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)

            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            #print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)

            # Interpolate color from green to red based on volPer
            color = (0, int(255 - (volPer * 2.55)), int(volPer * 2.55))

            # Draw the volume bar with the interpolated color
            cv2.rectangle(img, (50, 150), (85, 400), color, 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), color, cv2.FILLED)

        cv2.putText(img, f'{int(volPer)} % ', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow("IMG", img)
        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



def button4_click():
    import cv2
    from cvzone.HandTrackingModule import HandDetector

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detectionCon=1)
    startDist = None
    scale = 0
    cx, cy = 500, 500
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        img1 = cv2.imread("download.jpg")

        if len(hands) == 2:
            # print(detector.fingersUp(hands[0]), detector.fingersUp(hands[1]))
            if detector.fingersUp(hands[0]) == [1, 1, 0, 0, 0] and \
                    detector.fingersUp(hands[1]) == [1, 1, 0, 0, 0]:
                # print("Zoom Gesture")
                lmList1 = hands[0]["lmList"]
                lmList2 = hands[1]["lmList"]
                # point 8 is the tip of the index finger
                if startDist is None:
                    # length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)
                    length, info, img = detector.findDistance(hands[0]["center"], hands[1]["center"], img)

                    startDist = length

                # length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)
                length, info, img = detector.findDistance(hands[0]["center"], hands[1]["center"], img)

                scale = int((length - startDist) // 2)
                cx, cy = info[4:]
                print(scale)
        else:
            startDist = None

        try:
            h1, w1, _ = img1.shape
            newH, newW = ((h1 + scale) // 2) * 2, ((w1 + scale) // 2) * 2
            img1 = cv2.resize(img1, (newW, newH))

            img[cy - newH // 2:cy + newH // 2, cx - newW // 2:cx + newW // 2] = img1
        except:
            pass

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()







# Create the main window
root = tk.Tk()
root.title("Virtual Computer System")
root.geometry("1920x1080")  # Set window dimensions



# Customize the main window background color
root.configure(bg="#23272f")

# Create a custom font
custom_font = ("cambria", 16, "bold")


image = tk.PhotoImage(file="megalogowithstroke.png")
image_label = tk.Label(root, image=image, bg="#23272f")
image_label.pack()

button1_style = tk.Button(root, text="Virtual mouse ", command=button1_click, relief="flat", font=custom_font, bg="#087ea4", fg="white")
button1_style.pack(pady=20)  # Add vertical padding to center the button

# Create Button 2 with different colors and font and center it
button2_style = tk.Button(root, text="Virtual Keyboard", command=button2_click, relief="flat", font=custom_font, bg="#087ea4", fg="white")
button2_style.pack(pady=20)

# Create Button 3 with another set of colors and font and center it
button3_style = tk.Button(root, text="Virtual volume control", command=button3_click, relief="flat", font=custom_font, bg="#087ea4", fg="white")
button3_style.pack(pady=20)

button4_style = tk.Button(root, text="Virtual Zoom ", command=button4_click, relief="flat", font=custom_font,
                          bg="#087ea4", fg="white")
button4_style.pack(pady=20)



# Start the GUI main loop
root.mainloop()
