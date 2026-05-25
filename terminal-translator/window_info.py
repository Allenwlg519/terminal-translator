import win32gui
import time

def get_window_info():
    """获取活动窗口的信息"""
    hwnd = win32gui.GetForegroundWindow()
    
    # 获取窗口标题
    title = win32gui.GetWindowText(hwnd)
    
    # 获取窗口类名
    class_name = win32gui.GetClassName(hwnd)
    
    # 获取窗口位置
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    print(f"窗口句柄: {hwnd}")
    print(f"窗口标题: {title}")
    print(f"窗口标题(小写): {title.lower()}")
    print(f"窗口类名: {class_name}")
    print(f"窗口位置: ({left}, {top}) - ({right}, {bottom})")
    print(f"窗口大小: {right-left} x {bottom-top}")
    
    return title, class_name

def main():
    print("=" * 60)
    print("窗口信息诊断工具")
    print("=" * 60)
    print("请切换到你想要测试的窗口（终端或文件管理器）")
    print("按 Ctrl+C 退出")
    print("=" * 60)
    
    last_title = ""
    last_class = ""
    
    try:
        while True:
            title, class_name = get_window_info()
            
            # 只在窗口变化时显示
            if title != last_title or class_name != last_class:
                print("\n" + "=" * 60)
                print(f"窗口标题: {title}")
                print(f"窗口类名: {class_name}")
                print(f"建议操作:")
                if "explorer" in class_name.lower() or "cabinet" in class_name.lower():
                    print("  - 这是文件管理器窗口，应该被排除")
                elif "console" in class_name.lower() or "terminal" in class_name.lower():
                    print("  - 这是终端窗口，应该被识别")
                else:
                    print("  - 未知窗口类型")
            
            last_title = title
            last_class = class_name
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n诊断结束")

if __name__ == "__main__":
    main()