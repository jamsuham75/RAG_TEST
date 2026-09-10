from langchain_community.document_loaders import PyPDFLoader

# 1단계: PDF 로드
loader = PyPDFLoader("../../data/manual.pdf")
docs = loader.load()

def validate(docs):
    print("=" * 45)
    print("문서 개수 :", len(docs))
    # ① 빈 페이지 점검 (내용 없으면 스캔본 의심)
    empty_pages = []
    for d in docs:
        text = d.page_content.strip()
        if len(text) < 10:
            empty_pages.append(d.metadata.get("page", "?"))    
    if empty_pages:
        print("⚠ 내용이 거의 없는 페이지 :", empty_pages)         
        print("  → 스캔 PDF일 수 있습니다.")
    else:
        print("✓ 빈 페이지 없음")
    # ② 전체 글자 수 (너무 적으면 의심)
    total_len = 0
    for d in docs:
        total_len += len(d.page_content)
    print("전체 글자 수 :", total_len)
    # ③ 실제 내용을 눈으로 확인 (가장 중요!)
    print("-" * 45)
    print("첫 페이지 내용 :", docs[0].page_content[:200])     
    print("=" * 45)
    
validate(docs)