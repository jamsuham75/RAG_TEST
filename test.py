import sys


print("=" * 50)
print("RAG 환경 설정 테스트")
print("=" * 50)
print(f"Python 버전: {sys.version}")

packages = [
    ("langchain", "LangChain"),
    ("openai", "OpenAI"),
    ("faiss", "FAISS"),
    ("chromadb", "Chroma"),
    ("dotenv", "python-dotenv"),
]

for module_name, display_name in packages:
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", None)
        version_text = f" (버전: {version})" if version else ""
        print(f"[OK] {display_name} 설치됨{version_text}")
    except ImportError:
        print(f"[MISSING] {display_name} 설치되지 않음")

print("=" * 50)
print("환경 확인 완료")
print("=" * 50)
