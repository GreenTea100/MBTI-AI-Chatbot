import streamlit as st
from dotenv import load_dotenv
import os

from json_db import (
    load_messages,
    save_messages,
    clear_messages,
    init_db,
)
from openai_service import (
    get_ai_response,
    init_rag_db,
    analyze_user_mbti
)

# 아이콘
ICON_USER = "icon/user.png"
ICON_AI_BASIC = "icon/basic.png"
ICON_AI_F = "icon/f.png"
ICON_AI_T = "icon/t.png"

# mbti 리스트
mbti_list = [
    "????",
    "ESTJ",
    "ESTP",
    "ESFJ",
    "ESFP",
    "ENTJ",
    "ENTP",
    "ENFJ",
    "ENFP",
    "ISTJ",
    "ISTP",
    "ISFJ",
    "ISFP",
    "INTJ",
    "INTP",
    "INFJ",
    "INFP",
]

# .env 파일 로드
load_dotenv()

# 앱 시작 시 JSON 파일 초기화
init_db()


# 사용자 MBTI 설정 팝오버
def toggle_popover():
    st.session_state.drawer = not st.session_state.drawer

def on_popover_change():
    pass

# session_state 초기화
if "my_mbti" not in st.session_state:
    st.session_state.my_mbti = {"item": "없음"}

if "mbti_radio" not in st.session_state:
    st.session_state["mbti_radio"] = "기본"


with st.popover(f"나의 MBTI ({st.session_state.my_mbti['item']})", on_change=on_popover_change, key='drawer'):
    st.markdown("당신의 MBTI를 알고 계십니까?")
    
    my_mbti = st.selectbox('MBTI 선택', mbti_list)
    
    if st.button("확인", on_click=toggle_popover):
        # 선택한 값을 session_state에 저장
        st.session_state.my_mbti = {"item": my_mbti}
        st.rerun()




# ----------------------
# 사용자 MBTI 설정 모달창
# ----------------------
@st.dialog("나의 MBTI 설정")
def mbti_setup_modal():
    st.markdown("### 당신의 MBTI를 알고 계십니까?")
    
    # 셀렉트박스로 16가지 선택지 입력
    selected_mbti = st.selectbox("알고 있다면 아래에서 선택해주세요.", mbti_list)
    
    col1, col2= st.columns(2)
    with col1:
        # 확인 버튼을 누르면 세션에 저장하고 모달 닫기
        if st.button("저장하기", use_container_width=True):
            st.session_state.my_mbti = {"item": selected_mbti}
            st.rerun()
    with col2:
        # 모른다면 MBTI 테스트 페이지로 강제 이동
        if st.button("MBTI를 모른다면?", use_container_width=True):
            st.switch_page("mbti_test.py")

    # 모른다면 MBTI 테스트 페이지로 강제 이동
    if st.button("간단하게 MBTI 알아보기", use_container_width=True):
            st.switch_page("mbti_info.py")



# ----------------------
# 모달창 호출 로직
# ----------------------
# MBTI가 "없음"이면 강제로 모달창 띄우기
if st.session_state.my_mbti["item"] == "없음":
    mbti_setup_modal()



with st.sidebar:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    

    # ------------------
    # '성향 분석' 버튼 
    # ------------------
    st.write("### 🔍 내 성향 분석")
    st.caption("AI가 내 대화 기록을 보고 T/F를 판독합니다")
    
    # 분석 버튼 생성
    if st.button("내 T/F 성향 판독하기"):
        if not openai_api_key:
            st.warning("API Key가 없습니다.")
        else:
            # 분석하는 동안 로딩 스피너 보여주기
            with st.spinner("사용자의 뼛속까지 분석 중..."):
                # session_state에 저장된 전체 대화 기록을 함수에 넘겨줌
                analysis_result = analyze_user_mbti(openai_api_key, st.session_state["messages"])
                
                # 분석 결과를 사이드바에 예쁜 초록색 창으로 출력
                st.success(analysis_result)




    # -------------------
    # 대화 내역 다운로드 
    # -------------------
    st.write("---")
    st.write("### 💾 대화 내역 저장")
    st.caption("현재까지의 대화를 텍스트 파일로 다운로드합니다")

    # json_db.py의 함수를 이용해 JSON 파일에서 직접 대화 기록 전체를 불러옵니다.
    all_saved_messages = load_messages()

    # 다운로드할 텍스트 형식 만들기
    chat_export = "MBTI 과몰입 챗봇 대화 내역\n"
    chat_export += "=" * 30 + "\n\n"
    
    # JSON에서 불러온 메시지들을 줄바꿈하여 하나의 문자열로 합칩니다.
    for msg in all_saved_messages:
        # 화자 이름 설정
        if msg["role"] == "user":
            speaker = "나"
        else:
            persona = msg.get("persona", "기본")
            speaker = f"챗봇 ({persona})"
            
        # 대화 내용 추가
        chat_export += f"{speaker}: {msg['content']}\n\n"

    # 스트림릿 기본 다운로드 버튼 생성
    st.download_button(
        label="대화 내역 다운로드 (.txt)",
        data=chat_export,              # 위에서 만든 텍스트 데이터
        file_name="mbti_chat_history.txt", # 저장될 파일 이름
        mime="text/plain"              # 텍스트 파일 형식 지정
    )



    # ------------------
    # 대화 초기화 버튼
    # ------------------
    st.write("---")
    st.write("### 🔄 초기화")
    st.caption("입력된 대화 내용을 초기화합니다")
    if st.button("대화 초기화"):
        clear_messages()

        # session_state 초기화
        st.session_state["messages"] = [
            {"role" : "assistant", "content" : "무엇을 도와드릴까요?", "persona": "기본"}
        ]

        # 초기 메시지 JSON에 저장
        save_messages("assistant", "무엇을 도와드릴까요?", "기본")

        
        st.session_state["mbit_radio"] = "기본"

        st.rerun()

