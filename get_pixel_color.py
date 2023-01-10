import pyautogui
while True:
    x, y = pyautogui.position()
    print(x, y)
    px = pyautogui.pixel(x, y)
    print(px)