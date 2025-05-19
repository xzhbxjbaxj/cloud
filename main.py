import requests
import os
url=os.getenv("FC_URL")
try:
    response = requests.get(url)
    response.raise_for_status()
    data=response.json()
    if(data['code']==0):print(data['msg'])
    else:print(data['msg'])
except requests.exceptions.RequestException as e:
    print("❌ 请求失败:", e)
