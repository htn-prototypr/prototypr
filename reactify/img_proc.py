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

IMG = None
INPUT = 'data/pic6.png'
OUTPUT = 'json/app.json'
ID_LENGTH = 5   # for ids used in the json

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

    def to_dict(self):
        node_type = 'container'
        if not self.children:
            crop_img = IMG[self.p1[1]: self.p2[1], self.p1[0]:self.p2[0]]
            node_type = 'do ocr'

        node_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(ID_LENGTH))

        style = {}
        if self.parent is not None:
            style = {
                'width': (int)(self.p2[0] - self.p1[0]),
                'height': (int)(self.p2[1] - self.p1[1]),
                'marginTop': (int)(self.p1[1] - self.parent.p1[1]),
                'marginBottom': (int)(self.parent.p2[1] - self.p2[1]),
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

def find_rects(img):
    rects = []
    ret,thresh = cv2.threshold(img,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
        if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
            cnt = cnt.reshape(-1, 2)
            max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
            if max_cos >= 0.2:
                continue

            rects.append(cnt)
    return rects

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
    json_list = [node.to_dict() for node in tree]
    with open(OUTPUT, 'w') as out:
        json.dump({'root': {'children': json_list}}, out) 

if __name__ == '__main__':
    #read in
    og_img = cv2.imread(INPUT)

    #preprocess
    global IMG
    IMG = cv2.cvtColor(og_img, cv2.COLOR_BGR2GRAY)

    # canny edge detection
    can = cv2.Canny(IMG, 50, 200)
    st = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    can = cv2.morphologyEx(can, cv2.MORPH_CLOSE, st, iterations=1)

    rects = find_rects(can)
    rects = deduplicate_rects(rects)

    rectangles = make_rectangles(rects)
    tree = buildTreeFromList(rectangles)

    save_to_json(tree)

    can = cv2.cvtColor(can, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(can, rects, -1, (0, 255, 0), 3 )

    cv2.imshow('rectangles', can)
    ch = 0xFF & cv2.waitKey()

