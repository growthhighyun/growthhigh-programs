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
    today = datetime.now().strftime('%Y-%m-%d')
    year_2026 = '2026-01-01'

    print(f"수집 시작 / 기준일: {today}")

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

            print(f"페이지 {page} / {(total//per_page)+1} ({len(items)}건 / 총 {total}건)")

            if not items:
                break

            for item in items:
                end_date = item.get('신청종료일자', '') or ''
                reg_date = item.get('등록일자', '') or ''

                is_2026   = reg_date >= year_2026
                no_end    = end_date == ''
                not_ended = end_date != '' and end_date >= today

                if is_2026 or no_end or not_ended:
                    all_data.append({
                        "id":        str(item.get('번호', '')),
                        "name":      item.get('사업명', ''),
                        "org":       item.get('소관기관', ''),
                        "agency":    item.get('수행기관', ''),
                        "field":     item.get('분야', ''),
                        "startDate": item.get('신청시작일자', ''),
                        "endDate":   item.get('신청종료일자', ''),
                        "url":       item.get('상세URL', ''),
                        "regDate":   reg_date,
                    })

            if page * per_page >= total:
                break
            page += 1

        except Exception as e:
            print(f"에러 page {page}: {e}")
            import traceback
            traceback.print_exc()
            break

    all_data.sort(key=lambda x: x.get('regDate', ''), reverse=True)
    print(f"수집 완료: 총 {len(all_data)}건")
    return all_data


programs = fetch_programs()

output = {
    "updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
    "count": len(programs),
    "data": programs
}

with open('programs.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"저장 완료: {len(programs)}건")
