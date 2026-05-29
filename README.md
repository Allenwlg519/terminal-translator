# 终端翻译工具

自动监听并翻译终端中的英文输出，通过悬浮窗显示中文翻译。

## 功能特性

- ✅ **自动监听终端输出**（无需手动复制）
- ✅ 实时 OCR 识别 + 翻译
- ✅ 支持拖动、自动隐藏悬浮窗
- ✅ 使用百度翻译 API（免费 5万字/月）
- ✅ 可配置过滤规则和显示样式

## 安装步骤

### 1. 安装 Tesseract OCR 引擎

下载并安装：https://github.com/UB-Mannheim/tesseract/wiki

- 选择 `tesseract-ocr-w64-setup-5.x.x.exe`
- 安装时勾选 **English** 语言包
- 默认安装路径：`C:\Program Files\Tesseract-OCR\`

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API

编辑 `config.yaml`，填入百度翻译 API 密钥：

1. 访问 https://fanyi-api.baidu.com/
2. 注册并创建应用
3. 获取 `APP ID` 和 `密钥`
4. 填入配置文件：

```yaml
baidu:
  app_id: "你的APP_ID"
  secret_key: "你的密钥"

# 如果 Tesseract 安装路径不同，修改此项
tesseract_path: "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

### 4. 启动工具

双击 `启动翻译工具.bat` 或运行：

```bash
python main.py
```

## 使用方法

1. 启动工具后，**切换到终端窗口**（PowerShell/CMD/Git Bash）
2. 工具自动 OCR 识别终端内容
3. 检测到英文输出时，右下角弹出悬浮窗显示翻译
4. 双击悬浮窗可关闭

## 配置说明

编辑 `config.yaml` 自定义：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `monitor.interval` | 检测间隔（秒） | 0.5 |
| `monitor.english_threshold` | 英文字符占比阈值 | 0.5 |
| `monitor.min_length` | 最小文本长度 | 10 |
| `monitor.ignore_keywords` | 忽略的关键词 | npm, git, cd... |
| `ui.opacity` | 窗口透明度 | 0.9 |
| `ui.font_size` | 字体大小 | 12 |
| `ui.auto_hide` | 自动隐藏时间（秒） | 5 |
| `ui.position` | 窗口位置 | right-bottom |

## 常见问题



**Q: 如何更换翻译服务？**  
A: 修改 `translator.py`，替换为其他 API（如腾讯翻译、DeepL）

**Q: 能否监听终端输出而不是剪贴板？**  
A: Windows 下直接监听终端输出需要更复杂的实现（如 hook），当前方案更轻量

## 技术栈

- Python 3.8+
- tkinter（悬浮窗）
- pyperclip（剪贴板监听）
- requests（API 调用）
- 百度翻译 API

## 许可证

MIT License
