# from time import sleep

import psutil
import ctypes
from ctypes import wintypes

# for i in range(1, 100000000):
#     pid = wintypes.DWORD()
#     active = ctypes.windll.user32.GetForegroundWindow()
#     active_window = ctypes.windll.user32.GetWindowThreadProcessId(active, ctypes.byref(pid))
#
#     pid = pid.value
#     for item in psutil.process_iter():
#         print(item.name())
#         if pid == item.pid:
#             print(item.name())
#     sleep(1)

from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer


def get_foreground_window_title() -> Optional[str]:
    hwnd = windll.user32.GetForegroundWindow()
    # print(hWnd)
    length = windll.user32.GetWindowTextLengthW(hwnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    if buf.value:
        return buf.value
    else:
        return None


def get_active_window():
    # print()
    name, active_window_name = '', ''

    active_window_name = get_foreground_window_title()
    # print(active_window_name)
    if active_window_name:
        active_window_name = active_window_name.replace('–', '-').replace('|', '-').split(' - ')[::-1]

    # print(active_window_name)

    pid = wintypes.DWORD()
    active = ctypes.windll.user32.GetForegroundWindow()
    active_window = ctypes.windll.user32.GetWindowThreadProcessId(active, ctypes.byref(pid))
    # print(active_window)
    pid = pid.value
    for item in psutil.process_iter():
        # print(item.name())
        if pid == item.pid:
            name = [item.name()]
            # print(name)
    # sleep(1)
    res = []
    if name:
        res += name
    if active_window_name:
        res += active_window_name
    if len(res) == 0:
        res = None

    # make names more convenient to understand

    if len(res) >= 2:
        if res[0] == 'chrome.exe':
            res.pop(0)
            if len(res) > 2:
                res = res[0:2]
            # if res[1] == 'YouTube':
            #     res = res[0:2]
        elif res[0] == 'explorer.exe':
            res = res[0:1]
            # res.pop(0)
            # if res[0] == 'Program Manager':
            #     res = ["Desktop"]
            # else:
            #     res = ["Folders"]
        else:
            if len(res) > 2:
                res = res[0:2]

        if len(res) > 1 and res[1].lower().replace(" ", "") in res[0].lower():
            res.pop(0)

    # print(res)
    return res


if __name__ == "__main__":
    import win32gui

    w = win32gui
    a = w.GetWindowText(w.GetForegroundWindow())
    # print(a)

    import pyautogui

    window_title = pyautogui.getActiveWindowTitle()
    # print(window_title)

    # for i in range(1, 100000000):
    #     print(get_active_window())


# from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
#
#
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.setStyleSheet("background: black")
#         self.setWindowOpacity(0.9)


# if __name__ == '__main__':
#     app = QApplication([])
#
#     mw = MainWindow()
#     mw.showFullScreen()
#
#     ok = QMessageBox.question(None, 'Question', 'Question?')
#     if ok == QMessageBox.Yes:
#         print('User select Ok')
#     else:
#         print('User select No')
#
#     # Убираем затемнение
#     mw.close()
#
#     app.exec()


# importing the module
# import screen_brightness_control as sbc
#
# # get current brightness value
# prev = sbc.get_brightness()
# print(prev)
#
# # set brightness to 50%
# sbc.set_brightness(1)
#
# print(sbc.get_brightness())
# sleep(2)
# # set the brightness of the primary display to 75%
# sbc.set_brightness(prev[0])
#
# print(sbc.get_brightness())
