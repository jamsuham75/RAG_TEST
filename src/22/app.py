import os
import sys
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rag_app'))

# from rag import ask
from graph import ask

question = input("질문을 입력하세요: ")

result = ask(question)

print("\n답변:")
print(result["answer"])

print("\n출처:")
for source in result["sources"]:
    print(source)