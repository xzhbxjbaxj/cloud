import requests

url = "https://small-union-d8c6.folxekye28.workers.dev/"

try:
    response = requests.get(url)
    response.raise_for_status()
    print("📨 返回内容:", response.text)
except requests.exceptions.RequestException as e:
    print("❌ 请求失败:", e)
