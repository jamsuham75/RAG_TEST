
import numpy as np
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

emb = OpenAIEmbeddings(model="text-embedding-3-small")

def sim(a: str, b: str) -> float:
    """두 문장의 코사인 유사도를 계산한다 (0~1)"""
    v1 = np.array(emb.embed_query(a))
    v2 = np.array(emb.embed_query(b))
    dot_product = np.dot(v1, v2)
    length1 = np.linalg.norm(v1)
    length2 = np.linalg.norm(v2)
    return float(dot_product / (length1 * length2))

# 내 문서 주제에 맞춰 두 그룹을 만든다
BASE = "환불은 상품 수령 후 7일 이내에 신청할 수 있습니다"

RELATED = [      # 관련 있다고 봐야 할 질문들
    "반품하고 싶어요",
    "돈 돌려받을 수 있나요?",
    "구매 취소 기간이 어떻게 되나요?",
    "물건 안 마음에 들면 어떡하죠?",
    "환불 신청 기한 알려주세요",
]

UNRELATED = [    # 관련 없다고 봐야 할 질문들
    "회사 주차장은 어디인가요?",
    "채용 공고 보고 싶어요",
    "오늘 날씨 어때요?",
    "대표이사가 누구인가요?",
    "직원 복지 제도 알려주세요",
]

# ① 관련 있는 질문들의 점수를 하나씩 구해서 리스트에 담기 
rel = []
for q in RELATED:
    rel.append(sim(BASE, q))

# ② 관련 없는 질문들도 똑같이
unrel = []
for q in UNRELATED:
    unrel.append(sim(BASE, q))

print("■ 관련 있는 질문")
for i in range(len(RELATED)):
    print(f"   {rel[i]:.3f}  {RELATED[i]}")
print(f"   → 최저 {min(rel):.3f}")

print("\n■ 관련 없는 질문")
for i in range(len(UNRELATED)):
    print(f"   {unrel[i]:.3f}  {UNRELATED[i]}") 
print(f"   → 최고 {max(unrel):.3f}")

print(f"\n▶ 권장 임계값: {(min(rel) + max(unrel)) / 2:.2f}")