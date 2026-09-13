import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '10'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '11'))

from indexer import get_store
from retriever import build_context, MIN_SCORE

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
store = get_store()
llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def diagnose(question, k=3):
    print("=" * 60)
    print("Q:", question)
    pairs = store.similarity_search_with_relevance_scores(
        question, k=k)
    # ── 검색 단계 진단 ──
    if not pairs:
        print("→ 【검색 실패】 결과가 0건입니다")
        return
    # 기준(MIN_SCORE)을 넘는 것만 골라 담기
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
    # ── 생성 단계 ──
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
    
    # diagnose.py 끝에 추가

# diagnose.py 끝에 추가

if __name__ == "__main__":
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
            input("\n[Enter 키로 다음 질문 진행]")