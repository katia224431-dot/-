"""
두물보 AI 챗봇 모듈
Gemini API 연동 + 스마트 로컬 fallback + 버스 키워드 연동
"""

import os
import re

# ─────────────────────────────────────────────────
# 버스/교통 키워드 감지
# ─────────────────────────────────────────────────
BUS_KEYWORDS = ["시내", "동해역", "시내버스", "버스", "교통", "삼척버스", "노선"]
BUS_REPLY = (
    "🚌 **삼척 시내버스 정보**\n\n"
    "삼척시 시내버스 노선 및 시간표는 아래 링크에서 확인하세요!\n\n"
    "👉 [삼척시 시내버스 정보 바로가기](https://www.samcheok.go.kr/specialty/00463/02462.web)\n\n"
    "> 📌 동해역 경유 노선, 삼척 시내 순환 노선 등 모든 정보가 제공됩니다."
)


def check_bus_keyword(text: str) -> str | None:
    """교통 키워드 감지 시 삼척 버스 링크 반환, 아니면 None"""
    if any(kw in text for kw in BUS_KEYWORDS):
        return BUS_REPLY
    return None


# ─────────────────────────────────────────────────
# 로컬 스마트 답변 (API 미입력 시 fallback)
# ─────────────────────────────────────────────────
def _smart_local_response(user_text: str, all_programs, all_contests, all_scholarships) -> str:
    """키워드 기반 로컬 답변 생성"""
    kw = user_text.lower()

    # 모든 공고 합산
    all_notices = all_programs + all_contests + all_scholarships

    # 관련 공고 검색 (제목 키워드 매칭)
    matched = [
        n for n in all_notices
        if any(w in n["title"].lower() for w in kw.split() if len(w) >= 2)
    ]
    matched.sort(key=lambda x: x.get("date", ""), reverse=True)
    matched = matched[:5]  # 상위 5건

    # 카테고리별 힌트
    if any(w in kw for w in ["장학", "장학금", "근로", "생활비", "국가장학"]):
        intro = "💰 **장학금 관련 정보를 찾아드릴게요!**\n\n"
        related = [n for n in all_scholarships if any(w in n["title"].lower() for w in kw.split() if len(w) >= 2)][:5]
    elif any(w in kw for w in ["대회", "공모", "경진", "해커톤", "창업", "아이디어"]):
        intro = "🏆 **대회/공모전 관련 정보를 찾아드릴게요!**\n\n"
        related = [n for n in all_contests if any(w in n["title"].lower() for w in kw.split() if len(w) >= 2)][:5]
    elif any(w in kw for w in ["프로그램", "특강", "워크숍", "도서관", "교육", "세미나", "행사"]):
        intro = "📚 **프로그램/교육 관련 정보를 찾아드릴게요!**\n\n"
        related = [n for n in all_programs if any(w in n["title"].lower() for w in kw.split() if len(w) >= 2)][:5]
    else:
        intro = "🐻 **검색 결과입니다!**\n\n"
        related = matched

    if not related:
        return (
            f"{intro}"
            "관련 공고를 현재 찾지 못했어요. 😢\n\n"
            "**다음 방법을 시도해 보세요:**\n"
            "- 위 탭(📚 프로그램&대회 / 💰 장학금)에서 직접 키워드 검색\n"
            "- 더 간단한 키워드로 다시 질문 (예: `장학금`, `대회`, `프로그램`)\n"
            "- 🔄 사이드바의 **공고 새로고침** 버튼으로 최신 데이터 로드\n\n"
            "💡 **Gemini API Key**를 사이드바에 입력하시면 더 정확한 AI 답변을 받으실 수 있어요!"
        )

    result = intro
    for i, n in enumerate(related, 1):
        result += (
            f"**{i}. {n['title']}**\n"
            f"   - 📌 출처: {n.get('source', '교내 공지')}\n"
            f"   - 🗓️ 신청일시: {n.get('apply_period', '공지 참조')}\n"
            f"   - ⏰ 행사 날짜: {n.get('event_date', '상세 확인')}\n"
            f"   - 🔗 [공고 바로가기]({n.get('link', '#')})\n\n"
        )

    result += (
        "\n---\n"
        "더 자세한 정보는 위 탭에서 직접 검색하거나 공고 링크를 확인하세요! 🐻\n"
        "💡 사이드바에 Gemini API Key를 입력하면 더 똑똑한 AI 답변을 받을 수 있어요."
    )
    return result


