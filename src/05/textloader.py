from langchain_community.document_loaders import TextLoader

loader = TextLoader("../../data/notice.txt", encoding="utf-8")
documents = loader.load()

print(f"로드: {len(documents)} 개")
print(f"내용: {documents[0].page_content}")
print(f"메타: {documents[0].metadata}")