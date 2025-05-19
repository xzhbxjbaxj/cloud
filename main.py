import requests
import os
url=os.getenv("FC_URL")
try:
    response = requests.get(url)
    response.raise_for_status()
    print("📨 返回内容:", response.text)
except requests.exceptions.RequestException as e:
    print("❌ 请求失败:", e)
