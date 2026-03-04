import requests
import json
from datetime import datetime
import os

API_KEY = os.environ.get('API_KEY')
BASE_URL = "https://api.odcloud.kr/api/3034791/v1/uddi:fa09d13d-bce8-474e-b214-8008e79ec08f"

res = requests.get(BASE_URL, params={
    'page': 1,
    'perPage': 3,
    'serviceKey': API_KEY,
    'returnType': 'json'
}, timeout=60)

data = res.json()
sample = data.get('data', [])
total = data.get('totalCount', 0)

print(f"총 건수: {total}")
print(f"필드 목록: {list(sample[0].keys()) if sample else '없음'}")
print(f"샘플 1번:")
print(json.dumps(sample[0], ensure_ascii=False, indent=2) if sample else '없음')

with open('programs.json', 'w', encoding='utf-8') as f:
    json.dump({"updated": datetime.now().strftime('%Y-%m-%d %H:%M'), "count": 0, "data": []}, f, ensure_ascii=False)

print("완료")
