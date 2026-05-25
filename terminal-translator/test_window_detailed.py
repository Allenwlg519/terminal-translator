import win32gui
import time
import sys

print("=" * 60)
print("窗口识别测试工具")
print("=" * 60)
print("请切换到你想测试的窗口（终端或其他程序）")
print("按 Ctrl+C 退出")
print("=" * 60)

# 已知终端类名
terminal_classes = [
    "ConsoleWindowClass",      # CMD
    "Windows.Terminal",        # Windows Terminal
    "WindowsTerminal",         # Windows Terminal (旧版)
    "VTConsoleClass",          # Virtual Terminal
    "PseudoConsoleWindow",     # 伪控制台
]

# 已知终端标题关键词（更精确）
terminal_terms = ["powershell.exe", "cmd.exe", "-bash", "-wsl", "-ubuntu", "-debian", "bash.exe", "wsl.exe"]

# 需要排除的窗口类名
exclude_classes = [
    "CabinetWClass",           # 文件资源管理器
    "ExploreWClass",           # 文件资源管理器
    "Chrome_WidgetWin_1",      # Chrome
    "MozillaWindowClass",      # Firefox
    "Notepad",                 # 记事本
    "TfrmMain",                # 某些应用
    "Progman",                 # 桌面
    "WorkerW",                 # 桌面
    "Shell_TrayWnd",           # 任务栏
]

# 需要排除的标题关键词（IDE、编辑器等）
exclude_terms = [
    "explorer", "文件资源管理器", "图片", "downloads", "文档", "音乐", "视频",
    "visual studio", "vscode", "code", "jetbrains", "pycharm", "intellij",
    "eclipse", "atom", "sublime", "notepad++", "diffview", "terminal-translator",
    "chrome", "firefox", "edge", "brave", "opera", "safari",
    "word", "excel", "powerpoint", "pdf", "adobe", "reader"
]

def is_terminal(title, class_name):
    """判断是否为终端窗口"""
    # 首先排除非终端窗口（类名）
    if class_name in exclude_classes:
        return False, f"排除: 类名 '{class_name}' 匹配非终端"

    # 排除非终端窗口（标题关键词）
    for term in exclude_terms:
        if term in title.lower():
            return False, f"排除: 标题包含 '{term}'"

    # 检查终端类名（精确匹配）
    if class_name in terminal_classes:
        return True, f"识别: 类名 '{class_name}' 匹配终端"

    # 检查标题是否以终端程序结尾
    lower_title = title.lower()
    for term in terminal_terms:
        if lower_title.endswith(term) or (" - " + term) in lower_title:
            return True, f"识别: 标题包含终端程序 '{term}'"

    # 特殊处理: 标题为 "Command Prompt" 或 "PowerShell"
    if lower_title == "command prompt" or lower_title == "powershell":
        return True, "识别: 标题为标准终端"

    return False, "未识别: 非终端窗口"

try:
    last_title = ""
    while True:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)

        # 只在窗口变化时显示
        if title != last_title:
            is_term, reason = is_terminal(title, class_name)
            print(f"\n{'=' * 60}")
            print(f"窗口标题: {title}")
            print(f"窗口类名: {class_name}")
            print(f"判断结果: {'终端' if is_term else '非终端'}")
            print(f"判断原因: {reason}")
            print(f"{'=' * 60}")
            last_title = title

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n\n测试结束")