import streamlit as st
import os
from openai_service import get_mbti_relation_response
from json_db import load_relation_messages, save_relation_messages, clear_relation_messages

st.title("🤝 MBTI 관계 상담소")
st.caption("나와 다른 MBTI의 궁합, 연애, 친구, 직장동료 관계 등에 대해 AI에게 물어보세요!")

api_key = os.getenv("OPENAI_API_KEY")

# 사용자 MBTI 확인
if "my_mbti" not in st.session_state or st.session_state.my_mbti.get("item", "없음") == "없음":
    st.warning("내 MBTI가 설정되어 있지 않습니다. 홈 화면에서 내 MBTI를 먼저 설정해주세요!")
    if st.button("홈으로 가서 설정하기", use_container_width=True):
        st.switch_page("home.py")
    st.stop() # 아래 코드 실행 중단

my_mbti = st.session_state.my_mbti["item"]

# 2. 화면 상단: 상대방 MBTI 선택 UI
mbti_list = [
    "자동",
    "ESTJ", "ESTP", "ESFJ", "ESFP", "ENTJ", "ENTP", "ENFJ", "ENFP",
    "ISTJ", "ISTP", "ISFJ", "ISFP", "INTJ", "INTP", "INFJ", "INFP"
]

st.write("---")
col1, col2 = st.columns(2)
with col1:
    st.info(f"👤 나의 MBTI: **{my_mbti}**")
with col2:
    target_mbti = st.selectbox("🔍 상대방의 MBTI 선택", mbti_list)

st.write("---")


# 사이드바 초기화 버튼 추가
with st.sidebar:
    st.write("### 🔄 초기화")
    st.caption("상담 대화 내용을 초기화합니다")
    if st.button("상담 초기화"):
        clear_relation_messages() # JSON 초기화
        initial_msg = f"안녕하세요! MBTI 관계에 대해 무엇이든 물어보세요.\n\n*(예: 우리 둘이 연애하면 궁합이 어때?, 같이 여행 갈 때 주의할 점 알려줘, 화났을 때 어떻게 풀어줘야 해?)*"
        st.session_state.relation_messages = [{"role": "assistant", "content": initial_msg}]
        save_relation_messages("assistant", initial_msg) # 초기 메시지 저장
        st.rerun()



# 현재 선택된 타겟 업데이트
st.session_state.relation_target = target_mbti

# DB에서 메시지 먼저 불러오기
db_messages = load_relation_messages()


initial_msg_content = f"안녕하세요! 관계에 대해 무엇이든 물어보세요.\n\n대화 맥락 속에서 제가 그 유형을 **유추**해서 관계를 분석해 드릴게요.\n그 사람의 특징이 드러나는 행동이나 고민거리를 이야기해 보세요.\n\n*(예: 우리 둘이 연애하면 궁합이 어때?, 같이 여행 갈 때 주의할 점 알려줘, 화났을 때 어떻게 풀어줘야 해?)*"

# DB에 메시지가 전혀 없다면 멘트 추가 및 저장
if not db_messages:
    st.session_state.relation_messages = [{"role": "assistant", "content": initial_msg_content}]
    save_relation_messages("assistant", initial_msg_content)
else:
    # DB에 내역이 있다면 그대로 불러와서 세션에 탑재
    st.session_state.relation_messages = db_messages




# 기존 대화 기록 출력
for msg in st.session_state.relation_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 채팅 입력 및 AI 응답 처리
input_placeholder = f"{target_mbti}와의 관계에 대해 질문해보세요" if target_mbti != "자동" else "상대방의 특징이 드러나는 고민을 이야기해보세요"
if prompt := st.chat_input(input_placeholder):
    if not api_key:
        st.error("사이드바(또는 환경변수)에 API Key를 확인해주세요.")
        st.stop()

    # 사용자 메시지 화면에 출력 및 저장
    st.session_state.relation_messages.append({"role": "user", "content": prompt})
    save_relation_messages("user", prompt)
    with st.chat_message("user"):
        st.write(prompt)

    # AI 응답 받아오기
    analysis_spin_text = f"AI가 관계성을 분석 중입니다..." if target_mbti != "자동" else "AI가 대화 맥락에서 상대방 유형을 유추하며 분석 중입니다..."
    with st.spinner(analysis_spin_text):
        response = get_mbti_relation_response(
            api_key=api_key, 
            user_mbti=my_mbti, 
            target_mbti=target_mbti,
            chat_history=st.session_state.relation_messages
        )

    # AI 메시지 화면에 출력 및 저장
    st.session_state.relation_messages.append({"role": "assistant", "content": response})
    save_relation_messages("assistant", response)
    with st.chat_message("assistant"):
        st.write(response)