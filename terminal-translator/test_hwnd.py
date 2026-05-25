# -*- coding: utf-8 -*-
import win32gui
import ctypes

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('gbk', errors='replace').decode('gbk'))

# 获取当前控制台窗口
kernel32 = ctypes.windll.kernel32
console_hwnd = kernel32.GetConsoleWindow()
safe_print(f"当前控制台窗口句柄: {console_hwnd}")

# 枚举所有窗口
def enum_callback(hwnd, _):
    class_name = win32gui.GetClassName(hwnd)
    if class_name == "ConsoleWindowClass":
        title = win32gui.GetWindowText(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        is_plugin = (hwnd == console_hwnd)
        safe_print(f"  HWND={hwnd} | vis={visible} | size={width}x{height} | plugin={is_plugin} | '{title}'")

safe_print("\n所有 ConsoleWindowClass 窗口:")
win32gui.EnumWindows(enum_callback, None)
