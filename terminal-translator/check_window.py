import win32gui

# 获取当前活动窗口
hwnd = win32gui.GetForegroundWindow()
title = win32gui.GetWindowText(hwnd)
class_name = win32gui.GetClassName(hwnd)

print(f"窗口标题: {title}")
print(f"窗口类名: {class_name}")

# 检查是否为终端
terminal_classes = ["ConsoleWindowClass", "Windows.Terminal", "VTConsoleClass"]
terminal_terms = ["powershell", "cmd.exe", "terminal", "bash", "wsl", "命令提示符"]

is_terminal = False
if class_name in terminal_classes:
    is_terminal = True
else:
    for term in terminal_terms:
        if term in title.lower():
            is_terminal = True

print(f"是否为终端: {'是' if is_terminal else '否'}")