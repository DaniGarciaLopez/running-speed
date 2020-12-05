#must have OpenCv, numpy and matplot lib installed for python
import cv2
import import_json as ij
import numpy as np
import math
from matplotlib import pyplot as plt

#key data
athlete_height = 180 # in cm
camera_fps = 60

#importing json file data
kp = ij.get_keypoints()     #kp is a list of all the 25x3 lists of keypoints
#kp = ij.interpolate_uncertain_points(kp)       #uncomment to interpolate uncertain points
f_kp = []       #f_kp will be a 25x3 list of the keypoints at a specific frame

#init
speed = 0
max_distance = 0
stride_frames = 0
prev_ankle_distance = 0

#constants
bottom_left_of_screen = (20, 700)
eyes=17
neck=1
hip=8
left_knee=13
right_knee=10
left_ankle=14
right_ankle=11

#get angle between three points
def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang

#function that determines how many pixels correlate to 1 meter, using the height of the athlete
def get_pixels_per_meter(f_kp):   #returns how many pixels correlate to 1 meter in the frame
    coord_eyes = (f_kp[eyes][0], f_kp[eyes][1])
    coord_neck = (f_kp[neck][0], f_kp[neck][1])
    coord_hip = (f_kp[hip][0], f_kp[hip][1])
    coord_knee = (f_kp[left_knee][0], f_kp[left_knee][1])
    coord_ankle = (f_kp[left_ankle][0], f_kp[left_ankle][1])
    distance = 0        #we add the distances between eyes, neck, hip, knee and ankle
    distance += math.dist(coord_eyes,coord_neck)
    distance += math.dist(coord_neck, coord_hip)
    distance += math.dist(coord_hip, coord_knee)
    distance += math.dist(coord_knee, coord_ankle)

    pixels = int(distance/athlete_height*100)
    return pixels

#function to draw a meter measurement line on the floor using the athlete's height at a specific frame
def draw_meter_lines(frame, f_kp):
    values = []
    ppm = get_pixels_per_meter(f_kp)
    for keypoint in f_kp:      #we get just the y values
        values.append(keypoint[1])
    max_value = int(max(values))    #we draw the line at the lowest keypoint (approx the floor)
    frame = cv2.line(frame, (0, max_value), (1280, max_value), (255, 255, 255), 2)
    for meter in range(int(1280/ppm)+1):
        frame = cv2.line(frame, (0+(ppm*meter), max_value), (0+(ppm*meter), max_value+10), (255, 255, 255), 3)
        frame = cv2.putText(frame, str(meter), (-10+(ppm*meter), 44 + max_value),cv2.FONT_HERSHEY_SIMPLEX,       # font
                    1,      #font scale
                    (255, 255, 255),   #   font color
                    2)
    return frame

#function to draw circles at the keypoints of a specific frame
def draw_keypoints(frame, f_kp):
    kpid = 0
    for point in f_kp:  # drawing a circle for each kp
        center = (int(point[0]), int(point[1]))
        center_high = ((int(point[0])-5, int(point[1])-15))      #used for writing its id
        frame = cv2.circle(frame, center, 10, (0, int(255 * point[2]), 255 * (1 - point[2])), 3)       #draws green cirle if certain, red if not
        cv2.putText(frame,
                    str(kpid),
                    center_high,
                    cv2.FONT_HERSHEY_SIMPLEX,  # font
                    0.5,  # font scale
                    (255, 255, 255),  # font color
                    1)  # line type
        kpid += 1
    return frame

#function to draw the athlete speed at the bottom left of the screen of a frame
def draw_athlete_speed(frame, speed):
    cv2.putText(frame,
                str(round(speed, 2)) + ' Km/h',
                bottom_left_of_screen,
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (255, 255, 255),
                2)
    return frame


#main
while(1):
    cap = cv2.VideoCapture('makau.mp4')
    frame_count = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break

        f_kp = kp[frame_count]

        frame = draw_keypoints(frame, f_kp)

        # aqui iria el algoritmo de deteccion de velocidad, esto que he comentado ha sido un intento de hacerlo con la distancia entre tobillos

        # hip_coord = (kp[hip][0], kp[hip][1])
        # left_ankle_coord = (kp[left_ankle][0], kp[left_ankle][1])
        # right_ankle_coord = (kp[right_ankle][0], kp[right_ankle][1])
        # ankle_distance = math.fabs(left_ankle_coord[0]-right_ankle_coord[0])
        # if ankle_distance > prev_ankle_distance-5:
        #     stride_frames +=1
        #     prev_ankle_distance = ankle_distance
        # else:
        #     stride_pixels = ankle_distance
        #     stride_meters = stride_pixels/get_pixels_per_meter(kp)
        #     stride_time = stride_frames*(1/camera_fps)
        #     try:
        #         speed = (stride_meters/stride_time)*3.6
        #     except ZeroDivisionError:
        #         print ("Division by zero")
        #     stride_frames=0
        #     prev_ankle_distance = ankle_distance
        #     print("The stride travelled " + str(stride_meters) + " meters")
        #     print("The stride took " + str(stride_time) + " seconds")
        #     print("The speed is " + str(speed) + " kilometers per hour")

        frame = draw_athlete_speed(frame, speed)

        cv2.imshow('frame', frame)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()

cap.release()
cv2.destroyAllWindows()

