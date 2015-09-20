#!/usr/bin/env python

'''
Detects rectangles on page
parses them as a tree
returns a json as specified
'''
from matplotlib import pyplot as plt
import math
import numpy as np
import cv2
import json
import random
import string
import pytesseract
from PIL import Image

IMG = None
PROC_IMG = None
INPUT = 'data/goodbye.png'
OUTPUT = 'json/app.json'
ID_LENGTH = 5   # for ids used in the json
SCREEN_W = 360
SCREEN_H = 640

class Rectangle(object):
    # p2 is bottom right (max)
    # p1 is top left (maxs)
    def __init__(self, x1, y1, x2, y2):
        self.p1 = (x1, y1)
        self.p2 = (x2, y2)
        self.children = []
        self.parent = None

    def __str__(self):
        return "Rectangle defined by %s, %s, %i children" % (self.p1, self.p2, len(self.children))

    def is_child_of(self, other):
        return (self.p1[0] > other.p1[0] and
            self.p2[0] < other.p2[0] and
            self.p1[1] > other.p1[1] and
            self.p2[1] < other.p2[1])

    def add_child(self, other):
        self.children.append(other)

    def width(self):
        return (int)(self.p2[0] - self.p1[0])

    def height(self):
        return (int)(self.p2[1] - self.p1[1])

    def area(self):
        return self.width()*self.height()

    def get_scales(self):
        if self.parent:
            return self.parent.get_scales()
        else:
            return SCREEN_W / (float)(self.width()), SCREEN_H / (float)(self.height())

    def to_dict(self):
        node_type = 'container'
        node_id = ''.join(random.choice(string.ascii_uppercase) for _ in range(ID_LENGTH))

        if not self.children:
            crop_img = PROC_IMG[self.p1[1]: self.p2[1], self.p1[0]:self.p2[0]]
            
            t, r, p, c = find_shapes(crop_img)
            if c:
                node_type = 'image_view'
            elif t:
                node_type = 'text_view'
            elif p:
                node_type = 'button_view'
                node_str = get_text_in_image(crop_img)
                if node_str:
                    clean_str = [c for c in node_str if c.isalpha()]
                    node_id = clean_str + "-button"
            else:
                # default
                node_type = 'unknown'

        scale_w, scale_h = self.get_scales()

        marginTop = 0
        marginLeft = 0
        if self.parent:
            marginTop = (int)((self.p1[1] - self.parent.p1[1]) * scale_h)
            marginLeft = (int)((self.p1[0] - self.parent.p1[0]) * scale_w)

        style = {
            'width': (int)(self.width() * scale_w),
            'height': (int)(self.height() * scale_h),
            'marginTop': marginTop,
            'marginLeft': marginLeft,
        }

        return {
            'type': node_type,
            'style': style,
            'id': node_id,
            'children': [child.to_dict() for child in self.children],
        }


def make_rectangles(rects):
    sorted_rects = sort_points(rects)
    rectangles = []
    for rect in sorted_rects:
        rectangles.append(Rectangle(rect[0][0], rect[0][1], rect[-1][0], rect[-1][1]))

    return rectangles

def insertRect(newRect, rectList):
    hasBeenInserted = False
    for r in rectList:
        if newRect.is_child_of(r):
            newRect.parent = r
            if not r.children:
                hasBeenInserted = True
                r.add_child(newRect)
                return hasBeenInserted
            else:
                hasBeenInserted = insertRect(newRect, r.children)
    if not hasBeenInserted:
        rectList.append(newRect)
        hasBeenInserted = True
    return hasBeenInserted

def buildTreeFromList(rectList):
    tree = []
    for r in sorted(rectList, key=lambda x: x.p2[1], reverse=True):
        insertRect(r,tree)
    return tree

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_shapes(img):
    rects = []
    polygons = []
    circles = []
    triangles = []

    ret,thresh = cv2.threshold(img,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)

        # print len(cnt)
        # print cv2.contourArea(cnt)
        # print cv2.isContourConvex(cnt)
        # print "-------"

        if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
            #squares
            cnt = cnt.reshape(-1, 2)
            max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
            if max_cos >= 0.2:
                continue

            rects.append(cnt)
        elif len(cnt) == 3 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
            #triangles
            triangles.append(cnt)
        elif len(cnt) > 4 and len(cnt) <= 6 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
            # polygon
            polygons.append(cnt)
        elif len(cnt) > 6 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
            # circles
            circles.append(cnt)

    # print "++++++++"

    return triangles, rects, polygons, circles

def dist(a, b):
    return math.sqrt(math.pow(a[0] - b[0],2) + math.pow(a[1] - b[1],2))

def sort_points(rects):
    sorted_rects = []

    for rect in rects:
        sorted_rect = sorted(rect, key=lambda x: x[0])
        sorted_rects.append(np.array(
            sorted(sorted_rect[:2], key=lambda x: x[1]) + sorted(sorted_rect[2:], key=lambda x: x[1])
        ))

    return sorted_rects

def deduplicate_rects(rects):
    sorted_rects = sort_points(rects)

    rects_to_remove = []
    for i in range(len(sorted_rects)):
        rect_1 = sorted_rects[i]
        for j in range(i):
            rect_2 = sorted_rects[j]
            
            dists = []
            for k in range(4):
                dists.append(dist(rect_1[k],rect_2[k]))

            if max(dists) < 30:
                rects_to_remove.append(j)
        
    return [rect for i, rect in enumerate(rects) if i not in rects_to_remove]

def save_to_json(tree):
    tree.sort(key=lambda x: x.area())
    json_list = [node.to_dict() for node in tree[-1].children]

    title_img = PROC_IMG[
        0:tree[-1].p1[1],
        tree[-1].p1[0]:tree[-1].p2[0]
    ]

    root_id = get_text_in_image(title_img)

    with open(OUTPUT, 'w') as out:
        json.dump({'root': {'children': json_list, 'id': root_id}}, out) 

def get_text_in_image(img):
    # th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    # cv2.THRESH_BINARY,11,4)
    # st = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    # th3 = cv2.morphologyEx(th3, cv2.MORPH_OPEN, st, iterations=4)
    # # enhancer = ImageEnhance.Sharpness(img)
    # # enhancer.enhance(0.8)

    # can = cv2.Canny(img, 100, 200, 10)
    # st = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2))
    # can = cv2.morphologyEx(can, cv2.MORPH_GRADIENT, st, iterations=4)

    return pytesseract.image_to_string(Image.fromarray(img))

if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 2:
        f = sys.argv[1]
    else:
        f = INPUT

    #read in
    og_img = cv2.imread(f)
    if og_img.shape[0] > 720 or og_img.shape[1] > 1280:
        og_img = cv2.resize(og_img, (720, 1280))

    #preprocess
    global IMG
    img = cv2.cvtColor(og_img, cv2.COLOR_BGR2GRAY)
    IMG = img.copy()

    # canny edge detection
    can = cv2.Canny(img, 50, 200)
    st = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    can = cv2.morphologyEx(can, cv2.MORPH_CLOSE, st, iterations=1)

    global PROC_IMG
    PROC_IMG = can.copy()

    _, rects, _, _ = find_shapes(can)

    # print "++++===========++++"

    rects = deduplicate_rects(rects)

    rectangles = make_rectangles(rects)
    tree = buildTreeFromList(rectangles)

    save_to_json(tree)

    can = cv2.cvtColor(can, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(can, rects, -1, (0, 255, 0), 3 )

    # cv2.imshow('rectangles', can)
    # ch = 0xFF & cv2.waitKey()

