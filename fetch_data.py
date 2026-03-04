import requests
import json
from datetime import datetime
import os

API_KEY = os.environ.get('API_KEY')
BASE_URL = "https://api.odcloud.kr/api/3034791/v1/uddi:fa09d13d-bce8-474e-b214-8008e79ec08f"

def fetch_active_programs():
    all_data = []
    page = 1
    per_page = 1000
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"[{datetime.now()}] 데이터 수집 시작 (기준일: {today})")
    
    while True:
        try:
            res = requests.get(BASE_URL, params={
                'page': page,
                'perPage': per_page,
                'serviceKey': API_KEY,
                'returnType': 'json'
            }, timeout=30)
            
            data = res.json()
            items = data.get('data', [])
            total = data.get('totalCount', 0)
            
            print(f"  → 페이지 {page} / {(total//per_page) + 1} 처리 중... ({len(items)}건)")
            
            for item in items:
                end_date = item.get('신청종료일자', '') or ''
                if not end_date or end_date >= today:
                    all_data.append({
                        "id":        str(item.get('번호', '')),
                        "name":      item.get('사업명', ''),
                        "org":       item.get('소관기관', ''),
                        "agency":    item.get('수행기관', ''),
                        "field":     item.get('분야', ''),
                        "startDate": item.get('신청시작일자', ''),
                        "endDate":   item.get('신청종료일자', ''),
                        "url":       item.get('상세URL', ''),
                        "region":    item.get('지역', '전국'),
                    })
            
            if page * per_page >= total:
                break
            page += 1
            
        except Exception as e:
            print(f"  ⚠️ 에러 발생 (page {page}): {e}")
            break
    
    print(f"✅ 수집 완료: 총 {len(all_data)}건")
    return all_data

programs = fetch_active_programs()

output = {
    "updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
    "count": len(programs),
    "data": programs
}

with open('programs.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"💾 programs.json 저장 완료 ({len(programs)}건)")
