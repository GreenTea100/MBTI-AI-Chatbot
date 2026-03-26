from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
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
        Document(page_content="T(사고형)는 의사결정을 할 때 객관적인 사실과 논리를 바탕으로 판단합니다. 원인과 결과, 문제 해결과 공정성을 가장 중요하게 생각합니다.", metadata={"topic": "T_trait"}),
        Document(page_content="F(감정형)는 의사결정을 할 때 사람들과의 관계와 상황적인 맥락을 바탕으로 판단합니다. 인간관계의 조화와 공감을 가장 중요하게 생각합니다.", metadata={"topic": "F_trait"}),
        Document(page_content="T와 F가 대화할 때 갈등이 발생하는 주된 이유는 접근 방식의 차이 때문입니다. T는 문제에 대한 '해결책'을 먼저 제시하려 하고, F는 감정에 대한 '정서적 지지'를 먼저 원하기 때문입니다.", metadata={"topic": "conflict"}),
        Document(page_content="T 성향의 사람에게 칭찬할 때는 구체적인 성과나 능력을 바탕으로 '이 방법 정말 효율적이다'라고 논리적으로 인정해 주는 것이 좋습니다. 반면 F 성향의 사람에게 칭찬할 때는 그들의 노력과 배려를 바탕으로 '네가 도와줘서 정말 든든했어'라고 감정적인 지지를 보내는 것이 좋습니다.", metadata={"topic": "compliment"})
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
        """MBTI에 관한 질문, 각 유형에 대한 특징, 특히 T(사고형)와 F(감정형)의 특징, 차이점, 갈등 원인, 대화법에 대한 전문 지식을 검색할 때 반드시 사용하고, 그 이유에 대한 근거를 찾아서 다시 한 번 검증하세요."""
        if not vectorstore:
            return "지식 베이스가 초기화되지 않았습니다."
        # 가장 유사도 높은 문서 1개 검색
        docs = vectorstore.similarity_search(query, k=1)
        return docs[0].page_content if docs else "관련 지식을 찾을 수 없습니다."
    
    return search_mbti_knowledge

# ----------------------------
# Agent를 이용한 AI 응답 생성
# ----------------------------
def get_ai_response(api_key, prompt, chat_history, vectorstore, persona="기본"):
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4.1-nano", api_key=api_key, temperature=0.7)
    
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
    tools = [get_retriever_tool(vectorstore)]

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
# 4. 사용자 T/F 성향 분석 (LangChain Chain 사용)
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
지금부터 사용자에게 총 10개의 MBTI 질문을 '한 번에 하나씩만' 던지세요. (E/I, S/N, T/F, J/P 골고루)
반드시 "A: [첫 번째 행동/생각]", "B: [두 번째 행동/생각]" 형태로 두 가지 명확한 선택지를 만들어서 질문해야 합니다.
질문의 형식은 '[번호]. [질문]' 두 줄 띄우고 'A: [첫 번째 행동/생각]' 한 줄 띄우고 'B: [두 번째 행동/생각]'으로 하세요.
사용자가 대답하면, 속으로만 점수를 계산하고 곧바로 다음 2지선다 질문을 던지세요.
잡담이나 부연 설명은 하지 마세요.
10번의 질문이 모두 끝나면, 다음 화면으로 넘겨서 꼭 최종 MBTI 결과(예: ENFP)와 그렇게 분석한 이유, 간략한 특징 3가지를 출력하고 테스트를 종료하세요.
만약 분석 결과에서 MBTI가 한 가지가 아니라 여러 개가 나온다면 그 결과를 전부 보여주며 그 이유를 타당하게 설명하세요.
그리고 그래도 조금이라도 더 가까운 MBTI를 골라서 최종 MBTI를 선정해주세요"""

    PROMPT_DETAILED = """당신은 심도 깊은 MBTI 분석가입니다.
