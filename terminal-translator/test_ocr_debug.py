# -*- coding: utf-8 -*-
"""诊断：查看OCR到底识别到了什么，以及过滤后剩什么"""
import win32gui
import win32con
import win32ui
import ctypes
import pytesseract
import re
import yaml
from PIL import Image

try:
    with open("config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pytesseract.pytesseract.tesseract_cmd = cfg.get("tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
except:
    pass

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('gbk', errors='replace').decode('gbk'))

def capture_window(hwnd):
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width, height = right - left, bottom - top
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)
        save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer("RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1)
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        return img
    except Exception as e:
        safe_print(f"截图失败: {e}")
        return None

# 找到CMD窗口
console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
terminals = []
def enum_cb(hwnd, _):
    if not win32gui.IsWindowVisible(hwnd):
        return True
    cn = win32gui.GetClassName(hwnd)
    if cn == "ConsoleWindowClass" and hwnd != console_hwnd:
        r = win32gui.GetWindowRect(hwnd)
        w, h = r[2]-r[0], r[3]-r[1]
        if w >= 200 and h >= 100:
            terminals.append(hwnd)
    return True
win32gui.EnumWindows(enum_cb, None)

safe_print(f"找到 {len(terminals)} 个CMD窗口")

for hwnd in terminals:
    title = win32gui.GetWindowText(hwnd)
    safe_print(f"\n{'='*60}")
    safe_print(f"窗口: '{title}' (HWND={hwnd})")
    safe_print(f"{'='*60}")
    
    img = capture_window(hwnd)
    if not img:
        safe_print("截图失败!")
        continue
    
    img.save("debug_latest.png")
    safe_print(f"截图: {img.size[0]}x{img.size[1]}, 已保存 debug_latest.png")
    
    # OCR原始文本
    raw_text = pytesseract.image_to_string(img, lang="eng").strip()
    safe_print(f"\n--- OCR原始文本 ({len(raw_text)} 字符) ---")
    safe_print(raw_text[:500] if raw_text else "(空)")
    
    # 逐行分析过滤
    safe_print(f"\n--- 逐行过滤分析 ---")
    lines = raw_text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        reason = "PASS"
        # 检查各种过滤条件
        if re.match(r'^[A-Z0-9_.\-\s{};]+$', stripped):
            reason = "FILTER: 纯大写文件名"
        elif re.search(r'\{[0-9a-fA-F\-]+\}', stripped):
            reason = "FILTER: GUID"
        elif 'NTUSER' in stripped.upper():
            reason = "FILTER: NTUSER"
        elif re.match(r'^.*\.\s*(txt|dat|exe|dll|sys|ini|log|bat|cmd|ps1|msi|zip|rar|7z|tar|gz|py|js|html|css|json|xml|yaml|yml|md|cpp|c|h|java|class|jar|rb|php|go|rs|toml|cfg|conf|sh|bash|env|reg|blf|container|trans|regtrans)\s*$', stripped, re.IGNORECASE):
            reason = "FILTER: 文件扩展名"
        elif re.match(r'^[A-Za-z0-9_\-\s]+/$', stripped):
            reason = "FILTER: 目录名/"
        elif re.match(r'^[A-Za-z0-9_\-]+/$', stripped):
            reason = "FILTER: 目录名"
        elif re.match(r'^\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}', stripped):
            reason = "FILTER: 日期"
        elif re.match(r'^\d+\s*(File|Dir|bytes)', stripped, re.IGNORECASE):
            reason = "FILTER: 文件计数"
        elif re.match(r'^Volume (in drive|Serial Number)', stripped, re.IGNORECASE):
            reason = "FILTER: 卷标"
        elif re.match(r'^Directory of', stripped, re.IGNORECASE):
            reason = "FILTER: 目录"
        elif re.match(r'^\s*\d+ File\(s\)', stripped, re.IGNORECASE):
            reason = "FILTER: 文件数"
        elif re.match(r'^\s*\d+ Dir\(s\)', stripped, re.IGNORECASE):
            reason = "FILTER: 目录数"
        elif re.match(r'^[A-Za-z0-9_\-]+$', stripped) and len(stripped) < 20:
            reason = "FILTER: 短单词"
        elif re.match(r'^[A-Za-z]:\\[^\s]*$', stripped):
            reason = "FILTER: 路径"
        elif any(re.match(p, stripped) for p in [r'^PS\s+[A-Za-z]:.*>\s*', r'^[A-Za-z]:\\.*>\s*$', r'^C:\\.*>\s*$']):
            reason = "FILTER: 提示符"
        
        safe_print(f"  [{i:2d}] {reason:25s} | {stripped[:80]}")
