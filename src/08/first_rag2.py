import sys
import os

# 06 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '07'))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from prepare import prepare_chunks        # 7차시에서 만든 함수 

load_dotenv()
# ①② 문서 읽고 조각내기 (6·7차시 결과 재사용)
chunks = prepare_chunks("../../data/manual.pdf")
# ③ 조각을 벡터로 바꿔 저장
print("임베딩 중... (조금 걸립니다)")
emb = OpenAIEmbeddings(model="text-embedding-3-small") 

store = FAISS.from_documents(chunks, emb)
print("✓ 인덱싱 완료")

llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0)
print("✓ 준비 완료\n")
# ===== 질의 (질문할 때마다) =====
def build_context(docs):
    # 검색 결과를 번호 붙여 하나의 문자열로
    parts = []
    for i, d in enumerate(docs, 1):
        parts.append(f"[{i}] ({d.metadata['filename']} "                      
                     f"p.{d.metadata['page_no']})\n{d.page_content}")     
        return "\n\n".join(parts)

def ask(question, k=3):
    # ④ 검색
    found = store.similarity_search(question, k=k)
    if not found:
        print("관련 자료를 찾지 못했습니다.")
        return
    # ⑤ 근거 기반 프롬프트로 답변 생성
    prompt = (
        "아래 자료만 근거로 답하세요.\n"
        "자료에 없는 내용은 '자료에서 확인할 수 없습니다'라고 답하세요.\n"         
        "추측하지 마세요.\n\n"
        f"[자료]\n{build_context(found)}\n\n"         
        f"[질문] {question}"
    )
    answer = llm.invoke(prompt).content
    print("Q:", question)     
    print("A:", answer)
    print("\n 참고한 자료:")    
    for d in found:
        print(f"   · {d.metadata['filename']} "               
              f"{d.metadata['page_no']}페이지")     
        print("-" * 55)
        
if __name__ == "__main__":
    ask("환불은 며칠 이내에 신청해야 하나요?")