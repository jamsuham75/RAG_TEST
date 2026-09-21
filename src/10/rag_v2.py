from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from indexer import get_store          # 오늘 만든 함수
load_dotenv()
store = get_store()                    # 있으면 로드, 없으면 생성
llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0)
MIN_SCORE = 0.1                       # 9차시에서 정한 임계값

def build_context(docs):
    parts = []
    for i, d in enumerate(docs, 1):
        parts.append(f"[{i}] ({d.metadata['filename']} "                      
                     f"p.{d.metadata['page_no']})\n{d.page_content}")     
        return "\n\n".join(parts)
    
def ask(question, k=3):
    # 점수와 함께 검색해서 기준 미달은 걸러낸다
    pairs = store.similarity_search_with_relevance_scores(question, k=k)

    # # ← 이 3줄 추가: 거리값(음수)을 유사도(양수)로 변환
    # # 변환 공식: 거리가 작을수록 유사도가 높게
    # pairs = [(d, 1 / (1 + abs(s))) for d, s in pairs]

    # 기준(MIN_SCORE)을 넘는 것만 하나씩 골라 담기
    good = []
    for d, s in pairs:
        if s >= MIN_SCORE:
            good.append((d, s))
    if not good:
        print("Q:", question)
        print("A: 관련 자료를 찾지 못했습니다.")
        print(f"   (최고 점수 {pairs[0][1]:.3f} < 기준 {MIN_SCORE})")         
        print("-" * 55)
        return
    docs = []
    for d, s in good:
        docs.append(d)
    prompt = (
        "아래 자료만 근거로 답하세요.\n"
        "자료에 없는 내용은 '자료에서 확인할 수 없습니다'라고 답하세요.\n\n"         
        f"[자료]\n{build_context(docs)}\n\n[질문] {question}"
    )
    print("Q:", question)
    print("A:", llm.invoke(prompt).content)
    print("\n※ 근거:")
    for d, s in good:
        print(f"   · {d.metadata['filename']} "               
              f"p.{d.metadata['page_no']} (관련도 {s:.3f})")     
        print("-" * 55)

if __name__ == "__main__":
    ask("환불은 며칠 이내에 신청해야 하나요?")     
    ask("우리 회사 대표이사가 누구인가요?")