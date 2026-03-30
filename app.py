import streamlit as st

st.set_page_config(page_title="MBTI 챗봇", page_icon="💬", layout="centered")

st.markdown("""
    <style>
    /* 네비게이션 메뉴의 글자 및 아이콘 크기 조절*/
    [data-testid="stSidebarNav"] span {
        font-size: 1.1rem !important;
    }
    

    </style>
""", unsafe_allow_html=True)

# 페이지 등록
pages = [
    st.Page("home.py", title="홈", icon=":material/home:"),
    st.Page("mbti_test.py", title="MBTI 측정", icon=":material/quiz:"),
    st.Page("mbti_relation.py", title="MBTI 관계 상담", icon=":material/handshake:"),
    st.Page("mbti_info.py", title="MBTI 알아가기", icon=":material/info:"),
]

pg = st.navigation(pages)
pg.run()