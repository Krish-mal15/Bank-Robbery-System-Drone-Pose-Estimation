import cv2
import mediapipe as mp
import math
import djitellopy as tello
import KeyPressModule as kp
from time import sleep
import yagmail

# Initialize email send API. Using temporary password from google for security reasons
yag = yagmail.SMTP('krishnamalhotra150@gmail.com', 'wmns iikh mzii hxkm')

# Tello Drone Connection and Keyboard control

# me = tello.Tello()
# me.connect()
# me.streamon()
# kp.init()
# speed = 40
# lr, fb, ud, yv = 0, 0, 0, 0

# def getKeyboardInput():
#     lr, fb, ud, yv = 0, 0, 0, 0
#     speed = 50
#     if kp.getKey("LEFT"):
#         lr = -speed
#     elif kp.getKey("RIGHT"):
#         lr = speed
#     if kp.getKey("UP"):
#         fb = speed
#     elif kp.getKey("DOWN"):
#         fb = -speed
#     if kp.getKey("w"):
#         ud = speed
#     elif kp.getKey("s"):
#         ud = -speed
#     if kp.getKey("a"):
#         yv = -speed
#     elif kp.getKey("d"):
#         yv = speed
#     if kp.getKey("q"):
#         me.land()
#         sleep(3)
#     if kp.getKey("e"):
#         me.takeoff()
#     return [lr, fb, ud, yv]

notified = False  # Flag to track notification status

# Pose estimator

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

# For Camera testing
cap = cv2.VideoCapture(0)

hands = [15, 16, 21, 19, 17, 20, 18, 22]
landmark_coordinates = {}  # Dictionary to store the coordinates of specific landmarks


# Using Yagmail API to notify user
def notify_user():
    # message_battery = str(me.get_battery())
    message_battery_test = str(80)

    global notified
    if not notified:
        print("USER HAD BEEN NOTIFIED OF THIS THREAT")
        yag.send('krishnamalhotra150@gmail.com', 'Krishna Security System', ('DRONE HAS DETECTED THREAT. Drone is '
                                                                             'chasing threat. Battery: ', message_battery_test))
        notified = True


def attack_person(person_x, person_y, bp_12, bp_11, bp_23, bp_24):
    # Calculating approximate area, assuming body is a square
    person_area = math.dist(bp_12, bp_11) * math.dist(bp_23, bp_24)
    if person_area >= 12000:
        print("Drone Movement:   STATIONARY")
    elif person_area <= 8000:
        print("Drone Movement:   FORWARD")
    else:
        print("Drone Movement:   STATIONARY")


# Code execution loop
while True:

    # Get camera footage from drone (cap.read() for testing)
    success, img = cap.read()
    # img = me.get_frame_read().frame

    window_width = img.shape[0]
    window_height = img.shape[1]

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    # vals = getKeyboardInput()
    # me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    # Retrieve coordinates of four main body points
    if results.pose_landmarks:
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            if id in [11, 12, 23, 24] and lm.visibility > 0.5:
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_coordinates[id] = (cx, cy)

            # If body reaches past 500 pixels
            attack_threshold_x = 500
            for i in hands:
                if id == i and lm.visibility > 0.5:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                    if cx > attack_threshold_x:
                        notify_user()

    # Calculate body midpoint and move drone accordingly
    if all(key in landmark_coordinates for key in [11, 12, 23, 24]):
        bp_12 = landmark_coordinates[12]
        bp_11 = landmark_coordinates[11]
        bp_23 = landmark_coordinates[23]
        bp_24 = landmark_coordinates[24]

        attack_person(cx, cy, bp_12, bp_11, bp_23, bp_24)

        distance = abs(int(bp_12[0]) - int(bp_11[0]))
        mid_dist = (distance / 2) + abs(0 - bp_12[0])

        constant_diff = 75
        constant_shift = 100

        drone_left = (window_width / 2 + constant_diff) + constant_shift
        drone_right = (window_width / 2 - constant_diff) + constant_shift

        if mid_dist > drone_left:
            print("Drone Movement:   LEFT")
            # me.send_rc_control(-speed, 0, 0, 0)
        elif mid_dist < drone_right:
            print("Drone Movement:   RIGHT")
            # me.send_rc_control(speed, 0, 0, 0)
        else:
            # me.send_rc_control(0, 0, 0, 0)
            pass

        # Display body center coordinate
        cv2.circle(img, (int(mid_dist), 280), 5, (0, 255, 0), cv2.FILLED)
    else:
        print("DRONE MOVEMENT:   STATIONARY")
        # me.send_rc_control(0, 0, 0, 0)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
