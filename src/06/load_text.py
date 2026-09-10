from langchain_community.document_loaders import TextLoader

loader = TextLoader(
    "../../data/notice.txt",
    encoding="utf-8"
)

docs = loader.load()

print("문서 개수 :", len(docs))
print("본문 길이 :", len(docs[0].page_content), "글자") 
print()
print("--- 본문 앞 100자 ---") 
print(docs[0].page_content[:100]) 
print()
print("--- 메타데이터 ---") 
print(docs[0].metadata)