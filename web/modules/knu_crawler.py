"""
강원대학교 실시간 공고 크롤러 모듈
프로그램, 대회, 장학금 링크에서 최신 공고를 실시간 수집 및 파싱
"""

import urllib.request
import ssl
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8'
}


def parse_dates_from_title(title: str, default_date: str = ""):
    """제목이나 텍스트에서 접수기간 및 행사/마감 날짜 추출"""
    # 1. (~11/19) 또는 (~ 11.19) 형태
    m_single = re.search(r'\(~?\s*(\d{1,2}[\.\/]\d{1,2})\)', title)
    # 2. (11.05~11.19) 기간 형태
    m_range = re.search(r'\(?\s*(\d{1,2}[\.\/]\d{1,2})\s*~\s*(\d{1,2}[\.\/]\d{1,2})\s*\)?', title)
    
    current_year = "2026"
    apply_period = default_date
    event_date = "상세 공고 참조"
    is_available = True

    if m_range:
        start_d, end_d = m_range.group(1), m_range.group(2)
        apply_period = f"{current_year}.{start_d.replace('/', '.')} ~ {current_year}.{end_d.replace('/', '.')}"
        event_date = f"마감일: {current_year}.{end_d.replace('/', '.')}"
    elif m_single:
        end_d = m_single.group(1).replace('/', '.')
        apply_period = f"접수마감: {current_year}.{end_d}"
        event_date = f"마감일: {current_year}.{end_d}"
    else:
        # 등록일 기준 기본 설정
        if default_date:
            apply_period = f"등록일: {default_date} (선착순 또는 접수중)"
            event_date = "공지 상세일정 확인"
        else:
            apply_period = "현재 접수 가능"
            event_date = "공지 상세일정 확인"

    return apply_period, event_date, is_available


def fetch_knu_bbs_notices(bbs_id: int, category_name: str, source_label: str):
    """강원대 일반 웹 게시판(bbs/.../list.do) 크롤링"""
    url = f"https://www.kangwon.ac.kr/ko/bbs/{bbs_id}/list.do"
    items = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, context=ctx, timeout=7).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        target_table = None
        for t in tables:
            th_texts = [th.get_text(strip=True) for th in t.find_all('th')]
            if any('제목' in th or '번호' in th or '일시' in th for th in th_texts):
                target_table = t
                break
        if not target_table and len(tables) > 1:
            target_table = tables[1]

        if target_table:
            rows = target_table.find_all('tr')
            for r in rows[1:]:
                a = r.find('a')
                if not a:
                    continue
                title = a.get_text(strip=True)
                if not title:
                    continue
                
                link = a.get('href', '')
                if link.startswith('.'):
                    link = f"https://www.kangwon.ac.kr/ko/bbs/{bbs_id}/" + link.lstrip('./')
                elif link.startswith('/'):
                    link = "https://www.kangwon.ac.kr" + link
                elif not link.startswith('http'):
                    link = f"https://www.kangwon.ac.kr/ko/bbs/{bbs_id}/" + link

                cols = [td.get_text(strip=True) for td in r.find_all(['td', 'th'])]
                date_str = ""
                for c in cols:
                    if re.match(r'^\d{4}[\.\-\/]\d{2}[\.\-\/]\d{2}$', c):
                        date_str = c
                        break
                
                apply_period, event_date, is_available = parse_dates_from_title(title, default_date=date_str)

                items.append({
                    "title": title,
                    "apply_period": apply_period,
                    "event_date": event_date,
                    "date": date_str,
                    "link": link,
                    "source": source_label,
                    "category": category_name,
                    "is_available": is_available
                })
    except Exception as e:
        print(f"Error fetching BBS {bbs_id}: {e}")
    return items


def fetch_library_notices():
    """강원대 도서관 공지사항 API 크롤링"""
    url = "https://library.kangwon.ac.kr/pyxis-api/1/bulletin-boards/24/bulletins?max=25&offset=0"
    items = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=7) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('success') and 'data' in data and 'list' in data['data']:
                for item in data['data']['list']:
                    title = item.get('title', '')
                    raw_date = item.get('dateCreated', '')
                    date_str = raw_date[:10].replace('-', '.') if raw_date else ""
                    
                    apply_period, event_date, is_available = parse_dates_from_title(title, default_date=date_str)
                    
                    item_id = item.get('id')
                    link = f"https://library.kangwon.ac.kr/community/bulletin/notice"

                    items.append({
                        "title": title,
                        "apply_period": apply_period,
                        "event_date": event_date,
                        "date": date_str,
                        "link": link,
                        "source": "강원대 도서관 공지",
                        "category": "프로그램",
                        "is_available": is_available
                    })
    except Exception as e:
        print(f"Error fetching Library notices: {e}")
    return items


def get_program_notices():
    """
    프로그램: 3개 링크 통합
    - https://www.kangwon.ac.kr/ko/bbs/504/list.do (교내 행사/프로그램)
    - https://library.kangwon.ac.kr/community/bulletin/notice (도서관 프로그램)
    - https://www.kangwon.ac.kr/ko/bbs/407/list.do (학사/교육 프로그램)
    """
    n1 = fetch_knu_bbs_notices(504, "프로그램", "강원대 교내행사 공지")
    n2 = fetch_library_notices()
    n3 = fetch_knu_bbs_notices(407, "프로그램", "강원대 학사/교육 프로그램")

    all_programs = n1 + n2 + n3
    all_programs.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_programs


def get_program_and_contest_notices():
    """
    프로그램 & 대회 통합: 4개 링크
    - https://www.kangwon.ac.kr/ko/bbs/504/list.do (교내 행사/프로그램)
    - https://library.kangwon.ac.kr/community/bulletin/notice (도서관 프로그램)
    - https://www.kangwon.ac.kr/ko/bbs/407/list.do (학사/교육 프로그램)
    - https://www.kangwon.ac.kr/ko/bbs/719/list.do (공모전 및 경진대회)
    """
    n1 = fetch_knu_bbs_notices(504, "프로그램&대회", "강원대 교내행사 공지")
    n2 = fetch_library_notices()
    n3 = fetch_knu_bbs_notices(407, "프로그램&대회", "강원대 학사/교육 프로그램")
    n4 = fetch_knu_bbs_notices(719, "프로그램&대회", "강원대 공모/대회 게시판")

    all_items = n1 + n2 + n3 + n4
    all_items.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_items


def get_contest_notices():
    """
    대회: 1개 링크 (하위 호환용 — get_program_and_contest_notices 사용 권장)
    - https://www.kangwon.ac.kr/ko/bbs/719/list.do (공모전 및 경진대회)
    """
    contests = fetch_knu_bbs_notices(719, "대회", "강원대 공모/대회 게시판")
    contests.sort(key=lambda x: x.get('date', ''), reverse=True)
    return contests


def get_scholarship_notices():
    """
    장학금: 1개 링크
    - https://www.kangwon.ac.kr/ko/bbs/721/list.do (장학 공지)
    """
    scholarships = fetch_knu_bbs_notices(721, "장학금", "강원대 장학금 공지 게시판")
    scholarships.sort(key=lambda x: x.get('date', ''), reverse=True)
    return scholarships
