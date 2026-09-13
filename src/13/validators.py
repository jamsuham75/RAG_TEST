import re
import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '11'))

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from retriever import search, build_context
from prompts import PROMPTS
# from validators import check_citation  # ← 추가
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def check_citation(answer, n_docs):
    """
    답변의 인용 번호가 유효한지 검증
    
    Args:
        answer: 모델의 답변 문자열
        n_docs: 근거 문서 개수
    
    Returns:
        (성공 여부, 메시지) 튜플
    """
    # ① 인용 번호가 하나라도 있는가
    found = re.findall(r"\[(\d+)\]", answer)
    if not found:
        return False, "인용 번호가 전혀 없음"
    
    # 문자열 번호를 숫자로 바꾸기
    nums = [int(n) for n in found]
    
    # ② 존재하지 않는 번호를 인용하지 않았는가
    bad = [n for n in nums if n < 1 or n > n_docs]
    
    if bad:
        return False, f"존재하지 않는 근거 번호: {bad}"
    
    return True, f"인용 {len(nums)}건 정상"


def compare(question: str):
    """같은 근거, 같은 질문으로 다양한 프롬프트 비교"""
    
    docs = search(question)
    ctx = build_context(docs)
    
    print("=" * 70)
    print(f"📌 질문: {question}")
    print(f"📚 근거 문서: {len(docs)}개")
    print("-" * 70)
    print("\n【검색된 근거】")
    print(ctx)
    print("\n" + "-" * 70)
    
    for name, tmpl in PROMPTS.items():
        print(f"\n✅ {name}")
        print("-" * 70)
        
        chain = tmpl | llm | StrOutputParser()
        answer = chain.invoke({
            "context": ctx,
            "question": question
        })
        
        print(f"답변:\n{answer}\n")
        
        # 인용 검증 추가 ← 여기!
        ok, msg = check_citation(answer, len(docs))
        print(f"🔍 인용 검증: {'✓' if ok else '✗'} {msg}")
        print()
    
    print("=" * 70)

def main():
    test_questions = [
        "환불 신청 방법과 수수료를 알려주세요",
        "환불은 언제까지 가능한가요?",
        "배송 비용은 얼마인가요?"
    ]
    
    print("\n🚀 프롬프트 비교 데모 시작\n")
    
    for question in test_questions:
        compare(question)
        print("\n")

if __name__ == "__main__":
    main()
