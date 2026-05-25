from monitor import TerminalMonitor

def test_callback(text):
    print(f"\n=== 检测到新的英文内容 ===")
    print(f"原文: {text}")
    print("==========================")

# 创建监控器
monitor = TerminalMonitor(
    interval=1.0,
    english_threshold=0.8,
    min_length=5,
    ignore_keywords=["password", "token"]
)

print("终端监控器测试")
print("请切换到终端窗口，输入英文命令")
print("按 Ctrl+C 退出")

try:
    monitor.start(test_callback)
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
    print("\n测试结束")