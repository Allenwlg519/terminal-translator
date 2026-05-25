# -*- coding: utf-8 -*-
"""诊断测试脚本2 - 列出所有窗口并尝试单独截取CMD窗口"""
import win32gui
import win32con
import win32ui
import pytesseract
import time
import os
import yaml
import re
from PIL import Image

# 初始化 Tesseract
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
        
        save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
        
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
        safe_print(f"  截图失败: {e}")
        return None

# ===== 列出所有可见窗口 =====
safe_print("=" * 60)
safe_print("列出所有可见窗口")
safe_print("=" * 60)

windows = []

def enum_callback(hwnd, _):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if title:  # 只显示有标题的窗口
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width, height = right - left, bottom - top
            windows.append({
                'hwnd': hwnd,
                'title': title,
                'class': class_name,
                'size': f"{width}x{height}",
                'visible': True
            })

win32gui.EnumWindows(enum_callback, None)

safe_print(f"\n找到 {len(windows)} 个可见窗口:\n")

# 按窗口类名分组显示
terminal_classes = ["ConsoleWindowClass", "Windows.Terminal", "WindowsTerminal"]
terminal_keywords = ["cmd", "powershell", "terminal", "bash", "wsl"]

for i, w in enumerate(windows):
    is_term = w['class'] in terminal_classes
    has_keyword = any(kw in w['title'].lower() for kw in terminal_keywords)
    marker = " <<< TERMINAL" if (is_term or has_keyword) else ""
    
    safe_print(f"  [{i}] HWND={w['hwnd']} | 类名={w['class']} | 大小={w['size']}")
    safe_print(f"      标题: '{w['title']}'{marker}")

# ===== 尝试截取终端窗口 =====
safe_print(f"\n{'=' * 60}")
safe_print("尝试截取终端窗口并OCR")
safe_print("=" * 60)

for i, w in enumerate(windows):
    is_term = w['class'] in terminal_classes
    has_keyword = any(kw in w['title'].lower() for kw in terminal_keywords)
    
    if is_term or has_keyword:
        safe_print(f"\n--- 截取窗口: '{w['title']}' (类名: {w['class']}) ---")
        
        img = capture_window(w['hwnd'])
        if img:
            safe_print(f"  截图成功: {img.size[0]}x{img.size[1]}")
            img.save(f"debug_terminal_{i}.png")
            safe_print(f"  已保存: debug_terminal_{i}.png")
            
            # OCR识别
            try:
                raw_text = pytesseract.image_to_string(img, lang="eng").strip()
                if raw_text:
                    display = raw_text[:300].replace('\n', '\\n')
                    safe_print(f"  OCR文本 ({len(raw_text)} 字符):")
                    safe_print(f"  '{display}'")
                else:
                    safe_print(f"  OCR未识别到文本!")
                    # 尝试截取下半部分
                    w_img, h_img = img.size
                    bottom_half = img.crop((0, h_img // 2, w_img, h_img))
                    raw_text2 = pytesseract.image_to_string(bottom_half, lang="eng").strip()
                    if raw_text2:
                        display = raw_text2[:300].replace('\n', '\\n')
                        safe_print(f"  下半部分OCR ({len(raw_text2)} 字符):")
                        safe_print(f"  '{display}'")
                    else:
                        safe_print(f"  下半部分OCR也无文本!")
            except Exception as e:
                safe_print(f"  OCR失败: {e}")
        else:
            safe_print(f"  截图失败!")

safe_print(f"\n诊断完成!")
