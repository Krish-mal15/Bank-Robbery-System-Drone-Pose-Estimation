import cv2
import djitellopy as tello

me = tello.Tello()

me.connect()

print("Battery: ", me.get_battery())

me.streamon()

while True:
    cap = me.get_frame_read().frame

    print("Window Size: ", cap.shape)

    cv2.imshow("Image", cap)

    cv2.waitKey(1)
