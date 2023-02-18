import math

def xywh2xyxy(xywh):
    x, y, w, h = xywh
    
    x1, y1 = math.ceil(x), math.ceil(y)
    x2, y2 = math.ceil(x+w), math.ceil(y+h)
    
    
    return [x1, y1, x2, y2]