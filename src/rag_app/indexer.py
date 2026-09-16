import os, re
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter 
# import config
from . import config

NOISE = ["㈜한국주식회사 대외비"]

def _load():
    docs = PyPDFLoader(str(config.DOC_PATH)).load()
    for d in docs:
        text = d.page_content
        for n in NOISE:
            text = text.replace(n, "")
        d.page_content = re.sub(r"\n{3,}", "\n\n", text).strip()         
        d.metadata["filename"] = config.DOC_PATH.name         
        d.metadata["page_no"]  = d.metadata.get("page", 0) + 1     
        return docs
    
def _split(docs):
    sp = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""])     
    chunks = sp.split_documents(docs)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = i
    return chunks

def get_store(rebuild: bool = False):
    # 인덱스가 있으면 로드, 없으면 생성 후 저장
    emb = OpenAIEmbeddings(model=config.EMBED_MODEL)
    
    if os.path.exists(config.INDEX_PATH) and not rebuild:         
        return FAISS.load_local(
            config.INDEX_PATH, 
            emb,
            allow_dangerous_deserialization=True)
    chunks = _split(_load())
    store  = FAISS.from_documents(chunks, emb)     
    store.save_local(config.INDEX_PATH)    
    print(f"✓ 인덱스 생성 완료 (조각 {len(chunks)}개)")     
    return store