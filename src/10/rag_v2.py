# ============================================================
# FAISS에서 관련 문서를 검색하고 LLM으로 답변하는 RAG 코드입니다.
# 관련도가 낮으면 LLM을 호출하지 않고 바로 종료합니다.
# ============================================================

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from indexer import get_store


# ------------------------------------------------------------
# .env 파일에서 OpenAI API Key를 읽습니다.
# ------------------------------------------------------------

load_dotenv()


# ------------------------------------------------------------
# 검색에 사용할 FAISS 인덱스를 준비합니다.
# 저장된 인덱스가 있으면 불러오고, 없으면 새로 만듭니다.
# ------------------------------------------------------------

store = get_store()


# ------------------------------------------------------------
# 답변 생성에 사용할 LLM을 준비합니다.
# ------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ------------------------------------------------------------
# 검색 결과를 인정할 최소 관련도 점수입니다.
# ------------------------------------------------------------

MIN_SCORE = 0.1


# ------------------------------------------------------------
# 검색된 문서를 LLM에게 전달할 문자열로 만듭니다.
# 문서 번호, 파일명, 페이지 번호, 내용을 함께 표시합니다.
# ------------------------------------------------------------

def build_context(docs):
    parts = []

    for i, doc in enumerate(docs, 1):

        text = (
            f"[{i}] "
            f"({doc.metadata['filename']} "
            f"p.{doc.metadata['page_no']})\n"
            f"{doc.page_content}"
        )

        parts.append(text)

    return "\n\n".join(parts)


# ------------------------------------------------------------
# 질문을 받아 관련 문서를 검색하고 답변을 생성합니다.
# ------------------------------------------------------------

def ask(question, k=3):

    # 1. 질문과 관련된 문서를 점수와 함께 검색합니다.
    pairs = store.similarity_search_with_relevance_scores(
        question,
        k=k
    )


    # 2. 최소 관련도 이상인 문서만 남깁니다.
    good = []

    for doc, score in pairs:

        if score >= MIN_SCORE:
            good.append((doc, score))


    # 3. 관련 문서가 하나도 없으면 LLM을 호출하지 않습니다.
    if not good:

        print("Q:", question)
        print("A: 관련 자료를 찾지 못했습니다.")

        if pairs:
            print(
                f"   최고 점수: {pairs[0][1]:.3f} "
                f"< 기준: {MIN_SCORE}"
            )

        print("-" * 55)

        return


    # 4. 검색 결과에서 Document 객체만 꺼냅니다.
    docs = []

    for doc, score in good:
        docs.append(doc)


    # 5. 검색된 문서를 LLM에게 전달할 자료로 만듭니다.
    context = build_context(docs)


    # 6. 질문과 근거 자료를 이용해 프롬프트를 만듭니다.
    prompt = (
        "아래 자료만 근거로 답하세요.\n"
        "자료에 없는 내용은 "
        "'자료에서 확인할 수 없습니다'라고 답하세요.\n\n"
        f"[자료]\n{context}\n\n"
        f"[질문] {question}"
    )


    # 7. LLM에게 답변을 요청합니다.
    response = llm.invoke(prompt)


    # 8. 질문과 답변을 출력합니다.
    print("Q:", question)
    print("A:", response.content)


    # 9. 답변에 사용된 검색 근거를 출력합니다.
    print("\n※ 근거:")

    for doc, score in good:

        print(
            f"   · {doc.metadata['filename']} "
            f"p.{doc.metadata['page_no']} "
            f"(관련도 {score:.3f})"
        )

    print("-" * 55)


# ------------------------------------------------------------
# 이 파일을 직접 실행했을 때 테스트합니다.
# ------------------------------------------------------------

if __name__ == "__main__":

    ask("환불은 며칠 이내에 신청해야 하나요?")

    ask("우리 회사 대표이사가 누구인가요?")