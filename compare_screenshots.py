from win32api import GetSystemMetrics
import numpy as np
import time
import pyautogui


def main():
    width = GetSystemMetrics(0)
    height = GetSystemMetrics(1)

    x1 = int(width * 10 / 100)
    x2 = int(width * 70 / 100)
    y1 = int(height * 20 / 100)
    y2 = int(height * 80 / 100)

    first = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    time.sleep(3)
    second = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    diff = np.bitwise_xor(first, second).any()

    if diff:
        return 1
    else:
        return 0









