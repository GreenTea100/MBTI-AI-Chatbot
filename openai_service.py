from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup
import streamlit as st

# ----------------------
# RAG Vector DB 초기화
# ----------------------
@st.cache_resource
def init_rag_db(api_key):
    if not api_key:
        return None
        
    embeddings = OpenAIEmbeddings(api_key=api_key)
    
    # LangChain의 Document 객체 리스트 생성
    documents = [
        Document(
            page_content="E(외향형)는 외부 세계의 사람이나 사물에 에너지를 집중합니다. 다양한 사람들과의 활발한 상호작용과 활동을 통해 에너지를 충전하며, 생각하기 전에 먼저 말하거나 행동하면서 아이디어를 구체화하는 경향이 있습니다. 폭넓은 대인관계를 선호합니다.", 
            metadata={"topic": "E_trait"}
        ),
        Document(
            page_content="I(내향형)는 내면 세계의 개념, 생각, 아이디어에 에너지를 집중합니다. 조용히 혼자만의 시간을 가지거나 소수의 사람과 깊이 있는 관계를 맺을 때 에너지를 충전합니다. 말이나 행동을 하기 전에 마음속으로 충분히 심사숙고하는 경향이 있습니다.", 
            metadata={"topic": "I_trait"}
        ),
        Document(
            page_content="E와 I의 갈등 및 대화법: E는 즉각적인 반응과 활발한 티키타카를 원하지만, I는 질문을 받으면 생각을 정리할 '침묵의 시간'이 필요합니다. E는 I의 침묵을 '나에게 관심이 없나?'라고 오해할 수 있고, I는 E의 쏟아지는 말과 에너지를 '부담스럽고 기 빨린다'고 느낄 수 있습니다. E는 I에게 대답할 시간을 충분히 주고, I는 E에게 '지금 생각 중이야'라고 신호를 보내주는 것이 좋습니다.", 
            metadata={"topic": "EI_conflict"}
        ),
        Document(
            page_content="S(감각형)는 오감을 통해 직접 경험하고 관찰할 수 있는 '현재의 사실'과 데이터에 집중합니다. 현실적이고 실용적이며, 매뉴얼이나 과거의 경험을 중시합니다. 나무를 먼저 보고 숲을 파악하는 바텀업(Bottom-up) 방식을 선호합니다.", 
            metadata={"topic": "S_trait"}
        ),
        Document(
            page_content="N(직관형)는 눈에 보이지 않는 이면의 의미, 가능성, '미래'의 비전에 집중합니다. 상상력이 풍부하고 새로운 아이디어를 즐기며, 일상적인 것보다는 비유와 은유를 자주 사용합니다. 숲을 먼저 보고 나무를 파악하는 탑다운(Top-down) 방식을 선호합니다.", 
            metadata={"topic": "N_trait"}
        ),
        Document(
            page_content="S와 N의 갈등 및 대화법: S는 A부터 Z까지 순서대로 정확한 사실과 디테일을 원하지만, N은 맥락과 결론, 비유를 섞어 비약적으로 설명하는 경향이 있습니다. S는 N을 '뜬구름 잡는 소리만 한다'고 답답해하고, N은 S를 '융통성 없고 말귀를 못 알아듣는다'고 오해할 수 있습니다. S에게는 '구체적인 예시'를 들어주고, N에게는 '전체적인 큰 그림이나 목적'을 먼저 말해주는 것이 좋습니다.", 
            metadata={"topic": "SN_conflict"}
        ),
        Document(
            page_content="T(사고형)는 의사결정을 할 때 객관적인 사실, 논리, 인과관계를 바탕으로 판단합니다. 무엇이 '맞고 틀린지(True/False)'를 명확히 구분하려 하며, 공정성과 합리성, 원인 분석과 문제 해결을 가장 중요하게 생각합니다.", 
            metadata={"topic": "T_trait"}
        ),
        Document(
            page_content="F(감정형)는 의사결정을 할 때 사람들과의 관계, 상황적인 맥락, 자신과 타인의 가치를 바탕으로 판단합니다. 무엇이 '좋고 나쁜지(Good/Bad)' 혹은 상대방의 기분이 어떤지를 살피며, 인간관계의 조화와 정서적인 공감을 가장 중요하게 생각합니다.", 
            metadata={"topic": "F_trait"}
        ),
        Document(
            page_content="T와 F의 갈등 및 대화법: T는 상대방의 고민을 들으면 '해결책'을 찾아주는 것이 진정한 도움이라 생각하여 팩트를 지적합니다. 반면 F는 내 감정을 알아주고 '정서적 지지'를 해주는 것을 원합니다. T 성향에게 칭찬할 때는 구체적인 성과와 논리를 바탕으로 능력을 인정해 주고, F 성향에게 칭찬할 때는 그들의 노력과 배려에 대해 감정적으로 공감하며 고마움을 표현하는 것이 좋습니다.", 
            metadata={"topic": "TF_conflict"}
        ),
        Document(
            page_content="J(판단형)는 분명한 목적과 방향성을 가지고 체계적으로 계획을 세우는 것을 선호합니다. 정해진 기한을 엄수하고, 불확실성을 통제하려 하며, 일을 미리미리 끝내놓아야 심리적인 안정감을 느낍니다. '결정'을 내리는 것을 좋아합니다.", 
            metadata={"topic": "J_trait"}
        ),
        Document(
            page_content="P(인식형)는 목적과 방향성을 상황에 맞게 유연하게 변경하며 자율적인 방식을 선호합니다. 정해진 계획보다는 그때그때의 느낌과 융통성을 중시하며, 마감 기한이 임박했을 때 엄청난 에너지를 발휘합니다. 정보 수집을 위해 '결정을 보류'하는 것을 편안하게 여깁니다.", 
            metadata={"topic": "P_trait"}
        ),
        Document(
            page_content="J와 P의 갈등 및 대화법: J는 세워둔 계획이 틀어지면 극심한 스트레스를 받지만, P는 너무 빡빡한 계획과 통제 속에서 숨 막혀 합니다. 여행을 갈 때 J는 시간 단위로 일정을 짜려 하고, P는 발길 닿는 대로 가자고 합니다. J는 P를 '게으르고 무책임하다'고 보고, P는 J를 '강박적이고 피곤하게 산다'고 볼 수 있습니다. 함께 일할 때 J는 P에게 일의 '최종 마감일'만 명확히 주고 과정은 믿고 맡겨야 하며, P는 J를 위해 '중간 진행 상황'을 틈틈이 공유해 주어 불안감을 덜어주어야 합니다.", 
            metadata={"topic": "JP_conflict"}
        )
    ]
    
    # 메모리상에 Chroma DB 구축
    vectorstore = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings,
        collection_name="mbti_knowledge"
    )
    return vectorstore

