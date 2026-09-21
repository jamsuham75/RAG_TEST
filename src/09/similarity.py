import numpy as np
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

emb = OpenAIEmbeddings(model="text-embedding-3-small")

def sim(a: str, b: str) -> float:
    # 두 문장을 좌표(벡터)로 바꾼다
    v1 = np.array(emb.embed_query(a))
    v2 = np.array(emb.embed_query(b))
    
    # 코사인 유사도 = 내적 ÷ (길이 × 길이)
    dot_product = np.dot(v1, v2)
    length1 = np.linalg.norm(v1)
    length2 = np.linalg.norm(v2)
    return float(dot_product / (length1 * length2))

PAIRS = [
    ("환불 규정",       "반품 절차"),        # 뜻은 같고 글자는 다름     
    ("비밀번호 변경",   "패스워드 재설정"),  # 완전한 동의어
    ("제품이 고장났어요", "기기 불량 신고"),  # 표현이 다름     
    ("환불 규정",       "배송 안내"),        # 약하게 관련     
    ("환불 규정",       "오늘 점심 메뉴"),   # 완전 무관
]

for a, b in PAIRS:
    print(f"{sim(a, b):.3f}   {a:<18} ↔ {b}")