import sys
import threading
import yaml
import pytesseract
from translator import Translator
from monitor import TerminalMonitor
from overlay import TranslationOverlay

# 强制刷新输出
sys.stdout.reconfigure(line_buffering=True)

def load_config(path="config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()

    # 配置 Tesseract 路径（确保在初始化 monitor 前设置）
    tesseract_path = cfg.get("tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    print(f"配置 Tesseract 路径: {tesseract_path}")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # 使用新的 Translator（无需 API 密钥）
    translator = Translator()

    ui_cfg = cfg["ui"]
    overlay = TranslationOverlay(
        opacity=ui_cfg["opacity"],
        font_size=ui_cfg["font_size"],
        auto_hide=ui_cfg["auto_hide"],
        position=ui_cfg["position"],
    )

    mon_cfg = cfg["monitor"]
    monitor = TerminalMonitor(
        interval=mon_cfg["interval"],
        english_threshold=mon_cfg["english_threshold"],
        min_length=mon_cfg["min_length"],
        ignore_keywords=mon_cfg["ignore_keywords"],
    )

    def on_text(text: str):
        print(f"\n>>> 检测到英文: {text[:50]}...")
        translated = translator.translate(text)
        if translated:
            print(f">>> 翻译结果: {translated}")
            overlay.show(text, translated)

    monitor.start(on_text)
    print("终端翻译工具已启动，自动监听终端窗口输出。双击悬浮窗关闭。")
    overlay.run()

if __name__ == "__main__":
    main()