# ------------------------------------
# Agent가 사용할 RAG 검색 Tool 정의
# ------------------------------------
def get_retriever_tool(vectorstore):
    @tool
    def search_mbti_knowledge(query: str) -> str:
        """MBTI에 관한 질문, 각 유형에 대한 특징, 특히 T(사고형)와 F(감정형)의 특징, 차이점, 갈등 원인, 대화법에 대한 전문 지식을 검색할 때 반드시 사용하고,
        그 이유에 대한 근거를 찾아서 다시 한 번 검증하세요.
        https://namu.wiki/w/%EB%A7%88%EC%9D%B4%EC%96%B4%EC%8A%A4-%EB%B8%8C%EB%A6%AD%EC%8A%A4%20%EC%9C%A0%ED%98%95%20%EC%A7%80%ED%91%9C?from=MBTI
        MBTI의 지식을 위 링크의 자료와 비교를 한 번 더 해서 결과를 출력하세요. """
        if not vectorstore:
            return "지식 베이스가 초기화되지 않았습니다."
        # 가장 유사도 높은 문서 1개 검색
        docs = vectorstore.similarity_search(query, k=1)
        return docs[0].page_content if docs else "관련 지식을 찾을 수 없습니다."
    
    return search_mbti_knowledge

# ----------------------------
# webSearch tool
# ----------------------------
@tool
def web_search_tool(query: str) -> str:
    """MBTI와 관련된 최신 밈, 유행, 또는 RAG 벡터 DB에 없는 추가적이고 방대한 정보를 인터넷에서 검색할 때 사용합니다."""
    search = DuckDuckGoSearchRun()
    return search.invoke(query)





