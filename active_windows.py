import psutil
import ctypes

from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer


def get_foreground_window_title() -> Optional[str]:
    hwnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hwnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def get_active_window() -> Optional[list[str]]:
    name, active_window_name = '', ''
    active_window_name = get_foreground_window_title()
    # print(active_window_name)
    if active_window_name:
        active_window_name = active_window_name.replace('–', '-').replace('|', '-').split(' - ')[::-1]
    pid = wintypes.DWORD()
    active = ctypes.windll.user32.GetForegroundWindow()
    active_window = ctypes.windll.user32.GetWindowThreadProcessId(active, ctypes.byref(pid))
    pid = pid.value
    for item in psutil.process_iter():
        if pid == item.pid:
            name = [item.name()]
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
        elif res[0] == 'explorer.exe':
            res = res[0:1]
        elif res[0] == 'ApplicationFrameHost.exe':
            res = res[1:2]
        else:
            if len(res) > 1 and res[1].lower().replace(" ", "") in res[0].lower():
                res = res[1:2]
    if res:
        for i, v in enumerate(res):
            res[i] = v.replace("-", " ")
    return res


if __name__ == "__main__":
    import win32gui
    import pyautogui

    a = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    print(a)

    window_title = pyautogui.getActiveWindowTitle()
    print(window_title)
