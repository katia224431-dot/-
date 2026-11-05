"""
강원대학교 맞춤형 UI/UX 컴포넌트 및 커스텀 스타일 모듈
해커톤 발표와 시연 시 심사위원들의 시선을 사로잡는 모던 디자인 적용
"""

import streamlit as st


def apply_custom_styles():
    """KNU 브랜드 컬러 및 반응형 카드 UI 스타일 주입"""
    st.markdown(
        """
        <style>
        /* 메인 컬러 변수 */
        :root {
            --knu-blue: #003876;
            --knu-dark-blue: #00224D;
            --knu-light-blue: #EBF3FC;
            --knu-accent-gold: #F59E0B;
            --knu-emerald: #10B981;
            --knu-rose: #EF4444;
            --knu-bg-card: #FFFFFF;
            --knu-border: #E2E8F0;
        }

        /* 폰트 및 전체 여백 */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        /* 헤더 배너 */
        .knu-header-banner {
            background: linear-gradient(135deg, #003876 0%, #001f42 100%);
            border-radius: 16px;
            padding: 24px 30px;
            color: #FFFFFF;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 56, 118, 0.25);
            border-left: 6px solid #F59E0B;
        }
        .knu-header-title {
            font-size: 26px;
            font-weight: 800;
            margin: 0;
            color: #FFFFFF;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .knu-header-subtitle {
            font-size: 14.5px;
            color: #D1E5FC;
            margin-top: 6px;
            margin-bottom: 0;
            font-weight: 400;
        }
        .knu-badge-pill {
            display: inline-block;
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(8px);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #F8FAFC;
            margin-right: 6px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* 크롤링 공고 전용 모던 카드 */
        .knu-notice-item {
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
            transition: all 0.2s ease-in-out;
        }
        .knu-notice-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 56, 118, 0.09);
            border-color: #93C5FD;
        }
        .knu-notice-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .knu-source-tag {
            background-color: #EFF6FF;
            color: #1D4ED8;
            font-size: 11.5px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 6px;
            display: inline-block;
        }
        .knu-date-tag {
            color: #64748B;
            font-size: 12px;
            font-weight: 600;
        }
        .knu-notice-title {
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
            margin: 4px 0 10px 0;
            line-height: 1.45;
        }
        .knu-notice-meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            background: #F8FAFC;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 10px;
            font-size: 13px;
        }
        .meta-item {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #334155;
        }
        .meta-label {
            font-weight: 700;
            color: #003876;
        }
        .knu-link-btn {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background-color: #003876;
            color: #FFFFFF !important;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 700;
            text-decoration: none;
            transition: background 0.15s;
        }
        .knu-link-btn:hover {
            background-color: #002554;
            color: #FFFFFF !important;
            text-decoration: none;
        }

        /* 탭 커스텀 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: 2px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            font-weight: 800;
            font-size: 16px;
            padding: 0 24px;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] {
            color: #003876 !important;
            border-bottom: 3px solid #003876 !important;
            background-color: #F8FAFC;
        }

        /* 메트릭 박스 */
        .metric-container {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 800;
            color: #003876;
        }
        .metric-label {
            font-size: 12px;
            color: #64748B;
            font-weight: 600;
            margin-top: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_banner():
    """상단 강원대학교 히어로 배너"""
    st.markdown(
        """
        <div class="knu-header-banner">
            <div>
                <div style="margin-bottom: 8px;">
                    <span class="knu-badge-pill">🏛️ 국립강원대학교 공식 포털 실시간 연동</span>
                    <span class="knu-badge-pill">⚡ 실시간 공고 검색 에이전트</span>
                </div>
                <h1 class="knu-header-title">🧭 강원대학교 프로그램 · 대회 · 장학금 맞춤 큐레이션</h1>
                <p class="knu-header-subtitle">
                    교내 공지, 도서관, 공모/대회, 장학 게시판의 최신 공고를 실시간 검색하고 신청 가능한 기회를 바로 확인하세요.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_crawled_card(notice: dict):
    """실시간 크롤링된 공고 카드를 렌더링"""
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
            <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 6px;">
                <a href="{link}" target="_blank" class="knu-link-btn">
                    공고 바로가기 ↗
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