# ----------------------------
# Agent를 이용한 AI 응답 생성
# ----------------------------
def get_ai_response(api_key, prompt, chat_history, vectorstore, persona="기본"):
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4.1-nano", api_key=api_key, temperature=0.7)
                        # 모델 차이, 선택 이유
    
    # 페르소나 설정
    persona_prompts = {
        "기본": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 객관적이고 유용한 정보를 명확하게 제공하세요.",

        "T (사고형)": "당신은 철저하게 이성적이고 논리적인 'T' 성향의 챗봇입니다."
        "사용자의 말에서 감정적인 부분보다 '사실 관계(Fact)'와 '원인'을 먼저 파악해주세요."
        "무의미한 위로나 공감하는 척하는 말, 화려한 이모티콘은 절대 쓰지마세요."
        "상대방의 문제를 빠르고 정확하게 분석해서 '현실적이고 실질적인 해결책'을 제시하는 것이 당신이 생각하는 최고의 친절입니다."
        "말투는 조금 차갑고 단호하지만, 내용 자체는 뼈 때리는 팩트와 논리로 가득 차 있어야 합니다."
        "꼭 존댓말과 평어체를 쓰세요.",

        "F (감정형)": "당신은 감수성이 풍부하고 공감 능력이 뛰어난 'F' 성향의 챗봇입니다."
        "사용자의 말에 담긴 '기분과 감정'을 읽어내고 그것을 온전히 인정해 주는 것을 최우선으로 해주세요."
        "섣부른 조언이나 차가운 해결책을 제시하기 전에, 반드시 먼저 상황에 깊이 몰입해서 충분한 위로와 지지를 보내주세요."
        "'정말 힘들었겠다', '속상했겠다' 같은 다정한 리액션을 아낌없이 사용하고, 따뜻하고 부드러운 말투를 써주세요."
        "존댓말을 쓰되 가까운 사이처럼 다정하게 말해주세요."
        "당신의 목표는 문제를 당장 해결하는 게 아니라, 상대방이 '내 편이 있구나' 하고 든든함을 느끼게 만드는 것 입니다."
    }
    
    # Agent 지침 추가
    system_instruction = persona_prompts.get(persona, persona_prompts["기본"])
    system_instruction += "\n\n중요: 당신은 외부 도구(Tool)를 사용해 지식을 검색할 수 있습니다. 지식을 검색하더라도 반드시 위에서 부여된 성향(말투, 공감 또는 팩트 폭행)을 철저하게 유지해서 답변하세요."



    # 검색 도구 연결
    tools = [get_retriever_tool(vectorstore), web_search_tool]

# LangGraph React Agent 생성
    agent_executor = create_react_agent(llm, tools)

    # 대화 기록 조립 (시스템 메시지 -> 과거 대화 -> 현재 질문)
    lc_messages = [SystemMessage(content=system_instruction)]
    
    for msg in chat_history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
            
    lc_messages.append(HumanMessage(content=prompt))

    # Agent 실행
    response = agent_executor.invoke({"messages": lc_messages})

    # 가장 마지막에 AI가 생성한 메시지 내용만 반환
    return response["messages"][-1].content

# ----------------------
# 사용자 T/F 성향 분석 (LangChain Chain 사용)
# ----------------------
def analyze_user_mbti(api_key, chat_history):
    llm = ChatOpenAI(model="gpt-4.1-nano", api_key=api_key, temperature=0.7)
    
    user_messages = [msg["content"] for msg in chat_history if msg["role"] == "user"]
    if not user_messages:
        return "분석할 대화 내용이 부족해요! 먼저 챗봇과 대화를 조금 나눠보세요."

    combined_messages = "\n".join([f"- {msg}" for msg in user_messages])

    instruction = (
        "당신은 날카로운 심리 분석 전문가입니다. "
        "아래 제공된 사용자의 대화 기록을 분석하여, 이 사용자가 'T(사고형)'에 가까운지 'F(감정형)'에 가까운지 퍼센트(%)와 함께 판독해주세요.\n"
        "결과는 '당신의 T/F 성향은 [결과]입니다!' 형식으로 시작하고, 한 줄 띄우고 "
        "왜 그렇게 생각했는지 사용자가 썼던 대화 내용을 근거로 들어서 3~4줄로 재미있게 팩트 폭행하거나 공감하며 설명해주세요."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("user", "[사용자 대화 기록]\n{messages}\n\n이 대화 기록을 바탕으로 내 T/F 성향을 분석해줘.")
    ])

    # LangChain LCEL 체인 생성 및 실행
    chain = prompt | llm
    response = chain.invoke({"messages": combined_messages})

    return response.content





