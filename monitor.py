import time
import threading
import win32gui
import win32con
import win32ui
import ctypes
import yaml
from PIL import Image
import pytesseract
import re
import os

# 初始化 Tesseract
def _init_tesseract():
    try:
        with open("config.yaml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        pytesseract.pytesseract.tesseract_cmd = cfg.get("tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    except:
        pass

_init_tesseract()

class TerminalMonitor:
    def __init__(self, interval: float, english_threshold: float, min_length: int, ignore_keywords: list):
        self.interval = interval
        self.english_threshold = english_threshold
        self.min_length = min_length
        self.ignore_keywords = ignore_keywords
        self._running = False
        self._callback = None
        self._last_texts = {}  # hwnd -> last_text
        self._plugin_hwnd = None

    def _find_terminal_windows(self):
        """枚举所有终端窗口"""
        terminals = []
        terminal_classes = {
            "ConsoleWindowClass": "CMD",
            "Windows.Terminal": "Windows Terminal",
            "WindowsTerminal": "Windows Terminal",
            "VTConsoleClass": "Virtual Terminal",
        }
        def enum_callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            class_name = win32gui.GetClassName(hwnd)
            if class_name in terminal_classes:
                if self._plugin_hwnd and hwnd == self._plugin_hwnd:
                    return True
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width, height = right - left, bottom - top
                if width < 200 or height < 100:
                    return True
                title = win32gui.GetWindowText(hwnd)
                terminals.append({
                    'hwnd': hwnd, 'title': title, 'class': class_name,
                    'type': terminal_classes[class_name], 'size': (width, height),
                })
            return True
        win32gui.EnumWindows(enum_callback, None)
        return terminals

    def _capture_window(self, hwnd):
        """截取窗口截图"""
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
        except:
            return None

    def _clean_text(self, text):
        """简单清理：只去除提示符行和多余空白"""
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 只跳过纯提示符行（如 C:\Users\X> 后面没内容）
            if re.match(r'^[A-Za-z]:\\.*>\s*$', line):
                continue
            if re.match(r'^PS\s+[A-Za-z]:.*>\s*$', line):
                continue
            cleaned.append(line)
        return '\n'.join(cleaned)

    def _is_english(self, text):
        """简单判断：文本中是否有英文字母"""
        if len(text) < self.min_length:
            return False
        # 检查是否有英文字母
        letters = re.findall(r'[a-zA-Z]', text)
        if len(letters) < 3:
            return False
        return True

    def _has_new_content(self, hwnd, text):
        """检查指定窗口是否有新内容（使用相似度比较，避免OCR微小差异导致重复翻译）"""
        last = self._last_texts.get(hwnd, "")
        # 如果长度差距小于20%，且前80个字符相同，认为是相同内容
        if last and abs(len(text) - len(last)) < max(len(text), len(last)) * 0.2:
            if text[:80] == last[:80]:
                return False
        self._last_texts[hwnd] = text
        return True

    def _monitor_loop(self):
        last_log_time = 0
        try:
            self._plugin_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        except:
            self._plugin_hwnd = None
        
        print(f"[监控] 插件控制台窗口: {self._plugin_hwnd}")
        print(f"[监控] 已就绪，正在监控桌面上的终端窗口...")

        while self._running:
            try:
                current_time = time.time()
                terminals = self._find_terminal_windows()
                
                if not terminals:
                    if current_time - last_log_time > 15:
                        print(f"[监控] 未找到终端窗口，请打开CMD或PowerShell...")
                        last_log_time = current_time
                    time.sleep(self.interval)
                    continue
                
                if current_time - last_log_time > 15:
                    term_info = ", ".join(f"{t['type']}(0x{t['hwnd']:X})" for t in terminals)
                    print(f"[监控] 监控中... 终端窗口: {term_info}")
                    last_log_time = current_time
                
                for term in terminals:
                    hwnd = term['hwnd']
                    img = self._capture_window(hwnd)
                    if not img:
                        continue
                    try:
                        raw_text = pytesseract.image_to_string(img, lang="eng").strip()
                    except:
                        continue
                    if not raw_text:
                        continue
                    
                    text = self._clean_text(raw_text)
                    if not text or len(text) < self.min_length:
                        continue
                    if not self._has_new_content(hwnd, text):
                        continue
                    if self._is_english(text):
                        print(f"[监控] 检测到英文内容 ({term['type']}): {text[:80]}...")
                        if self._callback:
                            self._callback(text)
                                
            except Exception as e:
                print(f"[监控] 异常: {e}")
            time.sleep(self.interval)

    def start(self, callback):
        self._callback = callback
        self._running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop(self):
        self._running = False
