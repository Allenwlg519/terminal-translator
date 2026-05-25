# -*- coding: utf-8 -*-
"""诊断测试脚本 - 逐步排查为什么无法识别CMD内容"""
import win32gui
import win32con
import win32ui
import win32api
import pytesseract
import time
import os
import yaml
from PIL import Image

# 初始化 Tesseract
try:
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pytesseract.pytesseract.tesseract_cmd = cfg.get("tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
except:
    pass

def safe_print(msg):
    """安全打印，避免GBK编码错误"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('gbk', errors='replace').decode('gbk'))

def capture_window(hwnd):
    """截取窗口截图"""
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width, height = right - left, bottom - top
        if width <= 0 or height <= 0:
            return None
        
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)
        
        result = save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
        
        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        
        return img
    except Exception as e:
        safe_print(f"截图失败: {e}")
        return None

def is_plugin_window(content):
    """检查是否为插件窗口"""
    if not content:
        return False
    plugin_patterns = [
        "[监控]", "检测到英文", "翻译结果:", ">>> 检测到英文",
        "翻译 请求:", "翻译 成功:", "[调试]", "python main.py",
    ]
    for pattern in plugin_patterns:
        if pattern in content:
            return True
    return False

def is_terminal(title, class_name):
    """检查是否为终端"""
    terminal_classes = [
        "ConsoleWindowClass", "Windows.Terminal", "WindowsTerminal",
        "VTConsoleClass", "PseudoConsoleWindow",
    ]
    terminal_terms = [
        "powershell.exe", "cmd.exe", "-bash", "-wsl", "-ubuntu", "-debian",
        "bash.exe", "wsl.exe", "powershell", "command prompt", "terminal",
    ]
    exclude_classes = [
        "CabinetWClass", "ExploreWClass", "MozillaWindowClass",
        "Notepad", "TfrmMain", "Progman", "WorkerW", "Shell_TrayWnd",
    ]
    exclude_terms = [
        "explorer", "visual studio", "vscode", "jetbrains", "pycharm",
        "chrome", "firefox", "edge", ".py", ".txt", ".json", ".yaml",
        "- trae", "- trae cn",
    ]
    
    lower_title = title.lower()
    
    if class_name in exclude_classes:
        return False, f"排除: 类名 '{class_name}'"
    
    for term in exclude_terms:
        if term in lower_title:
            return False, f"排除: 标题含 '{term}'"
    
    if class_name in terminal_classes:
        return True, f"识别: 类名 '{class_name}'"
    
    for term in terminal_terms:
        if term in lower_title:
            return True, f"识别: 标题含 '{term}'"
    
    if class_name == "Chrome_WidgetWin_1":
        if "terminal" in lower_title or "powershell" in lower_title or "cmd" in lower_title:
            return True, "识别: Trae IDE 终端"
    
    return False, "未识别"

def is_english(text):
    """检查是否为英文"""
    if len(text) < 10:
        return False, "长度不足10"
    
    # 检查文件路径
    import re
    if re.search(r'[A-Za-z]:\\[^\\\s]+', text):
        return False, "包含文件路径"
    
    # 检查特殊字符比例
    special_chars = r'[^\w\s\n\r\t.,!?;:(){}[\]<>+\-*/=~`@#$%^&|\\]'
    special_count = len(re.findall(special_chars, text))
    if special_count > len(text) * 0.1:
        return False, f"特殊字符过多 ({special_count}/{len(text)})"
    
    # 检查乱码
    invalid_patterns = [
        r'[a-zA-Z]{8,}',
        r'([a-zA-Z])\1{3,}',
        r'[^a-zA-Z0-9\s]{4,}',
    ]
    for pattern in invalid_patterns:
        if re.search(pattern, text):
            return False, f"匹配乱码模式 '{pattern}'"
    
    # 检查ASCII比例
    ascii_count = sum(1 for c in text if ord(c) < 128)
    ratio = ascii_count / len(text)
    if ratio < 0.5:
        return False, f"ASCII比例过低 ({ratio:.2f})"
    
    # 检查英文单词
    words = re.findall(r'[a-zA-Z]{2,}', text)
    if len(words) < 2:
        return False, f"英文单词不足 ({len(words)})"
    
    avg_word_length = sum(len(w) for w in words) / len(words)
    if avg_word_length < 2 or avg_word_length > 15:
        return False, f"平均单词长度异常 ({avg_word_length:.1f})"
    
    return True, "是英文"

# ===== 主测试 =====
safe_print("=" * 60)
safe_print("诊断测试开始")
safe_print("请在3秒内切换到CMD窗口!")
safe_print("=" * 60)
time.sleep(3)

for i in range(3):
    safe_print(f"\n{'=' * 40}")
    safe_print(f"测试轮次 {i+1}")
    safe_print(f"{'=' * 40}")
    
    # 步骤1: 获取活动窗口
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    
    safe_print(f"\n[步骤1] 活动窗口信息:")
    safe_print(f"  标题: '{title}'")
    safe_print(f"  类名: {class_name}")
    safe_print(f"  句柄: {hwnd}")
    
    # 步骤2: 判断是否为终端
    is_term, term_reason = is_terminal(title, class_name)
    safe_print(f"\n[步骤2] 终端识别:")
    safe_print(f"  结果: {is_term}")
    safe_print(f"  原因: {term_reason}")
    
    # 步骤3: 截图
    safe_print(f"\n[步骤3] 窗口截图:")
    img = capture_window(hwnd)
    if img:
        safe_print(f"  截图成功: {img.size[0]}x{img.size[1]}")
        # 保存截图用于调试
        img.save(f"debug_screenshot_{i+1}.png")
        safe_print(f"  已保存: debug_screenshot_{i+1}.png")
    else:
        safe_print(f"  截图失败!")
        time.sleep(2)
        continue
    
    # 步骤4: OCR识别
    safe_print(f"\n[步骤4] OCR识别:")
    try:
        raw_text = pytesseract.image_to_string(img, lang="eng").strip()
        if raw_text:
            # 只显示前200个字符
            display = raw_text[:200].replace('\n', '\\n')
            safe_print(f"  原始文本 ({len(raw_text)} 字符):")
            safe_print(f"  '{display}'")
        else:
            safe_print(f"  OCR未识别到任何文本!")
    except Exception as e:
        safe_print(f"  OCR失败: {e}")
        time.sleep(2)
        continue
    
    # 步骤5: 检查是否为插件窗口
    safe_print(f"\n[步骤5] 插件窗口检查:")
    is_plugin = is_plugin_window(raw_text)
    safe_print(f"  结果: {is_plugin}")
    if is_plugin:
        safe_print(f"  -> 内容被识别为插件输出，将被跳过!")
    
    # 步骤6: 清理文本
    safe_print(f"\n[步骤6] 文本清理:")
    # 去除提示符
    clean_text = raw_text
    prompt_patterns = [
        r'PS\s+[A-Za-z]:[^>]*>\s*',
        r'[A-Za-z]:\\[^>]*>\s*',
        r'\$\s*$',
        r'#\s*$',
    ]
    import re
    for pattern in prompt_patterns:
        clean_text = re.sub(pattern, '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    if clean_text:
        display = clean_text[:200]
        safe_print(f"  清理后文本 ({len(clean_text)} 字符):")
        safe_print(f"  '{display}'")
    else:
        safe_print(f"  清理后无文本!")
    
    # 步骤7: 英文检测
    safe_print(f"\n[步骤7] 英文检测:")
    is_eng, eng_reason = is_english(clean_text)
    safe_print(f"  结果: {is_eng}")
    safe_print(f"  原因: {eng_reason}")
    
    # 步骤8: 最终结论
    safe_print(f"\n[步骤8] 最终结论:")
    if is_plugin:
        safe_print(f"  SKIP - 插件窗口")
    elif not is_term:
        safe_print(f"  SKIP - 非终端窗口")
    elif not is_eng:
        safe_print(f"  SKIP - 非英文内容: {eng_reason}")
    else:
        safe_print(f"  OK - 可以翻译!")
    
    time.sleep(2)

safe_print(f"\n诊断测试完成!")
