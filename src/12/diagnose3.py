# diagnose.py 전체 구조
import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '10'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '11'))

from indexer import get_store
from retriever import build_context, MIN_SCORE

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════
# 1단계: 초기화 (기존 코드)
# ═══════════════════════════════════════════════════════
load_dotenv()
store = get_store()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ═══════════════════════════════════════════════════════
# 2단계: 함수 정의
# ═══════════════════════════════════════════════════════

def diagnose(question, k=3):
    """상세 진단 (개별 질문)"""
    print("=" * 60)
    print("Q:", question)
    pairs = store.similarity_search_with_relevance_scores(question, k=k)
    
    if not pairs:
        print("→ 【검색 실패】 결과가 0건입니다")
        return
    
    passed = []
    for d, s in pairs:
        if s >= MIN_SCORE:
            passed.append((d, s))
    
    print(f"검색 {len(pairs)}개 / 기준 통과 {len(passed)}개")
    print("-" * 60)
    
    for i, (d, s) in enumerate(pairs, 1):
        mark = "✓" if s >= MIN_SCORE else "✗"
        text = d.page_content[:70].replace("\n", " ")
        print(f"{mark} [{i}] {s:.3f} p.{d.metadata['page_no']}  {text}...")
    
    if not passed:
        print("\n→ 【검색 실패】 기준을 넘는 조각이 없습니다")
        return
    
    docs = []
    for d, s in passed:
        docs.append(d)
    
    prompt = ("아래 자료만 근거로 답하세요.\n"
              "자료에 없으면 '자료에서 확인할 수 없습니다'라고 답하세요.\n\n"
              f"[자료]\n{build_context(docs)}\n\n[질문] {question}")
    
    answer = llm.invoke(prompt).content
    print("\nA:", answer)
    print("\n👉 판단: 위 조각들 안에 정답이 있었는가?")
    print("   있는데 답이 틀렸다면 → 생성 문제 (13차시)")
    print("   없다면              → 검색 문제 (7·11차시)")
    print("=" * 60)


def score():
    """정답률 평가 (전체 테스트)"""
    TESTS = [
        {"q": "환불은 며칠 이내인가요?",     "keys": ["7일", "일주일"]},
        {"q": "교환은 며칠 이내인가요?",     "keys": ["30일"]},
        {"q": "고객센터 운영 시간은?",       "keys": ["09:00", "18:00", "평일"]},
        {"q": "대표이사 이름은?",            "keys": ["확인할 수 없"]},
        # ... 20개까지 추가
    ]
    
    hit = 0
    fails = []
    
    for t in TESTS:
        pairs = store.similarity_search_with_relevance_scores(t["q"], k=3)
        docs = []
        for d, s in pairs:
            if s >= MIN_SCORE:
                docs.append(d)
        
        if not docs:
            ans = "자료에서 확인할 수 없습니다"
        else:
            prompt = ("아래 자료만 근거로 답하세요.\n"
                      "자료에 없으면 '자료에서 확인할 수 없습니다'.\n\n"
                      f"[자료]\n{build_context(docs)}\n\n[질문] {t['q']}")
            ans = llm.invoke(prompt).content
        
        # 정답 키워드 중 하나라도 들어있으면 정답
        ok = False
        for key in t["keys"]:
            if key in ans:
                ok = True
                break
        
        if ok:
            hit += 1
        else:
            fails.append((t["q"], ans[:60]))
    
    print(f"\n{'='*60}")
    print(f"정답률: {hit}/{len(TESTS)} = {hit/len(TESTS)*100:.0f}%")
    print(f"{'='*60}")
    print("\n■ 실패한 질문")
    for q, a in fails:
        print(f"  · {q}")
        print(f"    → {a}...")
    print(f"\n총 {len(fails)}개 실패")
    print(f"{'='*60}")


# ═══════════════════════════════════════════════════════
# 3단계: 메인 블록 (실행 선택)
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "score":
            # python diagnose.py score
            score()
        elif sys.argv[1] == "detail":
            # python diagnose.py detail
            TESTS = {
                "① 정상 (문서에 명확히 있음)": [
                    "환불은 며칠 이내에 신청해야 하나요?",
                    "고객센터 운영 시간은 언제인가요?",
                ],
                "② 표현 변경 (같은 뜻, 다른 단어)": [
                    "반품하고 싶은데 언제까지 가능해요?",
                    "상담원이랑 통화되는 시간 알려주세요",
                ],
                "③ 없는 내용 (문서에 없음)": [
                    "대표이사 성함이 어떻게 되나요?",
                    "작년 매출이 얼마인가요?",
                ],
                "④ 복합 질문 (여러 조항에 걸침)": [
                    "환불과 교환의 조건 차이를 설명해주세요",
                    "배송비는 어떤 경우에 누가 부담하나요?",
                ],
            }
            for group, questions in TESTS.items():
                print(f"\n\n########## {group} ##########")
                for q in questions:
                    diagnose(q)
        else:
            # python diagnose.py "질문"
            diagnose(sys.argv[1])
    else:
        # python diagnose.py (기본)
        print("사용법:")
        print("  python diagnose.py score          # 전체 정답률 평가")
        print("  python diagnose.py detail         # 상세 진단 (카테고리별)")
        print('  python diagnose.py "질문내용"     # 개별 질문 진단')