# ----------------------
# 제목 
# ----------------------
st.title("💬 MBTI 과몰입러")
st.caption("🚀 다양한 유형의 답변을 받을 수 있습니다")


# 성향 리스트
t_f_list = ["기본", "T (사고형)", "F (감정형)"]

# 라디오버튼
t_f_choice = st.radio(label= " ", options=t_f_list, horizontal=True, key="mbti_radio")

if t_f_choice == "기본":
    st.text("현재 모드: 기본 (일반적인 AI 챗봇)")

elif t_f_choice == "T (사고형)":
    st.text("현재 모드: T (이성적이고 논리적인 'T' 성향의 챗봇)")

else:
    st.text("현재 모드: F (감수성이 풍부하고 공감 능력이 뛰어난 'F' 성향의 챗봇)")




# RAG VectorDB 초기화
vectorstore = init_rag_db(openai_api_key)



# ----------------------
# 초기 대화 기록 불러오기
# ----------------------
if "messages" not in st.session_state:
    db_messages = load_messages()

    if not db_messages:
        first_message = {
            "role" : "assistant",
            "content" : "무엇을 도와드릴까요?",
            "persona" : "기본"
        }
        st.session_state["messages"] = [first_message]
        save_messages(first_message["role"], first_message["content"], first_message["persona"])
    else:
        st.session_state["messages"] = db_messages


# ----------------------
# 기존 대화 출력
# ----------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=ICON_USER):
            st.markdown(msg["content"])

    else:
        # 저장된 페르소나 정보를 불러와 아이콘 매칭(정보 없으면 기본)
        saved_persona = msg.get("persona", "기본")

        if saved_persona == "T (사고형)":
            icon = ICON_AI_T
        elif saved_persona == "F (감정형)":
            icon = ICON_AI_F
        else:
            icon = ICON_AI_BASIC
            
        with st.chat_message("assistant", avatar=icon):
            st.markdown(msg["content"])

# ----------------------
# 사용자 입력 처리
# ----------------------
if prompt := st.chat_input("메시지를 입력하세요"):
    # API Key가 없으면 중단
    if not openai_api_key:
        st.info("OpenAI API key 확인해주세요.")
        st.stop()



    # ----------------------
    # 사용자 메시지 처리
    # ----------------------
    user_message = {
        "role" : "user",
        "content" : prompt
    }


    # session_state에 저장
    st.session_state["messages"].append(user_message)

    # JSON 파일에도 저장
    save_messages(user_message["role"], user_message["content"], "기본")

    # 화면에 사용자 메시지 출력
    with st.chat_message("user", avatar=ICON_USER):
        st.write(prompt)



    # AI 응답 받기
    try:
        with st.spinner("응답을 생성 중입니다..."):
            # 이전 대화 기록을 LangChain에 넘겨주기 위해 세션에서 추출 (가장 마지막 질문 제외)
            history_for_agent = st.session_state["messages"][:-1]
            assistant_text = get_ai_response(
                api_key=openai_api_key,
                prompt=prompt,
                chat_history=history_for_agent,   # JSON 대화 기록 전달
                vectorstore=vectorstore,          # VectorDB 전달
                persona=t_f_choice                # UI에서 선택한 mbti 전달
            )
    except Exception as e:
        assistant_text = f"오류가 발생하였습니다: {e}"


    # AI 응답 메시지 생성
    assistant_message = {
        "role" : "assistant",
        "content" : assistant_text,
        "persona" : t_f_choice
    }

    # session_state에 저장
    st.session_state["messages"].append(assistant_message)

    save_messages(assistant_message["role"], assistant_message["content"], t_f_choice)



    # 화면에 AI 응답 출력 (아이콘 적용)
    if t_f_choice == "T (사고형)":
        current_ai_icon = ICON_AI_T

    elif t_f_choice == "F (감정형)":
        current_ai_icon = ICON_AI_F

    else:
        current_ai_icon = ICON_AI_BASIC

    with st.chat_message("assistant", avatar=current_ai_icon):
        st.write(assistant_text)
