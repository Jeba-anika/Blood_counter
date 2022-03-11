# Need to use certain dye for pink color blood smear image, we won't work with violet color image
import os
from flask import Flask, request, jsonify
import numpy as np
import cv2

import random

# instantiate flask app
app = Flask("blood_counter")


@app.route("/count", methods=['POST', 'GET'])
def get_output():
    # get file from POST request and save it
    image_file = request.files['file']
    filename = str(random.randint(0, 100000))
    image_file.save(filename)

    # ====================================================WBC Detection=====================================

    image = cv2.imread(filename)
    image = cv2.resize(image, (374, 340))

    start_point = (57, 57)
    end_point = (57 + 257, 57 + 222)
    color = (0, 128, 0)
    thickness = 1

    roi = cv2.rectangle(image, start_point, end_point, color, thickness)

    crop = image[58:(57 + 222), 58:(57 + 257)]
    crop = cv2.resize(crop, (374, 340))
    crop_1 = crop.copy()

    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
    lab = cv2.resize(lab, (374, 340))

    l, a, b = cv2.split(lab)
    l = cv2.resize(l, (374, 340))
    a = cv2.resize(a, (374, 340))
    b = cv2.resize(b, (374, 340))
    lab_hstack = np.hstack((l, a, b))

    ret, th = cv2.threshold(b, 106, 255, cv2.THRESH_BINARY)

    k = np.ones((6, 6), np.uint8)
    # k = np.ones((2,2),np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, k)

    k = np.array(
        [[0, 1, 1, 1, 0],
         [1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [0, 1, 1, 1, 0]], np.uint8)
    # k = np.ones((8,8),np.uint8)
    erode = cv2.erode(opening, k)
    erode = cv2.resize(erode, (374, 340))

    edge = cv2.Canny(erode, 100, 200)

    circles = cv2.HoughCircles(edge, cv2.HOUGH_GRADIENT, 1, 10,
                               param1=200, param2=12, minRadius=9, maxRadius=20)

    if circles is not None:
        detected_circles = np.uint16(np.around(circles))

    for (x, y, r) in detected_circles[0, :]:
        cv2.circle(crop_1, (x, y), r, (128, 84, 231), 2)
        cv2.circle(crop_1, (x, y), 1, (0, 255, 255), 2)

    wbc_num = detected_circles.shape[1]

    # ====================================================RBC Detection=====================================

    image_big = cv2.resize(crop, (600, 600))

    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    ret, th = cv2.threshold(b, 106, 255, cv2.THRESH_BINARY)

    k = np.ones((6, 6), np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, k)

    k = np.array(
        [[0, 1, 1, 1, 0],
         [1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1],
         [0, 1, 1, 1, 0]], np.uint8)
    erode = cv2.erode(opening, k)

    k = np.ones((8, 8), np.uint8)
    erode_two = cv2.erode(opening, k)

    erode_two = cv2.resize(erode_two, (374, 340))

    erode_inv = cv2.bitwise_not(erode_two)

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    s = cv2.resize(s, (374, 340))

    wbc = cv2.addWeighted(s, 1, erode_inv, 1, 0)
    wbc = cv2.resize(wbc, (374, 340))
    bgr = cv2.cvtColor(wbc, cv2.COLOR_GRAY2BGR)
    ret, thresh_1 = cv2.threshold(bgr, 241, 255, cv2.THRESH_BINARY)
    wbc_removal = cv2.addWeighted(crop, 1, thresh_1, 1., 0)
    l_rbc, a_rbc, b_rbc = cv2.split(wbc_removal)
    lab_hstack_rbc = np.hstack((l_rbc, a_rbc, b_rbc))

    th = 0
    max_val = 255
    ret, otsu_rbc = cv2.threshold(a_rbc, th, max_val, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu_rbc = cv2.resize(otsu_rbc, (600, 600))

    rbc_circles = cv2.HoughCircles(otsu_rbc, cv2.HOUGH_GRADIENT, 1, 13.7,
                                   param1=200, param2=6, minRadius=12, maxRadius=15)

    if rbc_circles is not None:
        detected_circles = np.uint16(np.around(rbc_circles))

        for (x, y, r) in detected_circles[0, :]:
            cv2.circle(image_big, (x, y), r, (128, 84, 231), 2)
            cv2.circle(image_big, (x, y), 1, (0, 255, 255), 2)

    image_big = cv2.resize(image_big, (374, 340))
    rbc_num = detected_circles.shape[1]
    # print("Number of detected RBCs: ",rbc_num)

    # -----------------------------------------Platelet Detection -------------------------------------------

    crop = cv2.resize(crop, (374, 340))
    crop_2 = crop.copy()

    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    ret, th = cv2.threshold(b, 120, 255, cv2.THRESH_BINARY)

    k = np.ones((4, 4), np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, k)

    k = np.ones((2, 2), np.uint8)
    erode = cv2.erode(opening, k)

    edge = cv2.Canny(erode, 100, 200)

    contours, hierarchy = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(crop, contours, -1, (0, 255, 0), 2)

    l = len(contours)

    plat = []
    for i in range(0, l):
        area = cv2.contourArea(contours[i])
        perimeter = cv2.arcLength(contours[i], True)
        if area < 150 and perimeter < 70:
            plat.append(contours[i])

    cv2.drawContours(crop_2, plat, -1, (0, 255, 0), 2)

    plat_num = len(plat)
    # print("Number of detected platelets: ",plat_num)

    # we don't need the image file anymore - let's delete it!
    os.remove(filename)

    result = {"Number of detected platelets": plat_num,
              "Number of detected wbcs": wbc_num,
              "Number of detected rbcs": rbc_num,
              }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False)
