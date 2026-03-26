import streamlit as st
import os
import re
from openai_service import get_mbti_test_response 

st.title("📝 AI가 말아주는 MBTI 테스트")
st.caption("AI가 실시간으로 질문을 만들고 당신의 성향을 분석합니다! (참고만 하시고 정확한 진단은 정식 검사를 추천합니다)")

# API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")

# ----------------------
# 세션 상태 (Session State) 초기화
# ----------------------
if "test_mode" not in st.session_state:
    st.session_state.test_mode = None  # "simple" 또는 "detailed"
if "test_messages" not in st.session_state:
    st.session_state.test_messages = [] 
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# ----------------------
# 제어 로직 함수
# ----------------------
def start_test(mode):
    st.session_state.test_mode = mode
    st.session_state.test_messages = []
    st.session_state.question_count = 0
    
    with st.spinner("AI가 첫 번째 질문을 준비하고 있습니다..."):
        ai_reply = get_mbti_test_response(api_key, mode, st.session_state.test_messages)
        st.session_state.test_messages.append({"role": "assistant", "content": ai_reply})

def submit_answer(answer):
    st.session_state.test_messages.append({"role": "user", "content": answer})
    st.session_state.question_count += 1
    
    with st.spinner("AI가 답변을 분석하고 있습니다..."):
        ai_reply = get_mbti_test_response(api_key, st.session_state.test_mode, st.session_state.test_messages)
        st.session_state.test_messages.append({"role": "assistant", "content": ai_reply})

# ----------------------
# 화면 UI 구성
# ----------------------
if st.session_state.test_mode is None:
    st.write("### 어떤 방식의 테스트를 원하시나요?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 간단 버전 (10문제 / A, B 선택)", use_container_width=True):
            if api_key:
                start_test("simple")
                st.rerun()
            else:
                st.warning("사이드바에서 API Key를 먼저 입력해주세요.")
    with col2:
        if st.button("🟣 상세 버전 (30문제 / 상황극 몰입)", use_container_width=True):
            if api_key:
                start_test("detailed")
                st.rerun()
            else:
                st.warning("사이드바에서 API Key를 먼저 입력해주세요.")
else:
    st.markdown("Tip. 깊은 고민하지 말고 처음 볼 때 느껴지는 직관적인 선택을 하면 조금 더 정확도를 올릴 수 있어요!")
    if st.button("🔄 테스트 다시 고르기 / 초기화"):
        st.session_state.test_mode = None
        st.rerun()
        
    st.write("---")
    
    last_ai_msg = ""
    for msg in reversed(st.session_state.test_messages):
        if msg["role"] == "assistant":
            last_ai_msg = msg["content"]
            break
            
    st.info(last_ai_msg)
                
    # 버전별로 최대 문제 수 (간단: 10, 상세: 30)
    max_questions = 10 if st.session_state.test_mode == "simple" else 30
    
    # 진행도 표시 바
    progress = st.session_state.question_count / max_questions
    st.progress(progress if progress <= 1.0 else 1.0, text=f"{st.session_state.question_count}/{max_questions}")
                
    # 사용자가 선택할 버튼 UI
    if st.session_state.question_count < max_questions:
        st.write("---")
        if st.session_state.test_mode == "simple":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🅰️ 선택", use_container_width=True):
                    submit_answer("A를 선택하겠습니다.")
                    st.rerun()
            with col2:
                if st.button("🅱️ 선택", use_container_width=True):
                    submit_answer("B를 선택하겠습니다.")
                    st.rerun()
                    
        elif st.session_state.test_mode == "detailed":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("그렇다", use_container_width=True):
                    submit_answer("그렇다")
                    st.rerun()
            with col2:
                if st.button("약간 그렇다", use_container_width=True):
                    submit_answer("약간 그렇다")
                    st.rerun()
            with col3:
                if st.button("약간 그렇지 않다", use_container_width=True):
                    submit_answer("약간 그렇지 않다")
                    st.rerun()
            with col4:
                if st.button("그렇지 않다", use_container_width=True):
                    submit_answer("그렇지 않다")
                    st.rerun()
    else:
        st.success("테스트가 완료되었습니다! 위에서 AI의 분석 결과를 확인하세요.")


        # 마지막 답변에서 MBTI 4자리 알파벳(E/I, S/N, T/F, J/P) 자동 추출
        match = re.search(r'[EI][SN][TF][JP]', last_ai_msg)
        
        if match:
            extracted_mbti = match.group()
        else:
            extracted_mbti = None
            st.warning("정확한 MBTI 코드를 추출하지 못했습니다. AI의 답변을 직접 확인해 주세요.")
            
        st.write("---")

        # 테스트 완료 시 사이드바에 분석 결과 다운 버튼
        with st.sidebar:
            st.write("### 💾 분석 결과 저장")
            st.caption("AI의 MBTI 분석 결과를 텍스트 파일로 다운로드합니다")
            
            # 다운로드할 텍스트 파일의 내용 꾸미기
            export_text = "MBTI 분석 결과\n"
            export_text += "=" * 30 + "\n\n"
            export_text += last_ai_msg  # AI의 마지막 분석 내용 추가

            st.download_button(
                label="분석 결과 다운로드 (.txt)",
                data=export_text,
                file_name="my_mbti.txt",
                mime="text/plain",
                use_container_width=True
            )

        
        # 홈으로 돌아가기 버튼 및 저장
        if st.button("홈으로", use_container_width=True):
            # 추출된 MBTI가 있으면 session_state에 저장
            if extracted_mbti:
                st.session_state.my_mbti = {"item": extracted_mbti}
            
            # 다음번 테스트를 위해 테스트 상태 초기화
            st.session_state.test_mode = None
            st.session_state.test_messages = []
            st.session_state.question_count = 0
            
            # 홈 화면(home.py)으로 강제 이동
            st.switch_page("home.py")