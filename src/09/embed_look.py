from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
emb = OpenAIEmbeddings(model="text-embedding-3-small") 

vec = emb.embed_query("환불 규정이 궁금합니다")
print("차원 수 :", len(vec))
print("앞 10개 :", [round(v, 4) for v in vec[:10]]) 
print("최댓값  :", round(max(vec), 4))
print("최솟값  :", round(min(vec), 4))