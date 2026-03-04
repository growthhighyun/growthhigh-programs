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
    
    print(f"[{datetime.now()}] 데이터 수집 시작")
    
    # 1페이지만 먼저 확인 (총 건수 파악)
    try:
        res = requests.get(BASE_URL, params={
            'page': 1,
            'perPage': 10,
            'serviceKey': API_KEY,
            'returnType': 'json',
            'cond[등록일자::GTE]': '2024-01-01'  # 2024년 이후 등록
        }, timeout=60)
        
        print(f"HTTP 상태: {res.status_code}")
        data = res.json()
        total = data.get('totalCount', 0)
        print(f"필드 샘플: {list(data.get('data', [{}])[0].keys()) if data.get('data') else '없음'}")
        print(f"총 건수: {total}")
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()

    # 전체 수집 (날짜 필터 없이)
    while True:
        try:
            res = requests.get(BASE_URL, params={
                'page': page,
                'perPage': per_page,
                'serviceKey': API_KEY,
                'returnType': 'json',
                'cond[등록일자::GTE]': '2024-01-01'
            }, timeout=60)
            
            data = res.json()
            items = data.get('data', [])
            total = data.get('totalCount', 0)
            
            print(f"  → 페이지 {page} / {(total//per_page)+1} ({len(items)}건 / 총 {total}건)")
            
            if not items:
                break
                
            for item in items:
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
                    "regDate":   item.get('등록일자', ''),
                })
            
            if page * per_page >= total:
                break
            page += 1
            
        except Exception as e:
            print(f"  ⚠️ 에러 (page {page}): {e}")
            break
    
    # 최신 등록순 정렬
    all_data.sort(key=lambda x: x.get('regDate', ''), reverse=True)
    print(f"✅ 수집 완료: 총 {len(all_data)}건")
    return all_data

programs = fetch_programs()

output = {
    "updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
    "count": len(programs),
    "data": programs
}

with open('programs.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"💾 programs.json 저장 완료 ({len(programs)}건)")