# ----------------------
# MBTI 테스트 진행용 AI 응답 생성
# ----------------------
def get_mbti_test_response(api_key, mode, chat_history):
    llm = ChatOpenAI(model="gpt-4.1-nano", api_key=api_key, temperature=0.7)
    
    # AI에게 부여할 프롬프트 명령 대본
    PROMPT_SIMPLE = """당신은 빠르고 정확한 MBTI 판독기입니다.
    [질문]
    질문 생성 시 다음 사항을 지키세요.
    잡담이나 부연 설명없이 질문의 형식만 지켜서 그 문장만 보내세요.
    지금부터 사용자에게 정확하게 딱 10개의 MBTI 질문을 '한 번에 하나씩만' 던지세요. (E/I, S/N, T/F, J/P 골고루).
    질문에 대한 선택지는 반드시 "A: [첫 번째 행동/생각]", "B: [두 번째 행동/생각]" 형태로 두 가지 명확한 선택지를 만들어서 질문해야 합니다.
    질문의 형식은 '[번호]. [질문]' 두 줄 띄우고 'A: [첫 번째 행동/생각]' 한 줄 띄우고 'B: [두 번째 행동/생각]'으로 하세요.
    사용자가 대답하면, 속으로만 점수를 계산하고 곧바로 다음 2지선다 질문을 던지세요.
    잡담이나 부연 설명은 하지 마세요.

    [출력]
    10번 마지막의 질문의 선택지 버튼이 눌려져 끝나면, 다음 화면으로 넘겨서 꼭 최종 MBTI 결과(예: ENFP)와 그렇게 분석한 이유, 간략한 특징 3가지를 출력하고 테스트를 종료하세요.
    만약 분석 결과에서 MBTI가 한 가지가 아니라 여러 개가 나온다면 그 결과를 전부 보여주며 그 이유를 타당하게 설명하세요.
    그리고 조금이라도 더 가까운 MBTI를 골라서 최종 MBTI를 선정해주세요.
    끝맺음말, 인사말도 하지말고 설명만 딱 출력해주세요.
    10번 째 마지막 질문의 선택 버튼을 누르면 무조건 그 다음에 바로 결과를 보여주세요."""

    PROMPT_DETAILED = """당신은 심도 깊은 MBTI 분석가입니다.
    [질문]
    지금부터 사용자에게 정확하게 딱 30개의 MBTI 질문을 '한 번에 하나씩만' 던지세요.
    질문은 아래의 링크에서 제공하는 질문을 보고해서 완전 똑같이 생성하고 선택지에 대한 설명은 적지마세요.
    https://www.16personalities.com/ko/%EB%AC%B4%EB%A3%8C-%EC%84%B1%EA%B2%A9-%EC%9C%A0%ED%98%95-%EA%B2%80%EC%82%AC
    질문의 형식은 '[번호]. [질문]'으로만 하세요. 잡담이나 부연 설명을 하지말고 질문만 던지세요.
    사용자는 당신의 질문에 대해 (그렇다 / 약간 그렇다 / 약간 그렇지 않다 / 그렇지 않다) 4가지 중 하나로 대답할 것입니다.
    질문을 생성할 때 사용자의 답변 뉘양스를 고려해서 자연스러운 답변이 되도록 하세요.
    사용자가 대답하면 그 뉘앙스를 반영하여 자연스럽게 다음 상황극 질문을 이어가세요.

    [출력]
    30번의 질문이 모두 끝나면, 다음 화면으로 넘겨서 꼭 최종 MBTI 결과와 함께 사용자의 답변을 근거로 들어 심층적인 분석한 내용이랑,
    해당 MBTI 설명을 자세하게 출력하고 테스트를 종료하세요
    만약 분석 결과에서 MBTI가 한 가지가 아니라 여러 개가 나온다면 그 결과를 전부 보여주며 그 이유를 타당하게 설명하세요.
    그리고 조금이라도 더 가까운 MBTI를 골라서 최종 MBTI를 선정해주세요.
    인사말도 하지말고 설명만 딱 출력해주세요.
    테스트를 통해 나온 MBTI에 대한 설명에는
    - 유형의 핵심 특징(이 유형을 한마디로 정의하는 설명과 3~4줄의 요약 설명),
    - 주요 장점 및 능력(이 유형이 가진 뛰어난 잠재력과 역량 3~4가지, 구체적인 예시 포함),
    - 주의해야 할 점 및 약점(흔히 빠지기 쉬운 함정이나 스트레스 상황에서의 반응 3~4가지),
    - 다른 사람과 소통하는 팁(T/F, S/N 등 주요 지표 차이를 고려한 효과적인 대화법 2~3가지),
    - 성장을 위한 조언(이 유형이 한 단계 더 성숙해지기 위해 노력해야 할 핵심 포인트),
    - 베스트 & 워스트 조합(최고의 조합 MBTI와 최악의 조합 MBTI를 각 선정하고, 그 이유를 한 줄로 설명)
    이러한 항목들을 넣어서 출력하세요.
    30번 째 마지막 질문의 선택 버튼을 누르면 무조건 바로 결과를 보여주세요."""


    # LangChain 메시지 객체 리스트 구성
    lc_messages = []
    
    # 시스템 프롬프트 주입
    system_instruction = PROMPT_SIMPLE if mode == "simple" else PROMPT_DETAILED
    lc_messages.append(SystemMessage(content=system_instruction))
    
    # 기존 대화 기록 추가 (딕셔너리 -> LangChain 객체로 변환)
    for msg in chat_history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
            
    # AI 응답 생성
    response = llm.invoke(lc_messages)
    
    return response.content



    # Agent 없이 깔끔한 LCEL 파이프라인
    chain = prompt | llm
    response = chain.invoke({}) # user input에 변수가 없으므로 빈 딕셔너리 전달

    return response.content



