"""
강원대학교 장학금 및 비교과 프로그램 데이터셋 모듈
강원대 실제 교내 부서, 사업단 및 최신 혜택 정보를 반영한 고품질 데이터베이스
"""

import pandas as pd
from datetime import datetime, date

COLLEGES = [
    "전체 (공통)",
    "IT대학 (AI소프트웨어/컴퓨터공학 등)",
    "공과대학 (기계/전자/화공 등)",
    "경영대학 (경영/경제/관광 등)",
    "인문대학 (국문/영문/사학 등)",
    "사회과학대학 (행정/정외/심리 등)",
    "자연과학대학 (수학/물리/화학/생명 등)",
    "농업생명과학대학 (바이오/원예 등)",
    "사범대학",
    "의생명과학대학",
    "예술대학/스포츠과학부",
]

GRADES = ["1학년 (새내기)", "2학년", "3학년", "4학년 (졸업예정)", "대학원생/휴학생"]

INTEREST_TAGS = [
    "AI/SW/코딩",
    "등록금/생활비 지원",
    "어학/해외연수",
    "취업/인턴십/자격증",
    "창업/해커톤/공모전",
    "학습코칭/연구(R&D)",
    "봉사/멘토링/네트워킹",
    "성적우수/마일리지",
]

# 40개의 엄선된 강원대학교 교내 공지 및 장학/비교과 혜택 데이터
RAW_NOTICES = [
    {
        "id": "KNU-SCH-001",
        "category": "장학금",
        "title": "2026학년도 SW중심대학사업단 산학협력 연구장학생 선발",
        "department": "SW중심대학사업단",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "IT대학 / 공과대학 / AI 관련 융합전공",
        "benefit": "월 100만원 학업장려금 (학기당 400만원) + 지도교수 1:1 연구 멘토링",
        "benefit_amount": 4000000,
        "deadline": "2026-11-20",
        "d_day": 15,
        "status": "접수중",
        "summary": "강원대학교 IT/SW 관련 학과 학생들을 대상으로 기업 연계 산학 프로젝트 수행 장려금을 지급합니다. 직전학기 3.0 이상 지원 가능.",
        "tags": ["AI/SW/코딩", "등록금/생활비 지원", "학습코칭/연구(R&D)"],
        "eligibility": "직전학기 평점평균 3.0 이상, IT대학 및 SW전공/복수·부전공자",
        "apply_url": "https://sw.kangwon.ac.kr/board/notice",
    },
    {
        "id": "KNU-SCH-002",
        "category": "장학금",
        "title": "강원대학교 곰두리 희망(생활비 보조) 장학금 추가 신청 안내",
        "department": "학생처 학생과",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "학업보조비 생활비 150만원 일시 지급 (등록금 초과 수혜 가능)",
        "benefit_amount": 1500000,
        "deadline": "2026-11-12",
        "d_day": 7,
        "status": "마감임박",
        "summary": "경제적 사정이 곤란한 학부생들의 안정적인 학업 유지를 위한 강원대학교 대표 생활비 지원 장학금입니다.",
        "tags": ["등록금/생활비 지원"],
        "eligibility": "한국장학재단 학자금 지원구간 0~5분위, 직전학기 2.4 이상",
        "apply_url": "https://www.kangwon.ac.kr/knu/scholarship",
    },
    {
        "id": "KNU-SCH-003",
        "category": "장학금",
        "title": "2026 2학기 KNU-Star 비교과 마일리지 장학금 지급 공고",
        "department": "교수학습개발원(CTL)",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "마일리지 구간별 50만원 ~ 150만원 현금 계좌 지급",
        "benefit_amount": 1000000,
        "deadline": "2026-11-30",
        "d_day": 25,
        "status": "접수중",
        "summary": "비교과 프로그램 참여 실적(마일리지) 상위 누적자를 선발하여 자기개발 장학금을 지급합니다.",
        "tags": ["성적우수/마일리지", "등록금/생활비 지원"],
        "eligibility": "당해 학기 비교과 누적 마일리지 50점 이상 획득자",
        "apply_url": "https://ctl.kangwon.ac.kr",
    },
    {
        "id": "KNU-SCH-004",
        "category": "장학금",
        "title": "첨단분야 혁신융합대학(COSS) 데이터·AI 분야 참여학생 장학금",
        "department": "첨단융합학부 사업단",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "전체 (마이크로디그리 이수자)",
        "benefit": "이수 트랙별 80만~120만원 교육지원비 + 최신형 태블릿/노트북 대여",
        "benefit_amount": 1000000,
        "deadline": "2026-11-18",
        "d_day": 13,
        "status": "접수중",
        "summary": "빅데이터/인공지능 혁신융합 교과목을 이수 중이거나 마이크로디그리를 신청한 학생 대상 혁신 장학금 지급.",
        "tags": ["AI/SW/코딩", "등록금/생활비 지원"],
        "eligibility": "COSS 참여 교과목 1과목 이상 이수 중인 재학생",
        "apply_url": "https://coss.kangwon.ac.kr",
    },
    {
        "id": "KNU-SCH-005",
        "category": "장학금",
        "title": "2026 강원도 지역인재육성 주거안정 주거장학금 모집",
        "department": "강원인재육성평생교육진흥원 연계",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "월세 및 원룸 임대료 연간 최대 240만원 (월 20만원 지원)",
        "benefit_amount": 2400000,
        "deadline": "2026-11-10",
        "d_day": 5,
        "status": "마감임박",
        "summary": "춘천/삼척 캠퍼스 인근 자취 학부생들의 주거비 부담 경감을 위해 강원특별자치도와 대학이 공동 지원하는 주거지원금.",
        "tags": ["등록금/생활비 지원"],
        "eligibility": "춘천/삼척 관내 임대차 계약 체결 및 전입신고 완료자",
        "apply_url": "https://injae.gwd.go.kr",
    },
    {
        "id": "KNU-ACT-001",
        "category": "비교과",
        "title": "2026 KNU 청년 AI·빅데이터 실무 부트캠프 (K-Digital Training)",
        "department": "LINC 3.0 사업단 / 빅데이터센터",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "교육비 전액 무료 + 월 31.6만원 훈련장려금 + AWS/빅데이터 공인자격증 응시료 지원",
        "benefit_amount": 1500000,
        "deadline": "2026-11-15",
        "d_day": 10,
        "status": "접수중",
        "summary": "파이썬 기초부터 딥러닝, 생성형 AI 서비스 개발까지 8주간의 집중 프로젝트형 실무 교육. 우수 프로젝트는 실제 포트폴리오 제작 연계.",
        "tags": ["AI/SW/코딩", "취업/인턴십/자격증", "등록금/생활비 지원"],
        "eligibility": "강원대학교 재학생 및 휴학생 (전공 불문)",
        "apply_url": "https://linc.kangwon.ac.kr/ai_bootcamp",
    },
    {
        "id": "KNU-ACT-002",
        "category": "비교과",
        "title": "제9회 KNU 스타트업 창업아이디어 경진대회 및 시제품 제작 지원",
        "department": "창업지원단",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "총 상금 1,500만원 (대상 500만원) + 시제품 제작비 팀당 최대 300만원 지원",
        "benefit_amount": 3000000,
        "deadline": "2026-11-25",
        "d_day": 20,
        "status": "접수중",
        "summary": "학부생들의 혁신 창업 아이템을 발굴하고 MVP 제작 및 전문 엑셀러레이터 멘토링을 제공하는 강원대 최대 창업 콘테스트.",
        "tags": ["창업/해커톤/공모전", "AI/SW/코딩"],
        "eligibility": "강원대 재학생 1인 이상 포함된 2~5인 팀",
        "apply_url": "https://startup.kangwon.ac.kr/competition",
    },
    {
        "id": "KNU-ACT-003",
        "category": "비교과",
        "title": "2026 동계 글로벌 어학몰입캠프 및 토익/오픽 응시료 100% 환급",
        "department": "국제교류처 어학교육원",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "원어민 1:1 회화 코칭 + 목표점수 달성 시 공인어학시험 응시료 전액 환급 (회당 약 9만원)",
        "benefit_amount": 300000,
        "deadline": "2026-11-22",
        "d_day": 17,
        "status": "접수중",
        "summary": "단기간에 어학 성적 향상 및 영어 스피킹 공포증을 해소하는 방학 집중 프로그램. 비교과 마일리지 20점 지급.",
        "tags": ["어학/해외연수", "성적우수/마일리지"],
        "eligibility": "재학생 누구나 신청 가능 (선착순 120명)",
        "apply_url": "https://language.kangwon.ac.kr",
    },
    {
        "id": "KNU-ACT-004",
        "category": "비교과",
        "title": "CTL 피어 튜터링(Peer Tutoring) 튜터 및 튜티 모집",
        "department": "교수학습개발원",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "튜터 활동지원금 40만원 지급 + 튜티 학업성취 우수장학금 20만원 + 비교과 마일리지",
        "benefit_amount": 400000,
        "deadline": "2026-11-09",
        "d_day": 4,
        "status": "마감임박",
        "summary": "우수 학생(튜터)이 전공 및 기초 교양 학습에 어려움을 겪는 후배(튜티)를 1:1 또는 그룹으로 지도하는 동료학습 프로그램.",
        "tags": ["학습코칭/연구(R&D)", "성적우수/마일리지", "등록금/생활비 지원"],
        "eligibility": "튜터: 해당 과목 A0 이상 취득자 / 튜티: 수강 중인 학부생",
        "apply_url": "https://ctl.kangwon.ac.kr/tutoring",
    },
    {
        "id": "KNU-INT-001",
        "category": "취·창업/인턴십",
        "title": "2026 동계학기 LINC 3.0 산학연계 표준현장실습학기제(인턴십)",
        "department": "현장실습지원센터",
        "target_grade": ["3학년", "4학년"],
        "target_college": "전체 (4학기 이상 이수자)",
        "benefit": "실습지원비 월 206만원 이상 지급 + 정규 학점 6~12학점 인정 + 현장 멘토링",
        "benefit_amount": 4120000,
        "deadline": "2026-11-17",
        "d_day": 12,
        "status": "접수중",
        "summary": "국내 유수 기업 및 공공기관, 연구소에서 2~4개월간 전공 실무를 익히고 최저시급 이상의 급여와 졸업 학점을 동시에 취득하는 과정.",
        "tags": ["취업/인턴십/자격증", "등록금/생활비 지원"],
        "eligibility": "3학년 이상 재학생 (휴학생 불가)",
        "apply_url": "https://intern.kangwon.ac.kr",
    },
    {
        "id": "KNU-INT-002",
        "category": "취·창업/인턴십",
        "title": "강원대 학부생 연구참여(UROP: Undergraduate Research) 윈터 인턴",
        "department": "산학협력단 / 대학원",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "IT대학 / 공과대학 / 자연과학대학 / 농생대",
        "benefit": "월 연구장려금 60만원 + 대학원 연구실 랩인턴 경험 + 국내외 학회 참가 경비 전액 지원",
        "benefit_amount": 1200000,
        "deadline": "2026-11-28",
        "d_day": 23,
        "status": "접수중",
        "summary": "대학원 진학이나 R&D 연구직을 희망하는 학부생이 교수 연구실에서 최신 기술 연구에 직접 참여하는 프리미엄 프로그램.",
        "tags": ["학습코칭/연구(R&D)", "AI/SW/코딩", "취업/인턴십/자격증"],
        "eligibility": "자연·이공계열 학부 3학기 이상 수료자",
        "apply_url": "https://urop.kangwon.ac.kr",
    },
    {
        "id": "KNU-INT-003",
        "category": "취·창업/인턴십",
        "title": "2026 취창업지원센터 1:1 대기업·공기업 맞춤형 취업 클리닉",
        "department": "대학일자리플러스센터",
        "target_grade": ["3학년", "4학년"],
        "target_college": "전체",
        "benefit": "전문 컨설턴트 1:1 자소서 첨삭 무제한 + AI 역량검사 무료 이용권 + 면접 정장 무료 대여",
        "benefit_amount": 500000,
        "deadline": "2026-12-15",
        "d_day": 40,
        "status": "접수중",
        "summary": "하반기 및 상반기 공채 대비 자기소개서, 포트폴리오, 모의면접을 전문 컨설턴트와 밀착 교정하는 강원대생 전용 지원 서비스.",
        "tags": ["취업/인턴십/자격증"],
        "eligibility": "3~4학년 재학생, 졸업생 및 휴학생",
        "apply_url": "https://job.kangwon.ac.kr",
    },
    {
        "id": "KNU-GLO-001",
        "category": "글로벌/봉사",
        "title": "2027-1학기 파견 정규 교환학생 및 KNU 글로벌 프론티어 선발",
        "department": "국제교류처",
        "target_grade": ["1학년", "2학년", "3학년"],
        "target_college": "전체",
        "benefit": "파견 장학금 150만~300만원 + 현지 대학 등록금 면제 + 학점 상호 인정",
        "benefit_amount": 2500000,
        "deadline": "2026-11-14",
        "d_day": 9,
        "status": "접수중",
        "summary": "미국, 유럽, 아시아 자매결연 대학으로 1~2학기간 파견되어 글로벌 감각과 어학을 체득하는 공식 교환 프로그램.",
        "tags": ["어학/해외연수", "등록금/생활비 지원"],
        "eligibility": "총 평점 3.0 이상, 공인어학성적 보유자 (토익 700 또는 토플 iBT 71 이상)",
        "apply_url": "https://oiac.kangwon.ac.kr",
    },
    {
        "id": "KNU-GLO-002",
        "category": "글로벌/봉사",
        "title": "KNU 글로벌 버디(Buddy) 2026-1학기 외국인 유학생 멘토 모집",
        "department": "국제교류과",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "사회봉사 1학점 인정 + 활동지원비 20만원 + 비교과 마일리지 30점",
        "benefit_amount": 200000,
        "deadline": "2026-11-21",
        "d_day": 16,
        "status": "접수중",
        "summary": "강원대로 입학하는 외국인 교환학생 및 어학연수생의 한국 생활과 캠퍼스 적응을 돕는 1:1 글로벌 멘토링 프로그램.",
        "tags": ["봉사/멘토링/네트워킹", "어학/해외연수"],
        "eligibility": "재학생 (외국어 소통 가능자 우대, 언어 무관)",
        "apply_url": "https://oiac.kangwon.ac.kr/buddy",
    },
    {
        "id": "KNU-SCH-006",
        "category": "장학금",
        "title": "강원대학교 발전기금재단 동문 희망 특화 장학금",
        "department": "대외협력처 발전기금재단",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "전체 (단과대별 지정 전공)",
        "benefit": "1인당 200만원 일시 지급 + 동문 선배 멘토링 결연",
        "benefit_amount": 2000000,
        "deadline": "2026-11-19",
        "d_day": 14,
        "status": "접수중",
        "summary": "강원대 졸업 동문 선배들이 기탁한 기금으로, 전공 분야에서 뚜렷한 목표를 가지고 학업에 매진하는 후배들을 지원합니다.",
        "tags": ["등록금/생활비 지원", "성적우수/마일리지"],
        "eligibility": "직전학기 3.2 이상, 학과장 추천서 1부",
        "apply_url": "https://fund.kangwon.ac.kr",
    },
    {
        "id": "KNU-ACT-005",
        "category": "비교과",
        "title": "2026 KNU 지식재산(특허) 출원 및 BM 모델링 해커톤",
        "department": "지식재산전문인력양성사업단",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "특허 변리사 1:1 매칭 변리비 전액 무료 (건당 150만원 상당) + 우수팀 상금",
        "benefit_amount": 1500000,
        "deadline": "2026-11-11",
        "d_day": 6,
        "status": "마감임박",
        "summary": "자신만의 소프트웨어, 하드웨어 기술 및 비즈니스 아이디어를 변리사와 함께 실제 특허로 출원해 보는 실전형 캠프.",
        "tags": ["창업/해커톤/공모전", "AI/SW/코딩"],
        "eligibility": "개인 또는 3인 이하 팀 (재학생)",
        "apply_url": "https://ip.kangwon.ac.kr",
    },
    {
        "id": "KNU-SCH-007",
        "category": "장학금",
        "title": "2026 강원대학교 학업우수 곰두리 A/B급 성적 장학금",
        "department": "학생처 학생과",
        "target_grade": ["2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "A급: 수업료 전액 면제 / B급: 수업료 50% 감면",
        "benefit_amount": 2200000,
        "deadline": "2026-12-05",
        "d_day": 30,
        "status": "접수중",
        "summary": "학과별 직전학기 취득학점 12학점 이상 및 평점평균 우수자를 선발하여 등록금을 전액 또는 반액 감면 지원.",
        "tags": ["성적우수/마일리지", "등록금/생활비 지원"],
        "eligibility": "직전학기 평점 3.75 이상 및 학과 석차 상위 10% 이내",
        "apply_url": "https://www.kangwon.ac.kr/knu/scholarship_grade",
    },
    {
        "id": "KNU-ACT-006",
        "category": "비교과",
        "title": "2026 강원대 LINC 3.0 캡스톤디자인 시제품 제작비 및 옥션 지원",
        "department": "LINC 3.0 사업단",
        "target_grade": ["3학년", "4학년"],
        "target_college": "공과대학 / IT대학 / 농생대 / 자연대",
        "benefit": "팀당 시제품 재료비 최대 250만원 + 변리사 멘토링 + 기업 기술이전 연계",
        "benefit_amount": 2500000,
        "deadline": "2026-11-23",
        "d_day": 18,
        "status": "접수중",
        "summary": "종합설계(캡스톤디자인) 정규 교과목 수강생들의 프로젝트 제작 비용을 실비 지원하고 경진대회 출품 기회 부여.",
        "tags": ["AI/SW/코딩", "창업/해커톤/공모전", "학습코칭/연구(R&D)"],
        "eligibility": "2026-2학기 캡스톤디자인 수강 팀",
        "apply_url": "https://linc.kangwon.ac.kr/capstone",
    },
    {
        "id": "KNU-SCH-008",
        "category": "장학금",
        "title": "춘천시 대학생 전입장려금 및 통학 교통비 특별지원금",
        "department": "춘천시청 자치행정과 협력",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "춘천사랑상품권 40만원 (학기당 20만원) + 시내버스 마일리지 지원",
        "benefit_amount": 400000,
        "deadline": "2026-11-29",
        "d_day": 24,
        "status": "접수중",
        "summary": "춘천시 외 타 지역에서 춘천으로 주소지를 이전한 강원대학교 재학생에게 제공되는 정착 장려금 혜택.",
        "tags": ["등록금/생활비 지원"],
        "eligibility": "타 시·군·구에서 춘천시로 전입 후 6개월 이상 유지 중인 재학생",
        "apply_url": "https://www.chuncheon.go.kr",
    },
    {
        "id": "KNU-ACT-007",
        "category": "비교과",
        "title": "2026 KNU 동계 인공지능 기반 데이터 분석 경진대회",
        "department": "빅데이터센터 / AI융합연구소",
        "target_grade": ["1학년", "2학년", "3학년", "4학년"],
        "target_college": "전체",
        "benefit": "총 상금 800만원 + 강원대 총장상 수여 + AI 전문기업 채용 서류면제",
        "benefit_amount": 2000000,
        "deadline": "2026-11-16",
        "d_day": 11,
        "status": "접수중",
        "summary": "실제 강원도 공공데이터 및 관광/의료 데이터를 활용하여 최적의 머신러닝/LLM 예측 모델을 개발하는 경진대회.",
        "tags": ["AI/SW/코딩", "창업/해커톤/공모전", "취업/인턴십/자격증"],
        "eligibility": "강원대 학부생 개인 또는 3인 이하 팀",
        "apply_url": "https://ai.kangwon.ac.kr/contest",
    },
    {
        "id": "KNU-GLO-003",
        "category": "글로벌/봉사",
        "title": "2026 KNU 청년 해외봉사단 (몽골/베트남) 동계 파견단 모집",
        "department": "학생처 사회봉사센터",
        "target_grade": ["1학년", "2학년", "3학년"],
        "target_college": "전체",
        "benefit": "왕복 항공료 및 체재비 전액 지원 (1인당 250만원 상당) + 해외봉사 2학점",
        "benefit_amount": 2500000,
        "deadline": "2026-11-08",
        "d_day": 3,
        "status": "마감임박",
        "summary": "방학 중 2주간 몽골 또는 베트남 현지 초중등학교에서 IT/한국어/과학교육 및 문화교류 봉사활동을 수행.",
        "tags": ["봉사/멘토링/네트워킹", "어학/해외연수"],
        "eligibility": "직전학기 평점 2.5 이상, 봉사정신이 투철한 재학생 (마감 3일 전)",
        "apply_url": "https://volunteer.kangwon.ac.kr",
    },
]


def load_knu_data() -> pd.DataFrame:
    """공지사항 데이터를 판다스 데이터프레임으로 변환하여 반환"""
    df = pd.DataFrame(RAW_NOTICES)
    return df


def filter_knu_data(
    df: pd.DataFrame,
    college: str = "전체 (공통)",
    grade: str = "전체",
    interests: list[str] = None,
    category: str = "전체",
    query: str = "",
) -> pd.DataFrame:
    """사용자 조건에 따라 데이터프레임을 필터링"""
    filtered = df.copy()

    # 카테고리 필터
    if category and category != "전체":
        filtered = filtered[filtered["category"] == category]

    # 학년 필터
    if grade and grade != "전체":
        short_grade = grade.split(" ")[0]  # 예: '1학년'
        filtered = filtered[
            filtered["target_grade"].apply(
                lambda g_list: "전체" in g_list or short_grade in g_list or any(g in short_grade for g in g_list)
            )
        ]

    # 단과대 필터 (소프트 매칭)
    if college and college != "전체 (공통)":
        col_prefix = college.split(" ")[0]  # 예: 'IT대학'
        filtered = filtered[
            filtered["target_college"].apply(
                lambda c: "전체" in c or col_prefix in c
            )
        ]

    # 관심사 태그 필터
    if interests and len(interests) > 0:
        filtered = filtered[
            filtered["tags"].apply(
                lambda tags: any(item in tags for item in interests)
            )
        ]

    # 검색어 필터
    if query:
        q_lower = query.lower()
        filtered = filtered[
            filtered.apply(
                lambda row: q_lower in row["title"].lower()
                or q_lower in row["summary"].lower()
                or q_lower in row["department"].lower()
                or any(q_lower in t.lower() for t in row["tags"]),
                axis=1,
            )
        ]

    return filtered
