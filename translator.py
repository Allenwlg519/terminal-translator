import requests
import re
import yaml
import hashlib
import random
import json

class Translator:
    def __init__(self):
        self._cache: dict[str, str] = {}
        self._baidu_app_id = ""
        self._baidu_secret_key = ""
        self._load_config()

    def _load_config(self):
        """加载百度翻译API配置"""
        try:
            with open("config.yaml", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                if "baidu" in cfg:
                    self._baidu_app_id = cfg["baidu"].get("app_id", "")
                    self._baidu_secret_key = cfg["baidu"].get("secret_key", "")
        except:
            pass

    def translate(self, text: str) -> str:
        if text in self._cache:
            return self._cache[text]

        # 清理文本（去除多余空白）
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return ""

        print(f"[翻译] 请求: {text[:30]}...")

        # 首先尝试百度翻译
        if self._baidu_app_id and self._baidu_secret_key:
            result = self._translate_baidu(text)
            if result:
                return result
        
        # 百度翻译失败或未配置，使用Google翻译
        return self._translate_google(text)

    def _translate_baidu(self, text: str) -> str:
        """使用百度翻译API"""
        try:
            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            
            salt = str(random.randint(32768, 65536))
            sign_str = f"{self._baidu_app_id}{text}{salt}{self._baidu_secret_key}"
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            
            params = {
                "q": text,
                "from": "en",
                "to": "zh",
                "appid": self._baidu_app_id,
                "salt": salt,
                "sign": sign
            }
            
            resp = requests.get(url, params=params, timeout=15)
            
            if resp.status_code == 200:
                result = resp.json()
                if "trans_result" in result and len(result["trans_result"]) > 0:
                    translated = result["trans_result"][0]["dst"]
                    self._cache[text] = translated
                    print(f"[翻译] 百度成功: {translated[:30]}...")
                    return translated
                else:
                    print(f"[翻译] 百度响应格式错误: {result}")
                    return ""
            else:
                print(f"[翻译] 百度API失败: {resp.status_code}")
                return ""
                
        except Exception as e:
            print(f"[翻译] 百度API异常: {type(e).__name__}: {e}")
            return ""

    def _translate_google(self, text: str) -> str:
        """使用Google翻译API"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "en",
                "tl": "zh-CN",
                "dt": "t",
                "q": text
            }
            
            resp = requests.get(url, params=params, timeout=15)
            
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, list) and len(result) > 0 and len(result[0]) > 0:
                    translated = result[0][0][0]
                    self._cache[text] = translated
                    print(f"[翻译] Google成功: {translated[:30]}...")
                    return translated
                else:
                    print(f"[翻译] Google响应格式错误: {result}")
                    return ""
            else:
                print(f"[翻译] Google API失败: {resp.status_code}")
                return ""
                
        except Exception as e:
            print(f"[翻译] Google API异常: {type(e).__name__}: {e}")
            return ""
