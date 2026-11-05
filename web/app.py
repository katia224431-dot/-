"""
두물보 (강원대학교 간편 챗봇) - 메인 애플리케이션
챗봇 기능 + 프로그램&대회·장학금 실시간 검색 통합 플랫폼
"""

import os
import base64
import pathlib
import random
import streamlit as st
import pandas as pd
from datetime import datetime

# 모듈 임포트
from modules.knu_crawler import (
    get_program_and_contest_notices,
    get_scholarship_notices,
)
from modules.ui_components import apply_custom_styles
from modules.ai_chatbot import get_chatbot_response, check_bus_keyword

# ───────────────────────────────────────────────
# 1. 페이지 설정
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="강원대학교 간편 챗봇 : 두물보",
    page_icon="🐻",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_styles()

# ───────────────────────────────────────────────
# 2. 곰두리 이미지 Base64 로드 (애니메이션용)
# ───────────────────────────────────────────────
_GOMDURI_B64 = ""
_gomduri_path = pathlib.Path("assets/gomduri.png")
if _gomduri_path.exists():
    _GOMDURI_B64 = base64.b64encode(_gomduri_path.read_bytes()).decode()


def show_gomduri_animation(count: int = 5):
    """곰두리 이미지가 풍선처럼 위로 떠오르는 애니메이션 (풍선 대체)"""
    if not _GOMDURI_B64:
        st.balloons()
        return

    bears_html = ""
    for i in range(count):
        left = random.randint(5, 85)
        delay = round(random.uniform(0, 1.5), 2)
        size = random.randint(60, 100)
        bears_html += (
            f'<img class="gomduri-float" src="data:image/png;base64,{_GOMDURI_B64}" '
            f'width="{size}" style="left:{left}vw; animation-delay:{delay}s;">'
        )

    st.markdown(
        f"""
        <style>
        @keyframes floatBear {{
            0%   {{ transform: translateY(100vh) scale(0.5) rotate(-5deg); opacity: 0; }}
            15%  {{ opacity: 1; }}
            80%  {{ opacity: 0.9; }}
            100% {{ transform: translateY(-120px) scale(1.1) rotate(5deg); opacity: 0; }}
        }}
        .gomduri-float {{
            position: fixed;
            bottom: -120px;
            animation: floatBear 3.5s ease-out forwards;
            z-index: 99999;
            pointer-events: none;
        }}
        </style>
        {bears_html}
        """,
        unsafe_allow_html=True,
    )


# ───────────────────────────────────────────────
# 3. 세션 상태 초기화
# ───────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 저는 강원대학교 간편 챗봇 **강비서 (두물보)** 🐻입니다.\n\n"
                "장학금, 프로그램, 대회 공고부터 교통 정보까지 뭐든지 물어보세요!\n\n"
                "예시: `근로장학생 신청하고 싶어요`, `AI 경진대회 알려줘`, `시내버스 어떻게 타요?`"
            ),
        }
    ]

# ───────────────────────────────────────────────
# 4. 사이드바
# ───────────────────────────────────────────────
with st.sidebar:
    # 마스코트 & 타이틀
    if _GOMDURI_B64:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 10px 0 16px 0;">
                <img src="data:image/png;base64,{_GOMDURI_B64}" width="90"
                     style="border-radius:50%; border: 3px solid #003876; box-shadow: 0 4px 12px rgba(0,56,118,0.25);">
                <div style="font-size: 20px; font-weight: 900; color: #003876; margin-top: 8px;">강비서</div>
                <div style="font-size: 12px; color: #64748B;">강원대학교 간편 챗봇 두물보</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="text-align:center; padding: 10px 0 16px 0;">
                <div style="font-size: 60px; line-height: 1;">🐻</div>
                <div style="font-size: 20px; font-weight: 900; color: #003876; margin-top: 6px;">강비서</div>
                <div style="font-size: 12px; color: #64748B;">강원대학교 간편 챗봇 두물보</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("---")

    # Gemini API 키
    st.markdown("#### 🔑 Gemini AI 엔진")
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    api_key_input = st.text_input(
        "API Key (선택사항)",
        value=env_key,
        type="password",
        help="입력 시 Gemini 2.5 Flash 실시간 AI 답변 활성화. 미입력 시에도 모든 검색 기능 사용 가능합니다.",
    )
    if api_key_input:
        st.success("🟢 Gemini AI 연동 활성화")
    else:
        st.info("💡 스마트 검색 모드로 작동 중")

    st.markdown("---")

    # 공고 새로고침
    st.markdown("#### 📡 실시간 공고")
    if st.button("🔄 공고 새로고침", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    # 필터 옵션
    st.markdown("#### ⚙️ 검색 옵션")
    only_available = st.checkbox(
        "✅ 접수 가능한 공고만 보기",
        value=True,
        help="현재 신청 가능한 공고만 표시합니다.",
    )
    view_mode = st.radio("결과 표시 형태", ["카드 뷰", "테이블 뷰"], horizontal=True)

    st.markdown("---")

    # 채팅 초기화
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "대화가 초기화되었어요! 다시 무엇이든 물어보세요 🐻\n\n"
                    "예시: `공모전 알려줘`, `생활비 장학금 있어요?`, `동해역 가는 버스`"
                ),
            }
        ]
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size: 11px; color: #94A3B8; line-height: 1.6;">
            🏛️ 국립강원대학교<br>
            데이터 갱신: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
            Powered by Gemini 2.5 Flash
        </div>
        """,
        unsafe_allow_html=True,
    )


# ───────────────────────────────────────────────
# 5. 상단 헤더
# ───────────────────────────────────────────────
header_icon = (
    f'<img src="data:image/png;base64,{_GOMDURI_B64}" width="70" '
    'style="border-radius:50%; border:3px solid rgba(255,255,255,0.6); flex-shrink:0;">'
    if _GOMDURI_B64
    else '<div style="font-size: 56px; line-height: 1; flex-shrink: 0;">🐻</div>'
)

st.markdown(
    f"""
    <div class="knu-header-banner">
        <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            {header_icon}
            <div>
                <div style="margin-bottom: 6px;">
                    <span class="knu-badge-pill">🏛️ 국립강원대학교</span>
                    <span class="knu-badge-pill">⚡ Gemini 2.5 Flash</span>
                    <span class="knu-badge-pill">📡 실시간 공고 연동</span>
                </div>
                <h1 class="knu-header-title">강원대학교 간편 챗봇 : 두물보</h1>
                <p class="knu-header-subtitle">
                    마스코트 강비서와 함께 — 장학금·프로그램·대회 공고 실시간 검색 &amp; AI 질의응답 서비스
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ───────────────────────────────────────────────
# 6. 공고 데이터 캐싱 로드
# ───────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_all_crawled_data():
    program_and_contests = get_program_and_contest_notices()
    scholarships = get_scholarship_notices()
    return program_and_contests, scholarships


