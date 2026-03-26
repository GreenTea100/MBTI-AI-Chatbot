import streamlit as st
from dotenv import load_dotenv
import os

from json_db import (
    load_messages,
    save_messages,
    clear_messages,
    init_db,
    save_conversation_id,
    load_conversation_id
)
from openai_service import (
    create_openai_client,
    get_ai_response,
    create_conversation,
    init_rag_db,
    retrieve_info,
    analyze_user_mbti
)

# 아이콘
ICON_USER = "icon/user.png"
ICON_AI_BASIC = "icon/basic.png"
ICON_AI_F = "icon/f.png"
ICON_AI_T = "icon/t.png"


# .env 파일 로드
load_dotenv()

# 앱 시작 시 JSON 파일 초기화
init_db()


# ----------------------
# 사이드바
# ----------------------
with st.sidebar:
    pages = [
        st.Page("app.py", title="홈", icon=":material/home:"),
        st.Page("mbti_info.py", title="MBTI 알아가기", icon=":material/info:"),
    ]
    pg = st.navigation(pages, position="sidebar", expanded=True)
    # pg.run()





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
            client = create_openai_client(openai_api_key)
            # 분석하는 동안 로딩 스피너 보여주기
            with st.spinner("사용자의 뼛속까지 분석 중..."):
                # session_state에 저장된 전체 대화 기록을 함수에 넘겨줌
                analysis_result = analyze_user_mbti(client, st.session_state["messages"])
                
                # 분석 결과를 사이드바에 예쁜 초록색 창으로 출력
                st.success(analysis_result)




    # -------------------
    # 대화 내역 다운로드 
    # -------------------
    st.write("---")
    st.write("### 💾 대화 내역 저장")
    st.caption("현재까지의 대화를 텍스트 파일로 다운로드합니다")

    # 1. json_db.py의 함수를 이용해 JSON 파일에서 직접 대화 기록 전체를 불러옵니다.
    all_saved_messages = load_messages()

    # 2. 다운로드할 텍스트 형식 만들기
    chat_export = "MBTI 과몰입 챗봇 대화 내역\n"
    chat_export += "=" * 30 + "\n\n"
    
    # 3. JSON에서 불러온 메시지들을 예쁘게 줄바꿈하여 하나의 문자열로 합칩니다.
    for msg in all_saved_messages:
        # 화자 이름 설정
        if msg["role"] == "user":
            speaker = "나"
        else:
            persona = msg.get("persona")
            speaker = f"챗봇 ({persona})"
            
        # 대화 내용 추가
        chat_export += f"{speaker}: {msg['content']}\n\n"

    # 4. 스트림릿 기본 다운로드 버튼 생성
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
    st.caption("대화 내용은 JSON 파일에 저장됩니다")
    if st.button("대화 초기화"):
        clear_messages()

        # session_state 초기화
        st.session_state["messages"] = [
            {"role" : "assistant", "content" : "무엇을 도와드릴까요?"}
        ]

        # 초기 메시지 JSON에 저장
        save_messages("assistant", "무엇을 도와드릴까요?", "기본")

        st.rerun()

# ----------------------
# 제목 
# ----------------------
st.title("💬 MBTI 과몰입러")
st.caption("🚀 다양한 유형의 답변을 받을 수 있습니다")


# 성향 리스트
t_f_list = [
        "기본",
        "T (사고형)",
        "F (감정형)"
    ]

# 라디오버튼
t_f_choice = st.radio(label= " ", options=t_f_list, horizontal=True)
st.text(f"현재 모드: {t_f_choice}")



# RAG 데이터베이스 초기화
collection = init_rag_db()



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

if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = load_conversation_id()


# ----------------------
# 기존 대화 출력
# ----------------------
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=ICON_USER):
            st.markdown(msg["content"])
    # st.chat_message(msg["role"]).write(msg["content"])
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
        st.info("Please add your OpenAI API key to continue.")
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

    # OpenAI 클라이언트 설정
    client = create_openai_client(openai_api_key)

    # 현재 세션에서 conversation_id 확인
    conversation_id = st.session_state.get("conversation_id")

    # 세션에 없으면 JSON 파일에서 확인
    if not conversation_id:
        conversation_id = load_conversation_id()

    # JSON 파일에서 없으면 새로 생성
    if not conversation_id:
        conversation_id = create_conversation(client)
        save_conversation_id(conversation_id)

    # session_state에도 반영
    st.session_state["conversation_id"] = conversation_id

    # 사용자의 질문을 바탕으로 ChromaDB에서 관련 지식 검색
    retrieved_context = retrieve_info(collection, prompt)

    # AI 응답 받기
    try:
        with st.spinner("응답을 생성 중입니다..."):
            assistant_text = get_ai_response(
                client=client,
                prompt=prompt,
                conversation_id=st.session_state["conversation_id"],
                context=retrieved_context,  # RAG로 찾은 지식 전달
                persona=t_f_choice           # UI에서 선택한 mbti 전달
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



    # 화면에 AI 응답 출력 (현재 선택한 모드에 맞는 아이콘 적용)
    if t_f_choice == "T (사고형)":
        current_ai_icon = ICON_AI_T

    elif t_f_choice == "F (감정형)":
        current_ai_icon = ICON_AI_F

    else:
        current_ai_icon = ICON_AI_BASIC

    with st.chat_message("assistant", avatar=current_ai_icon):
        st.write(assistant_text)
