import requests
import json
from datetime import datetime
import os

API_KEY = os.environ.get('API_KEY')
BASE_URL = "https://api.odcloud.kr/api/3034791/v1/uddi:fa09d13d-bce8-474e-b214-8008e79ec08f"

def fetch_programs():
    all_data = []
    page = 1
    per_page = 1000

    print(f"수집 시작: {datetime.now()}")

    while True:
        try:
            res = requests.get(BASE_URL, params={
                'page': page,
                'perPage': per_page,
                'serviceKey': API_KEY,
                'returnType': 'json'
            }, timeout=60)

            data = res.json()
            items = data.get('data', [])
            total = data.get('totalCount', 0)

            print(f"페이지 {page}/{(total//per_page)+1} ({len(items)}건)")

            if not items:
                break

            for item in items:
                # 필드 최소화로 용량 절약
                all_data.append({
                    "id":  str(item.get('번호', '')),
                    "n":   item.get('사업명', ''),
                    "o":   item.get('소관기관', ''),
                    "a":   item.get('수행기관', ''),
                    "f":   item.get('분야', ''),
                    "s":   item.get('신청시작일자', ''),
                    "e":   item.get('신청종료일자', ''),
                    "u":   item.get('상세URL', ''),
                    "r":   item.get('등록일자', ''),
                })

            if page * per_page >= total:
                break
            page += 1

        except Exception as e:
            print(f"에러 page {page}: {e}")
            import traceback
            traceback.print_exc()
            break

    # 최신순 정렬
    all_data.sort(key=lambda x: x.get('r', ''), reverse=True)
    print(f"수집 완료: {len(all_data)}건")
    return all_data


programs = fetch_programs()

output = {
    "updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
    "count": len(programs),
    "data": programs
}

with open('programs.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

print(f"저장 완료: {len(programs)}건")