with st.spinner("강원대 공식 게시판에서 최신 공고를 불러오는 중..."):
    all_program_contests, all_scholarships = load_all_crawled_data()

# 챗봇 컨텍스트용 (공모전만 별도 추출)
all_contests_for_chat = [n for n in all_program_contests if "719" in n.get("link", "") or "대회" in n.get("source", "")]
all_programs_for_chat = [n for n in all_program_contests if n not in all_contests_for_chat]


# ───────────────────────────────────────────────
# 7. 통계 메트릭 바 (3개 컬럼)
# ───────────────────────────────────────────────
m1, m2, m3 = st.columns(3)
for col, value, label, color in [
    (m1, len(all_program_contests), "📚 프로그램&대회 공고", "#003876"),
    (m2, len(all_scholarships),     "💰 장학금 공고",        "#10B981"),
    (m3, len(all_program_contests) + len(all_scholarships), "✨ 전체 공고 합계", "#6366F1"),
]:
    with col:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-value" style="color: {color};">{value}건</div>
                <div class="metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)


# ───────────────────────────────────────────────
# 8. 유틸리티 함수
# ───────────────────────────────────────────────
def filter_and_sort_notices(notices, keyword="", available_only=True):
    """키워드 검색 + 최근 순 + 가능 여부 필터"""
    filtered = []
    kw = keyword.strip().lower()
    for n in notices:
        if kw and kw not in n["title"].lower() and kw not in n.get("source", "").lower():
            continue
        if available_only and not n.get("is_available", True):
            continue
        filtered.append(n)
    filtered.sort(key=lambda x: x.get("date", ""), reverse=True)
    return filtered


