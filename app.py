import streamlit as st

st.set_page_config(page_title="MBTI 챗봇", page_icon="💬", layout="centered")

# 페이지 등록
pages = [
    st.Page("home.py", title="홈", icon=":material/home:"),
    st.Page("mbti_test.py", title="나의 MBTI 측정하기", icon=":material/quiz:"),
    st.Page("mbti_info.py", title="MBTI 알아가기", icon=":material/info:"),
]

pg = st.navigation(pages)
pg.run()