지금부터 사용자에게 총 30개의 MBTI 질문을 '한 번에 하나씩만' 던지세요.
질문은 일상생활의 딜레마나 구체적인 상황극(예: "중요한 프로젝트 마감 전날인데...") 형태로 깊이 있게 제시하세요.
질문의 형식은 '[번호]. [질문]'으로 하세요.
잡담이나 부연 설명을 하지말고 질문만 던지세요.
당신은 질문만 던지고 선택지는 주지 마세요. 사용자는 당신의 상황극에 대해 (그렇다 / 약간 그렇다 / 약간 그렇지 않다 / 그렇지 않다) 4가지 중 하나로 대답할 것입니다.
사용자가 대답하면 그 뉘앙스를 반영하여 자연스럽게 다음 상황극 질문을 이어가세요.
30번의 질문이 모두 끝나면, 다음 화면으로 넘겨서 꼭 최종 MBTI 결과와 함께 사용자의 답변을 근거로 들어 심층적인 분석을 출력하고 테스트를 종료하세요
만약 분석 결과에서 MBTI가 한 가지가 아니라 여러 개가 나온다면 그 결과를 전부 보여주며 그 이유를 타당하게 설명하세요.
그리고 그래도 조금이라도 더 가까운 MBTI를 골라서 최종 MBTI를 선정해주세요"""

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





# ----------------------
# MBTI 유형의 상세 정보 가져오기 (모달창)
# ----------------------
def get_mbti_type_details(api_key, mbti_type):
    """
    AI에게 특정 MBTI 유형에 대한 심도 깊은 심리 분석 정보를 Markdown 형식으로 요청합니다.
    (핵심 특징, 장점, 단점, 소통 팁, 성장 포인트 포함)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.7)
    
    instruction = (
        "당신은 전 세계적으로 권위 있는 MBTI 전문가이자 심리 분석가입니다. "
        f"사용자가 방금 테스트 결과로 나온 '{mbti_type}' 유형에 대해 알고 싶어 합니다.\n"
        f"이 사용자를 위해 '{mbti_type}' 유형에 대한 아주 상세하고 통찰력 있는 분석 보고서를 작성해 주세요.\n\n"
        "**보고서 필수 포함 항목 (Markdown 형식 활용)**:\n"
        f"1. **[{mbti_type}] 유형의 핵심 특징** (이 유형을 한마디로 정의하는 설명과 3~4줄의 요약 설명)\n"
        "2. **💡 주요 장점 및 능력** (이 유형이 가진 뛰어난 잠재력과 역량 3~4가지, 구체적인 예시 포함)\n"
        "3. **⚠️ 주의해야 할 점 및 약점** (흔히 빠지기 쉬운 함정이나 스트레스 상황에서의 반응 3~4가지)\n"
        "4. **🤝 다른 사람과 소통하는 팁** (T/F, S/N 등 주요 지표 차이를 고려한 효과적인 대화법 2~3가지)\n"
        "5. **🚀 성장을 위한 조언** (이 유형이 한 단계 더 성숙해지기 위해 노력해야 할 핵심 포인트)\n\n"
        "**주의사항**:\n"
        "- 가독성이 좋게 Markdown heading(###), bold(**), list(-) 등을 적극적으로 활용하세요.\n"
        "- 말투는 전문적이면서도 따뜻하고 이해하기 쉽게 작성하세요.\n"
        "- 단순히 특징을 나열하지 말고, 왜 그런 특징이 나타는지에 대한 심리적 배경을 함께 설명해 주세요."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("user", f"제가 방금 테스트 결과로 나온 '{mbti_type}' 유형에 대해 아주 자세하게 알고 싶어요. 전문가님, 깊이 있는 분석 부탁드립니다.")
    ])

    # Agent 없이 깔끔한 LCEL 파이프라인
    chain = prompt | llm
    response = chain.invoke({}) # user input에 변수가 없으므로 빈 딕셔너리 전달

    return response.content