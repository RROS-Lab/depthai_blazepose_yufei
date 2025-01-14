import math
import gripper_fcn as gf
import time

def image2camera(resoltion, z, px, py):
    fx = 1485.7717 * resoltion
    fy = 1483.8920 * resoltion
    cx = 968.5076 * resoltion
    cy = 537.6301 * resoltion

    # while True:
        # z = float(input('Z: '))
        # px = float(input('pixel x_coord: '))
        # py = float(input('pixel y_coord: '))

    x = ((px - cx) * z) / fx
    y = ((py - cy) * z) / fy

    print(x)
    print(y)


def isInCell(x, y):
    # (770, 590) (707, 345)
    # y = 3.89x - 2404.44
    if (y < 345 or y > 590):
        return False
    if (y < 3.89 * x - 2404.44 or x < 440):
        return False
    return True    


# calculate distance between two numpy points
def get_distance(x, y):
    a = x[0] - y[0]
    b = x[1] - y[1]
    c = x[2] - y[2]
    return math.sqrt(a * a + b * b + c * c)


def open_gripper(grip):

    #grip.resetActivate()
    # grip.reset()
    # grip.printInfo()
    # grip.activate()
    # grip.printInfo()
    print("gripper opening ...................")
    grip.goTo(0)
    # time.sleep(2)
    # grip.goTo(230)
    # time.sleep(2)

def close_gripper(grip):

    print("gripper closing ...................")
    grip.goTo(205)

# get the system-wise time in sec
def now():
    return time.perf_counter()