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

    print(f"[{datetime.now()}] 데이터 수집 시작")
    print(f"조건: 등록일 >= {year_2026} OR 마감일 >= {today} OR 상시접수")

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

            print(f"  → 페이지 {page} / {(total//per_page)+1} ({len(items)}건 / 총 {total}건)")

            if not items:
                break

            for item in items:
                end_date  = item.get('신청종료일자', '') or ''
                reg_date  = item.get('등록일자', '')    or ''

                # A안 조건
                # ① 등록일 2026년 이후
                is_2026   = reg_date >= year_2026
                # ② 마감일이 없는 것 (상시접수)
                no_end    = end_date == ''
                # ③ 마감일이 오늘 이후 (아직 유효)
                not_ended = end_date >= today

                if is_2026 or no_end or not_ended:
                    all_data.append({
                        "id":        str(item.get('번호', '')),
                        "name":      item.get('사업명', ''),
                        "org":       item.get('소관기관', ''),
                        "agency":    item.get('수행기관', ''),
                        "field":     item.get('분야', ''),
                        "overview":  item.get('사업개요', '') or item.get('지원내용', '') or '',
                        "startDate": item.get('신청시작일자', ''),
                        "endDate":   item.get('신청종료일자', ''),
                        "url":       item.get('상세URL', ''),
                        "region":    item.get('지역', '전국'),
                        "regDate":   reg_date,
                        "method":    item.get('신청방법', ''),
                        "contact":   item.get('문의처', ''),
                    })

            if page * per_page >= total:
                break
            page += 1

        except Exception as e:
            print(f"  ⚠️ 에러 (page {page}): {e}")
            import traceback
            traceback.print_exc()
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
```

---

저장 후 **Actions → Run workflow** 실행해주세요!

이번엔 로그에서 이런 게 보여야 해요:
```
조건: 등록일 >= 2026-01-01 OR 마감일 >= 2026-03-04 OR 상시접수
✅ 수집 완료: 총 X,XXX건