# ─────────────────────────────────────────────────
# Gemini API 답변 생성
# ─────────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 강원대학교 삼척캠퍼스의 간편 챗봇 '강비서(두물보)'입니다.
마스코트는 귀여운 파란 곰 '곰두리'이며, 학생들에게 친근하고 유익한 정보를 제공합니다.

역할:
- 강원대학교 교내 프로그램, 대회/공모전, 장학금 공고 안내
- 삼척 지역 교통 정보 안내 (시내버스 등)
- 학교생활 전반에 관한 질문 답변

답변 규칙:
1. 항상 한국어로 친근하게 답변하세요
2. 🐻 이모지를 적절히 활용하세요
3. 공고 정보는 마크다운 목록으로 깔끔하게 정리하세요
4. 모르는 정보는 솔직히 모른다고 하고 관련 링크를 안내하세요
5. 답변 마지막에는 추가 질문을 유도하는 한 마디를 넣어주세요
"""


def get_chatbot_response(
    messages: list,
    all_programs: list,
    all_contests: list,
    all_scholarships: list,
    api_key: str = "",
) -> str:
    """Gemini API 호출 또는 스마트 로컬 fallback"""

    user_text = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_text = msg["content"]
            break

    # API Key 없으면 로컬 답변
    if not api_key or api_key.strip() == "":
        return _smart_local_response(user_text, all_programs, all_contests, all_scholarships)

    # Gemini API 호출 시도
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key.strip())

        # 공고 컨텍스트 요약 (최근 10건씩)
        def summarize_notices(notices, label):
            if not notices:
                return f"[{label}] 현재 공고 없음\n"
            lines = [f"[{label}]"]
            for n in notices[:10]:
                lines.append(
                    f"- {n['title']} | 신청: {n.get('apply_period','?')} | 행사: {n.get('event_date','?')} | {n.get('link','')}"
                )
            return "\n".join(lines)

        context_text = (
            "=== 현재 강원대 공고 데이터 (실시간 크롤링) ===\n"
            + summarize_notices(all_programs, "프로그램&대회")
            + "\n"
            + summarize_notices(all_contests, "대회/공모전")
            + "\n"
            + summarize_notices(all_scholarships, "장학금")
            + "\n================================\n"
        )

        # 대화 히스토리 구성
        history = []
        for msg in messages[:-1]:  # 마지막 user 메시지 제외
            role = "user" if msg["role"] == "user" else "model"
            history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        full_user_msg = f"{context_text}\n\n사용자 질문: {user_text}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history + [types.Content(role="user", parts=[types.Part(text=full_user_msg)])],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        return response.text or "죄송해요, 답변을 생성하지 못했어요. 다시 질문해 주세요! 🐻"

    except ImportError:
        return (
            "⚠️ Gemini 라이브러리가 설치되지 않았어요.\n\n"
            "`pip install google-genai` 를 실행한 후 다시 시도해 주세요.\n\n"
            + _smart_local_response(user_text, all_programs, all_contests, all_scholarships)
        )
    except Exception as e:
        err_msg = str(e)
        if "API_KEY" in err_msg.upper() or "invalid" in err_msg.lower():
            return (
                "🔑 **API Key 오류**: 입력하신 Gemini API Key를 확인해 주세요.\n\n"
                + _smart_local_response(user_text, all_programs, all_contests, all_scholarships)
            )
        return (
            f"⚠️ AI 연결 오류가 발생했어요 ({err_msg[:80]})\n\n"
            + _smart_local_response(user_text, all_programs, all_contests, all_scholarships)
        )
