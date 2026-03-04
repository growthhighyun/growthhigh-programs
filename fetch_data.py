import requests
import json
from datetime import datetime
import os

API_KEY = os.environ.get('API_KEY')
BIZINFO_URL = "https://www.bizinfo.go.kr/uss/rss/bizInfoRss.do"

def fetch_programs():
    all_data = []
    page = 1
    per_page = 100
    today = datetime.now().strftime('%Y%m%d')
    year_2026 = '20260101'

    print(f"bizinfo.go.kr 수집 시작 / 기준일: {today}")

    while True:
        try:
            res = requests.get(BIZINFO_URL, params={
                'dataType': 'json',
                'pageUnit': per_page,
                'pageIndex': page,
                'serviceKey': API_KEY,
            }, timeout=60)

            print(f"HTTP 상태: {res.status_code}")

            data = res.json()

            # 첫 페이지 필드 확인
            if page == 1:
                items_sample = data.get('jsonArray', data.get('data', data.get('items', [])))
                if items_sample:
                    print(f"필드 목록: {list(items_sample[0].keys())}")
                    print(f"샘플: {json.dumps(items_sample[0], ensure_ascii=False)}")
                print(f"응답 키 목록: {list(data.keys())}")

            items = (
                data.get('jsonArray') or
                data.get('data') or
                data.get('items') or
                data.get('result') or
                []
            )

            total = int(
                data.get('totalCount') or
                data.get('total') or
                data.get('totalCnt') or
                0
            )

            print(f"페이지 {page} ({len(items)}건 / 총 {total}건)")

            if not items:
                print("데이터 없음 - 종료")
                break

            for item in items:
                # 날짜 필드 (bizinfo 형식: 20260101)
                end_date = (
                    item.get('pbancEndDe') or
                    item.get('reqstEndDe') or
                    item.get('endDe') or
                    ''
                )
                reg_date = (
                    item.get('creatDt') or
                    item.get('regDt') or
                    item.get('insDt') or
                    ''
                )

                end_date = str(end_date).replace('-', '')
                reg_date = str(reg_date).replace('-', '')

                is_2026   = reg_date >= year_2026
                no_end    = end_date == '' or end_date == 'None'
                not_ended = end_date != '' and end_date != 'None' and end_date >= today

                if is_2026 or no_end or not_ended:
                    def fmt(d):
                        d = str(d).replace('-','')
                        if len(d) == 8:
                            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
                        return d or ''

                    all_data.append({
                        "id":        str(item.get('pbancSn') or item.get('pblancId') or ''),
                        "name":      item.get('pbancNm') or item.get('pblancNm') or '',
                        "org":       item.get('jrsdInsttNm') or item.get('mnofNm') or '',
                        "agency":    item.get('excInsttNm') or item.get('insttNm') or '',
                        "field":     item.get('bsnsSeCdNm') or item.get('indutyNm') or '',
                        "startDate": fmt(item.get('pbancBgngDe') or item.get('reqstBgngDe') or ''),
                        "endDate":   fmt(end_date),
                        "url":       item.get('detlPageUrl') or item.get('pblancUrl') or '',
                        "region":    item.get('areaNmArray') or item.get('areaNm') or '전국',
                        "regDate":   fmt(reg_date),
                    })

            if total == 0 or page * per_page >= total:
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
