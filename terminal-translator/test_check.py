# -*- coding: utf-8 -*-
"""诊断：检查当前所有终端窗口"""
import win32gui
import ctypes
import time

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('gbk', errors='replace').decode('gbk'))

# 获取插件控制台窗口
kernel32 = ctypes.windll.kernel32
console_hwnd = kernel32.GetConsoleWindow()
safe_print(f"插件控制台窗口句柄: {console_hwnd}")
safe_print(f"是否为0: {console_hwnd == 0}")
safe_print("")

# 枚举所有窗口
terminal_classes = {
    "ConsoleWindowClass": "CMD",
    "Windows.Terminal": "Windows Terminal",
    "WindowsTerminal": "Windows Terminal",
}

safe_print("所有终端类窗口:")
def enum_callback(hwnd, _):
    class_name = win32gui.GetClassName(hwnd)
    if class_name in terminal_classes:
        title = win32gui.GetWindowText(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        is_plugin = (hwnd == console_hwnd)
        safe_print(f"  HWND={hwnd} | vis={visible} | size={width}x{height} | is_plugin={is_plugin} | '{title}'")

win32gui.EnumWindows(enum_callback, None)

safe_print("\n请确认：你是否在桌面上新打开了一个CMD窗口？")
safe_print("如果上面列表中没有你的新CMD窗口，说明窗口类名不是ConsoleWindowClass")
