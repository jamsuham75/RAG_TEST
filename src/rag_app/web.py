import streamlit as st
from rag import ask

st.set_page_config(page_title="문서 Q&A", page_icon="■")

st.title("■ 문서 기반 질의응답")

if "history" not in st.session_state:
    st.session_state.history = []

q = st.chat_input("궁금한 것을 물어보세요")

if q:
    with st.spinner("자료를 찾는 중..."):
        result = ask(q)

    st.session_state.history.append((q, result))

for question, result in st.session_state.history:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        st.write(result["answer"])
        
        if result["sources"]:
            # 중복 없이, 순서대로 페이지 번호만 모으기             
            pages = []
            for s in result["sources"]:
                if s["page"] not in pages:
                    pages.append(s["page"])
            pages.sort()
            page_texts = []
            for p in pages:
                page_texts.append(str(p))
            page_text = ", ".join(page_texts)             
            st.caption(f"※ 참고: {result['sources'][0]['file']} "                        
                       f"{page_text}페이지")