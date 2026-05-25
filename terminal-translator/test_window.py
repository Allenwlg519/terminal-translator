import win32gui
import time

def get_window_info(hwnd):
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    return title, class_name

print("开始检测活动窗口...")
print("请切换到要测试的终端窗口")
time.sleep(3)

for i in range(5):
    hwnd = win32gui.GetForegroundWindow()
    title, class_name = get_window_info(hwnd)
    
    # 处理Unicode编码问题
    try:
        title_display = title.encode('gbk', errors='replace').decode('gbk')
    except:
        title_display = "无法显示"
    
    print("")
    print("检测", i+1, ":")
    print("窗口标题: '", title_display, "'", sep="")
    print("窗口类名:", class_name)
    print("窗口句柄:", hwnd)
    
    # 检查是否为终端类名
    terminal_classes = ["ConsoleWindowClass", "Windows.Terminal", "WindowsTerminal", "VTConsoleClass", "PseudoConsoleWindow", "TrayNotifyWnd"]
    if class_name in terminal_classes:
        print("识别为终端窗口")
    else:
        print("未识别为终端窗口")
        print("建议将类名 '", class_name, "' 添加到终端类名列表中", sep="")
    
    time.sleep(2)
