import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '07'))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from prepare import prepare_chunks

load_dotenv()

# ===== 초기화 =====
chunks = prepare_chunks("../../data/manual.pdf")
print("임베딩 중...\n")
emb = OpenAIEmbeddings(model="text-embedding-3-small") 
store = FAISS.from_documents(chunks, emb)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
print("✓ 준비 완료\n")

# ===== ask 함수 =====
def ask(question):
    """질문 → 답변 + 출처"""
    found = store.similarity_search(question, k=3)
    
    # 프롬프트
    context = "\n".join([f"[{i}] {d.page_content}" 
                        for i, d in enumerate(found, 1)])
    prompt = (
        f"아래 자료만 근거로 답하세요.\n"
        f"자료에 없으면 '자료에서 확인할 수 없습니다'라고 하세요.\n\n"
        f"[자료]\n{context}\n\n"
        f"[질문] {question}"
    )
    
    answer = llm.invoke(prompt).content
    sources = [f"{d.metadata['filename']} p.{d.metadata['page_no']}" 
               for d in found]
    
    return answer, sources, found

# ===== 테스트 질문 =====
TESTS = [
    "환불은 며칠 이내에 신청해야 하나요?",     # ① 정상
    "우리 회사 대표이사 이름이 뭔가요?",        # ② 없는 내용
    "반품 절차를 알려주세요",                   # ③ 표현 변경
    "환불과 교환은 어떻게 다른가요?",          # ④ 복합
]

# ===== 테스트 실행 =====
print("=" * 100)
print("🧪 RAG 테스트 (4개 질문)")
print("=" * 100)

results = []
for i, q in enumerate(TESTS, 1):
    print(f"\n[질문 {i}] {q}")
    answer, sources, chunks_found = ask(q)
    print(f"[답변] {answer}")
    print(f"[출처] {', '.join(sources)}")
    
    results.append({
        "번호": i,
        "질문": q,
        "답변": answer,
        "출처": sources,
        "청크": chunks_found
    })
    print("-" * 100)

# ===== 평가 =====
print("\n\n" + "=" * 100)
print("📋 평가 - 각 질문의 Y/N 입력하세요")
print("=" * 100)

evals = []
for r in results:
    print(f"\n[질문 {r['번호']}] {r['질문']}")
    print(f"[답변] {r['답변']}")
    
    ans = input(f"  → 답변 정확? (Y/N): ").strip().upper() == 'Y'
    src = input(f"  → 출처 정확? (Y/N): ").strip().upper() == 'Y'
    note = input(f"  → 비고: ").strip() or "-"
    
    evals.append({
        "번호": r['번호'],
        "질문": r['질문'],
        "답변": "✅" if ans else "❌",
        "출처": "✅" if src else "❌",
        "비고": note
    })

# ===== 평가표 출력 =====
print("\n" + "=" * 120)
print("📊 평가표")
print("=" * 120)
print(f"{'번호':<4} {'질문':<40} {'답변':<6} {'출처':<6} {'비고':<30}")
print("-" * 120)

for e in evals:
    print(f"{e['번호']:<4} {e['질문'][:40]:<40} {e['답변']:<6} {e['출처']:<6} {e['비고'][:30]:<30}")

# ===== 통계 =====
correct_ans = sum(1 for e in evals if e['답변'] == "✅")
correct_src = sum(1 for e in evals if e['출처'] == "✅")

print("\n" + "=" * 120)
print("📈 통계")
print("=" * 120)
print(f"답변 정확성: {correct_ans}/4 ({correct_ans*100//4}%)")
print(f"출처 정확성: {correct_src}/4 ({correct_src*100//4}%)")

# ===== 실패 사례 분석 =====
print("\n" + "=" * 120)
print("🔍 실패 사례 분석")
print("=" * 120)

failures = [e for e in evals if e['답변'] == "❌"]

if failures:
    for fail in failures:
        r = next(x for x in results if x['번호'] == fail['번호'])
        print(f"\n【질문】{fail['질문']}")
        print(f"【답변 결과】{r['답변']}")
        print(f"【검색된 청크】")
        for j, chunk in enumerate(r['청크'], 1):
            print(f"  [{j}] {chunk.page_content[:100]}...")
        
        print(f"\n【분석】이 청크들에 정답이 있었나요?")
        has_answer = input(f"     (Y/N): ").strip().upper() == 'Y'
        
        if has_answer:
            print(f"  ✗ [생성 문제] 정답이 있는데 틀린 답변을 생성함")
        else:
            print(f"  ✗ [검색 문제] 정답이 포함된 청크를 찾지 못함")
        
        print("-" * 120)
else:
    print("\n✅ 모든 질문을 정확하게 답변했습니다!")