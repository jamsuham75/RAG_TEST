from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("../../data/manual.pdf")
docs = loader.load()

print("총 페이지 수 :", len(docs))
print()
# 모든 쪽을 살펴보기 (지금은 2쪽뿐입니다)
for d in docs:
    page = d.metadata["page"]
    preview = d.page_content[:60].replace("\n", " ")     
    print(f"[{page}쪽] {preview} ...")