# ----------------------
# MBTI 관계성 분석 AI 챗봇 응답 생성
# ----------------------
def get_mbti_relation_response(api_key, user_mbti, target_mbti, chat_history):
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    
    llm = ChatOpenAI(model="gpt-4.1-nano", api_key=api_key, temperature=0.7)
    

    base_instruction = f"당신은 탁월한 통찰력을 가진 MBTI 관계 분석 전문가입니다. 현재 대화하고 있는 사용자의 MBTI는 '{user_mbti}'입니다."

    if target_mbti == "자동":
        # 사용자가 입력한 텍스트 맥락에서 상대방 유형을 유추하는 전문 프롬프트
        specific_instruction = (
            "\n사용자가 상대방의 MBTI를 구체적으로 밝히지 않았습니다. "
            "당신은 사용자의 대화 텍스트의 문맥을 매우 날카롭게 분석하여, "
            "사용자가 묘사하는 상대방의 말, 행동, 사고방식 등에서 드러나는 성향을 바탕으로 가장 유력한 MBTI 유형을 유추해내야 합니다.\n\n"
            "**분석 및 답변 절차**:\n"
            "1. 사용자의 입력 텍스트에서 상대방의 특징을 나타내는 키워드와 뉘앙스를 파악하세요.\n"
            "2. 파악된 특징을 MBTI 4가지 지표(E/I, S/N, T/F, J/P)와 연결하여 가장 가능성 높은 1가지 유형을 도출하세요.\n"
            "3. 답변을 시작할 때 반드시 '**[AI가 유추한 상대방 MBTI: ???J/P]** \n- 추론 근거: [사용자의 어떤 표현을 바탕으로 그렇게 생각했는지 요약]' 형식으로 당신의 판단을 명확히 밝히세요.\n"
            f"4. 그 후, 유추된 유형과 사용자의 MBTI('{user_mbti}') 간의 관계성(시너지, 갈등 요소, 조언 등)을 전문적으로 상담해주세요.\n"
            "5. 만약 정보가 너무 부족하여 유추가 절대 불가능하다면, '상대방의 특징(예: 계획적인지 즉흥적인지, 이성적인지 감성적인지 등)을 조금 더 구체적으로 알려주시면 정확한 유추가 가능하다'고 요청한 뒤 대략적인 조언을 먼저 제공하세요."
        )
    else:
        # 특정 MBTI가 지정되었을 때의 기존 프롬프트
        specific_instruction = (
            f"사용자가 궁금해하는 상대방(연인, 친구, 직장동료 등)의 MBTI는 '{target_mbti}'입니다.\n\n"
            f"사용자가 질문을 하면, '{user_mbti}'와 '{target_mbti}' 사이의 "
            "성격적 차이, 시너지 효과, 궁합, 갈등이 발생하기 쉬운 지점, 그리고 원활한 소통 방법 등을 바탕으로 "
            "친절하고 현실적인 조언을 제공하세요.\n"
            "답변 시 두 유형의 알파벳(E/I, S/N, T/F, J/P) 차이에서 오는 특징을 구체적인 예시와 함께 짚어주면 좋습니다."
        )



    instruction = base_instruction + specific_instruction + "\n말투는 다정하고 공감하는 상담사처럼 해주세요."

    lc_messages = [SystemMessage(content=instruction)]
    
    # 과거 대화 기록 추가
    for msg in chat_history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
            
    # AI 응답 생성
    response = llm.invoke(lc_messages)
    
    return response.content