import os
import sys
import warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '11'))

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from retriever import search, build_context
from prompts import PROMPTS
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def compare(question):
    docs = search(question)            # 검색은 한 번만!
    ctx  = build_context(docs)
    
    print("=" * 60)
    print("Q:", question)
    print(f"근거 {len(docs)}개")
    print("-" * 60)
    
    for name, tmpl in PROMPTS.items():
        chain = tmpl | llm | StrOutputParser()
        ans = chain.invoke({"context": ctx, "question": question})         
        print(f"\n[{name}]")
        print(ans)
    print("=" * 60)
    
compare("환불 신청 방법과 수수료를 알려주세요")