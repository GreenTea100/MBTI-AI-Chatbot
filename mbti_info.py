import streamlit as st

def main():
    # 1. 페이지 전체 너비 활용 설정 및 제목 설정
    st.set_page_config(page_title="MBTI 4가지 지표 설명", page_icon="", layout="wide")

    # 타이틀 및 설명 중앙 정렬
    st.markdown("<h1 style='text-align: center;'>MBTI 4가지 핵심 지표 설명</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: gray;'>초보자를 위한 개념 정리</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- 1. 에너지의 방향 ---
    st.markdown("<h3 style='text-align: center;'>1. 에너지의 방향 (Energy Direction)</h3>", unsafe_allow_html=True)
    col_e, col_i = st.columns(2)
    with col_e:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>✨ E (Extraversion, 외향)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            외부 세계의 사람이나 사물에 에너지를 집중합니다.<br>
            외부와의 상호작용, 활동, 경험을 통해 에너지를 얻고 발산하며,<br>
            생각보다는 행동을 통해 세상을 이해하려는 경향이 있습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_i:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>🤫 I (Introversion, 내향)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            내면 세계의 개념, 아이디어, 생각에 에너지를 집중합니다.<br>
            내부적인 성찰과 조용한 환경 속에서 에너지를 축적하며,<br>
            행동하기 전에 먼저 심사숙고하여 내면을 이해하려는 경향이 있습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-top: 1px dashed #bbb;'>", unsafe_allow_html=True)

    # --- 2. 정보 수집 방식 ---
    st.markdown("<h3 style='text-align: center;'>2. 정보 수집 방식 (Information Gathering)</h3>", unsafe_allow_html=True)
    col_s, col_n = st.columns(2)
    with col_s:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>🔎 S (Sensing, 감각)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            오감을 통해 직접 경험하고 관찰할 수 있는 '현재의 사실'을 수용합니다.<br>
            구체적이고 현실적이며,<br>
            세부적인 데이터와 실용성을 중요하게 여깁니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_n:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>💡 N (Intuition, 직관)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            사실 이면에 숨겨진 의미, 관계, 가능성을 파악하는 데 집중합니다.<br>
            현재보다는 '미래'와 비전에 초점을 맞추며,<br>
            상상력이 풍부하고 전체적인 숲(맥락)을 보는 것을 중요하게 여깁니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 1px dashed #bbb;'>", unsafe_allow_html=True)

    # --- 3. 결정과 판단 방식 ---
    st.markdown("<h3 style='text-align: center;'>3. 결정과 판단 방식 (Decision Making)</h3>", unsafe_allow_html=True)
    col_t, col_f = st.columns(2)
    with col_t:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>⚖️ T (Thinking, 사고)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            객관적인 진실, 인과 관계, 논리적 원칙을 바탕으로 판단합니다.<br>
            맞고 틀림(True/False)을 명확히 구분하려 하며,<br>
            공정성과 합리성을 의사결정의 최우선 가치로 둡니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_f:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>🤝 F (Feeling, 감정)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            주관적인 가치, 사람들과의 관계, 상황이 미치는 영향을 바탕으로 판단합니다.<br>
            좋다 나쁘다(Good/Bad) 혹은 상황에 대한 정상을 참작하며,<br>
            조화와 공감을 의사결정의 최우선 가치로 둡니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 1px dashed #bbb;'>", unsafe_allow_html=True)

    # --- 4. 생활 양식 ---
    st.markdown("<h3 style='text-align: center;'>4. 생활 양식 (Lifestyle)</h3>", unsafe_allow_html=True)
    col_j, col_p = st.columns(2)
    with col_j:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>📅 J (Judging, 판단)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            체계적이고 구조화된 삶을 선호합니다.<br>
            목적 뚜렷한 계획을 세우고, 통제와 조정을 통해<br>
            상황을 마무리 짓는 것(결정 내리기)에 안정감을 느낍니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_p:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2>🤸 P (Perceiving, 인식)</h2>
            <p style='font-size: 16px; line-height: 1.6;'>
            자율적이고 융통성 있는 삶을 선호합니다.<br>
            상황에 맞추어 적응하며, 새로운 정보나 가능성을 위해<br>
            결정을 보류하고 개방적인 상태를 유지하는 것에 안정감을 느낍니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()