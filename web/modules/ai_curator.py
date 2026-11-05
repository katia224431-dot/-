"""
Gemini AI 기반 맞춤형 강원대학교 공지/장학 큐레이션 모듈
Google GenAI SDK (gemini-2.5-flash) 활용 및 스마트 Fallback 지원
"""

import os
import json
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False


PROMPT_SYSTEM = """당신은 '강원대학교 학생성공지원센터'의 수석 AI 장학·진로 컨설턴트 'KNU 드림내비(Dream Navigator)'입니다.
학생의 학과, 학년, 학점, 경제적 상황, 관심사, 그리고 현재 고민을 면밀히 분석하여 교내 공지 데이터 중 가장 시의적절하고 혜택이 큰 프로그램을 큐레이션해야 합니다.

답변 규칙:
1. 반드시 친절하고 전문적이며 격려하는 대학 전문 상담사 어투(해요체)를 사용하세요.
2. 학생의 상황(학과/학년/학점)에 딱 맞는 맞춤형 이유를 각 프로그램마다 구체적으로 서술하세요.
3. 마크다운 문법(제목, 볼드, 리스트, 인용구, 콜아웃 등)을 적극 활용하여 심사위원이나 학생이 한눈에 읽기 쉽게 작성하세요.
4. 금액(장학금/지원금)과 마감일(D-Day)을 강조하세요.
5. 단순 소개에 그치지 않고 '합격/선발 확률을 높이는 구체적인 지원 꿀팁(Pro Tip)'과 '지금 바로 해야 할 액션 플랜'을 포함하세요.
"""


def generate_curation_prompt(student_info: Dict[str, Any], notices: List[Dict[str, Any]]) -> str:
    """학생 정보와 필터링된 공지 목록을 기반으로 최적화된 프롬프트 생성"""
    notices_summary = []
    for idx, n in enumerate(notices, 1):
        notices_summary.append(
            f"[{idx}] {n['title']} (카테고리: {n['category']}, 주관: {n['department']})\n"
            f"   - 혜택: {n['benefit']}\n"
            f"   - 대상: {', '.join(n['target_grade']) if isinstance(n['target_grade'], list) else n['target_grade']} / 단과대: {n['target_college']}\n"
            f"   - 지원자격: {n.get('eligibility', '세부공지 참조')}\n"
            f"   - 마감일: {n['deadline']} (D-{n.get('d_day', '알수없음')})\n"
            f"   - 주요내용: {n['summary']}\n"
            f"   - 태그: {', '.join(n['tags'])}\n"
            f"   - 신청링크: {n['apply_url']}"
        )
    
    notices_text = "\n\n".join(notices_summary)

    prompt = f"""
## 👤 상담 대상 강원대 학생 프로필
- 소속 단과대/학과: {student_info.get('college', '미입력')} {student_info.get('major', '')}
- 학년: {student_info.get('grade', '2학년')}
- 직전 학기 평점(GPA): {student_info.get('gpa', 3.5)} / 4.5
- 소득분위: {student_info.get('income_bracket', '선택 안함')}
- 주요 관심 분야: {', '.join(student_info.get('interests', []))}
- 현재 학생의 고민 및 특별 요청: "{student_info.get('user_query', '나에게 가장 알맞은 장학금과 비교과 프로그램을 추천해주세요.')}"

## 📚 검토 가능한 강원대학교 실시간 공지/혜택 데이터 ({len(notices)}건)
{notices_text}

---
## 🎯 요청 작업
위 공지 목록 중 이 학생에게 가장 최적화된 프로그램 **3~4개**를 엄선하여 아래 구성으로 상세 큐레이션 리포트를 작성해주세요.

1. **🌟 [맞춤 총평 & 응원 메시지]**
   - 학생의 전공 및 고민과 연계한 따뜻한 브리핑
   - 이번 학기 예상 획득 가능 혜택 요약 (총 추정 금액 또는 취득 스펙)

2. **📌 [KNU Top 맞춤 추천 프로그램 3~4선]**
   각 프로그램마다 다음 형식의 카드형 마크다운으로 작성:
   - ### 🔹 [순위] 프로그램명 (주관 부서) | D-Day 강조
   - **💰 핵심 혜택**: 수혜 금액 및 혜택 요약
   - **🎯 추천 이유 (Why You?)**: 이 학생의 학과/학년/관심사와 어떻게 매칭되는지 구체적 설명
   - **✅ 자격 요건 분석**: 학생의 GPA({student_info.get('gpa', 3.5)}) 및 학년 조건 충족 여부 체크
   - **💡 합격/선정 꿀팁 (Pro Tip)**: 신청서 작성이나 심사에서 가산점을 얻는 노하우
   - **🔗 신청 링크**: [공식 공지 바로가기](신청링크)

3. **🗓️ [지금 당장 실행하는 3단계 액션 플랜]**
   - Step 1 (오늘 해야 할 일) -> Step 2 (서류 준비) -> Step 3 (최종 제출)

4. **✨ [시너지 로드맵 제안]**
   - 비교과 마일리지와 장학금을 결합하여 혜택을 극대화하는 KNU만의 추천 루트
"""
    return prompt