def render_notice_card(notice: dict):
    """공고 카드 렌더링"""
    title = notice.get("title", "")
    apply_period = notice.get("apply_period", "공지 참조")
    event_date = notice.get("event_date", "상세 일정 확인")
    link = notice.get("link", "#")
    source = notice.get("source", "교내 공지")
    date_str = notice.get("date", "")

    st.markdown(
        f"""
        <div class="knu-notice-item">
            <div class="knu-notice-top">
                <span class="knu-source-tag">📌 {source}</span>
                <span class="knu-date-tag">등록일: {date_str}</span>
            </div>
            <h3 class="knu-notice-title">{title}</h3>
            <div class="knu-notice-meta-grid">
                <div class="meta-item">
                    <span class="meta-label">🗓️ 신청일시:</span>
                    <span>{apply_period}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">⏰ 행사 날짜:</span>
                    <span>{event_date}</span>
                </div>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-top: 6px;">
                <a href="{link}" target="_blank" class="knu-link-btn">공고 바로가기 ↗</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_notices_section(notices, section_name):
    """섹션 결과 출력 (카드/테이블)"""
    if not notices:
        st.warning(f"'{section_name}' 관련 공고를 찾지 못했어요. 다른 키워드로 검색해 보세요!")
        return

    st.markdown(f"**총 `{len(notices)}`건 · 최근 등록순 정렬**")

    if view_mode == "카드 뷰":
        for item in notices:
            render_notice_card(item)
    else:
        df = pd.DataFrame(
            [{
                "제목": it["title"],
                "신청일시": it["apply_period"],
                "행사 날짜": it["event_date"],
                "등록일": it["date"],
                "출처": it["source"],
                "공고 링크": it["link"],
            } for it in notices]
        )
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                "공고 링크": st.column_config.LinkColumn("공고 링크", display_text="원문 보기 ↗"),
            },
        )


# ───────────────────────────────────────────────
# 9. 메인 탭 구성: 챗봇 / 프로그램&대회 / 장학금
# ───────────────────────────────────────────────
tab_chat, tab_program_contest, tab_scholar = st.tabs(
    ["🐻 두물보 챗봇", "📚 프로그램 & 대회", "💰 장학금"]
)


# ══════════════════════════════════════════════
# TAB 0: 챗봇 (강비서 두물보)
# ══════════════════════════════════════════════
with tab_chat:
    st.markdown("### 🐻 강비서 두물보 — AI 질의응답 챗봇")
    st.caption(
        "장학금·프로그램·대회 공고 질문부터 교통 정보까지 편하게 물어보세요. "
        "시내버스, 동해역, 삼척 교통 키워드 자동 연결 지원."
    )

    # 대화 메시지 출력
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_messages"]:
            avatar = (
                f"data:image/png;base64,{_GOMDURI_B64}"
                if msg["role"] == "assistant" and _GOMDURI_B64
                else ("🐻" if msg["role"] == "assistant" else "🧑‍🎓")
            )
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # 입력창
    if user_input := st.chat_input("두리한테 물어보세요!", key="chat_input"):
        # 사용자 메시지 추가
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(user_input)

        # 버스 키워드 감지
        bus_reply = check_bus_keyword(user_input)

        if bus_reply:
            reply = bus_reply
        else:
            # Gemini AI 또는 스마트 로컬 답변
            with st.spinner("강비서가 답변을 준비하는 중입니다... 🐻"):
                reply = get_chatbot_response(
                    messages=st.session_state["chat_messages"],
                    all_programs=all_programs_for_chat,
                    all_contests=all_contests_for_chat,
                    all_scholarships=all_scholarships,
                    api_key=api_key_input,
                )

        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        avatar_reply = (
            f"data:image/png;base64,{_GOMDURI_B64}" if _GOMDURI_B64 else "🐻"
        )
        with st.chat_message("assistant", avatar=avatar_reply):
            st.markdown(reply)

        # 곰두리 애니메이션 (풍선 대체)
        show_gomduri_animation(count=random.randint(4, 7))


# ══════════════════════════════════════════════
# TAB 1: 프로그램 & 대회 (4개 링크 통합 검색)
# ══════════════════════════════════════════════
with tab_program_contest:
    st.markdown("### 📚 교내 프로그램 & 대회 통합 검색")
    st.caption(
        "수집 출처: "
        "[교내행사 공지(504)](https://www.kangwon.ac.kr/ko/bbs/504/list.do) · "
        "[도서관 공지](https://library.kangwon.ac.kr/community/bulletin/notice) · "
        "[학사/교육 프로그램(407)](https://www.kangwon.ac.kr/ko/bbs/407/list.do) · "
        "[공모/대회(719)](https://www.kangwon.ac.kr/ko/bbs/719/list.do)"
    )

    pc_col1, pc_col2 = st.columns([8, 2])
    with pc_col1:
        search_pc = st.text_input(
            "🔍 프로그램 & 대회 검색창",
            placeholder="학과·키워드 입력 (예: 교육, 워크숍, 해커톤, 경진대회, 공모전, 도서관, 창업, SW)",
            key="input_pc",
        )
    with pc_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("초기화", key="btn_reset_pc", use_container_width=True):
            st.session_state["input_pc"] = ""
            st.rerun()

    render_notices_section(
        filter_and_sort_notices(all_program_contests, keyword=search_pc, available_only=only_available),
        "프로그램&대회",
    )


# ══════════════════════════════════════════════
# TAB 2: 장학금 (1개 링크 검색)
# ══════════════════════════════════════════════
with tab_scholar:
    st.markdown("### 💰 장학금 및 근로장학생 공고 검색")
    st.caption(
        "수집 출처: "
        "[강원대 장학금 공지 게시판(721)](https://www.kangwon.ac.kr/ko/bbs/721/list.do)"
    )

    s_col1, s_col2 = st.columns([8, 2])
    with s_col1:
        search_scholar = st.text_input(
            "🔍 장학금 검색창",
            placeholder="학과·키워드 입력 (예: 근로, 국가장학, 창업, 생활비, 성적우수, 외국인)",
            key="input_scholar",
        )
    with s_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("초기화", key="btn_reset_scholar", use_container_width=True):
            st.session_state["input_scholar"] = ""
            st.rerun()

    render_notices_section(
        filter_and_sort_notices(all_scholarships, keyword=search_scholar, available_only=only_available),
        "장학금",
    )