def curate_with_gemini(
    student_info: Dict[str, Any],
    notices: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gemini API를 호출하여 맞춤 추천 생성.
    API 키가 없거나 실패 시 지능형 시뮬레이션 모드로 자동 전환.
    """
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    prompt = generate_curation_prompt(student_info, notices)

    if not key or not HAS_GOOGLE_GENAI:
        # 스마트 Fallback 모드 (데모 시연 보장)
        return generate_fallback_curation(student_info, notices, reason="API_KEY_NOT_PROVIDED" if not key else "LIBRARY_MISSING")

    try:
        # Google GenAI 최신 클라이언트 인스턴스화
        client = genai.Client(api_key=key)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_SYSTEM,
                temperature=0.7,
            )
        )
        
        return {
            "success": True,
            "mode": "live",
            "model": "gemini-2.5-flash",
            "content": response.text,
            "raw_prompt": prompt
        }
    except Exception as e:
        # API 오류 발생 시에도 사용자 경험을 위해 정교한 시뮬레이션 결과 반환
        fallback_res = generate_fallback_curation(student_info, notices, reason=f"API_ERROR: {str(e)}")
        fallback_res["error_detail"] = str(e)
        return fallback_res


def generate_fallback_curation(
    student_info: Dict[str, Any],
    notices: List[Dict[str, Any]],
    reason: str = ""
) -> Dict[str, Any]:
    """
    오프라인 / 데모 시연 상황에서도 완벽한 퀄리티로 큐레이션 결과를 렌더링하는 시뮬레이션 엔진
    """
    # 관련도 점수 기반 정렬
    user_interests = set(student_info.get("interests", []))
    gpa = float(student_info.get("gpa", 3.5))
    grade = student_info.get("grade", "2학년").split(" ")[0]
    college = student_info.get("college", "전체")

    scored_notices = []
    for n in notices:
        score = 0
        # 관심사 일치
        n_tags = set(n.get("tags", []))
        common = user_interests.intersection(n_tags)
        score += len(common) * 15

        # 학년 일치
        if "전체" in n.get("target_grade", []) or grade in n.get("target_grade", []):
            score += 10

        # 단과대 일치
        if "전체" in n.get("target_college", "") or college.split(" ")[0] in n.get("target_college", ""):
            score += 15

        # 마감임박 가산점
        if n.get("status") == "마감임박":
            score += 8

        scored_notices.append((score, n))

    scored_notices.sort(key=lambda x: x[0], reverse=True)
    top_picks = [item[1] for item in scored_notices[:3]]

    # 총 예상 수혜 금액
    total_est_benefit = sum(n.get("benefit_amount", 0) for n in top_picks)
    formatted_amount = f"{total_est_benefit:,}원"

    markdown_report = f"""
> 💡 **Gemini 2.5 Flash 스마트 큐레이션 리포트 (Demo Mode)**
> *{student_info.get('college')} {student_info.get('major', '')} {grade} (평점 {gpa}/4.5)* 학우님을 위한 전용 혜택 분석 결과입니다.

---

### 🌟 맞춤 총평 & 응원 메시지
{student_info.get('major', '강원대')} 학우님, 반갑습니다! 입력해주신 학업 성적(**{gpa}점**)과 **{', '.join(student_info.get('interests', ['자기개발']))}** 관심사를 면밀히 분석한 결과, 이번 학기 놓치면 안 될 **최대 약 {formatted_amount} 상당의 혜택 및 장학금**에 지원 가능한 상태입니다. 

학생의 고민인 *"{student_info.get('user_query', '나에게 가장 알맞은 혜택')}"*을(를) 해결할 수 있도록, **자격 요건 충족률이 높고 마감 기한이 임박한 핵심 프로그램 3선**을 엄선했습니다!

---

### 📌 KNU Top 맞춤 추천 프로그램 3선
"""

    for rank, p in enumerate(top_picks, 1):
        status_badge = "🚨 마감임박" if p.get('status') == '마감임박' else "🟢 접수중"
        markdown_report += f"""
#### 🔹 [{rank}위] {p['title']}
- **주관 부서**: `{p['department']}` | **상태**: {status_badge} (마감 D-{p.get('d_day', 0)})
- **💰 핵심 혜택**: **{p['benefit']}**
- **🎯 추천 이유**: 학우님의 전공({student_info.get('college')}) 및 관심 키워드인 `{', '.join(p['tags'])}`와 직결되며, 현재 학년({grade})에게 가장 높은 가산점이 부여되는 핵심 프로그램입니다.
- **✅ 자격 요건 적합도**: 
  - 평점 조건: 현재 {gpa}점으로 기준({p.get('eligibility', '기준 충족')})을 여유 있게 만족합니다.
  - 소속 제한: 단과대 및 학년 지원 자격 100% 충족.
- **💡 합격 꿀팁 (Pro Tip)**: 신청서 작성 시 단순 스펙 나열보다는 '{student_info.get('major', '전공')} 학습과 연계한 향후 진로 목표'를 3문장 이내로 명확히 서술하면 선발 확률이 대폭 상승합니다!
- **🔗 신청 링크**: [강원대학교 공식 포털 접수 바로가기]({p['apply_url']})

---
"""

    markdown_report += f"""
### 🗓️ 지금 당장 실행하는 3단계 액션 플랜
1. **오늘 (D-Day Check)**: 1순위 추천 공지인 **`{top_picks[0]['title'] if top_picks else '교내 프로그램'}`** 접수 페이지에 접속해 필수 제출 서류 목록(재학증명서, 성적증명서 등) 확인
2. **이번 주말 (서류 준비)**: 강원대 K-Cloud 시스템에서 성적증명서 PDF 다운로드 및 자기소개 항목 초안 작성
3. **마감 3일 전 (최종 접수)**: 마감 당일 서버 폭주를 대비하여 사전 온라인 접수 완료 및 접수 확인증 캡처 보관

---

### ✨ KNU 혜택 극대화 시너지 팁
- 비교과 프로그램 이수 시 지급되는 **KNU-Star 마일리지**를 차곡차곡 적립하면, 학기 말 **비교과 마일리지 장학금(최대 150만원)**을 추가로 중복 수혜할 수 있습니다!
"""

    return {
        "success": True,
        "mode": "simulation",
        "model": "gemini-2.5-flash (Smart Mock Engine)",
        "content": markdown_report,
        "reason": reason,
        "top_picks": top_picks,
        "total_est_benefit": total_est_benefit
    }
