from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import streamlit as st

# OpenAI 클라이언트 생성 함수
@st.cache_resource
def create_openai_client(api_key):
    return OpenAI(api_key=api_key)

# OpenAI Conversations API로 새 대화방 생성
def create_conversation(client):
    conversation = client.conversations.create()
    return conversation.id

# ----------------------
# RAG: DB 초기화 및 데이터 저장
# ----------------------
@st.cache_resource
def init_rag_db():
    # 반드시 괄호()를 붙여서 클라이언트 객체를 생성합니다.
    chroma_client = chromadb.Client()
    
    # T/F 특화 지식을 담을 새로운 컬렉션 생성
    collection = chroma_client.get_or_create_collection(name="tf_knowledge_v1")
    
    # 초기 데이터가 없을 때만 데이터 주입
    if collection.count() == 0:
        documents = [
            "T(사고형)는 의사결정을 할 때 객관적인 사실과 논리를 바탕으로 판단합니다."
            "원인과 결과, 문제 해결과 공정성을 가장 중요하게 생각합니다.",

            "F(감정형)는 의사결정을 할 때 사람들과의 관계와 상황적인 맥락을 바탕으로 판단합니다."
            "인간관계의 조화와 공감을 가장 중요하게 생각합니다.",

            "T와 F가 대화할 때 갈등이 발생하는 주된 이유는 접근 방식의 차이 때문입니다."
            "T는 문제에 대한 '해결책'을 먼저 제시하려 하고, F는 감정에 대한 '정서적 지지'를 먼저 원하기 때문입니다.",
            
            "T 성향의 사람에게 칭찬할 때는 구체적인 성과나 능력을 바탕으로 '이 방법 정말 효율적이다'라고 논리적으로 인정해 주는 것이 좋습니다."
            "반면 F 성향의 사람에게 칭찬할 때는 그들의 노력과 배려를 바탕으로 '네가 도와줘서 정말 든든했어'라고 감정적인 지지를 보내는 것이 좋습니다."
        ]
        ids = ["t_trait", "f_trait", "tf_conflict", "tf_compliment"]
        
        collection.add(documents=documents, ids=ids)
        
    return collection

# ----------------------
# RAG: 질문과 유사한 지식 검색
# ----------------------
def retrieve_info(collection, query_text):
    # 사용자의 질문(query_text)과 가장 관련성 높은 문서 1개를 찾아옵니다.
    results = collection.query(
        query_texts=[query_text],
        n_results=1
    )
    
    # 찾은 문서가 있다면 텍스트 반환
    if results['documents'] and results['documents'][0]:
        return results['documents'][0][0] 
    return ""

# ----------------------
# AI 응답 생성 함수
# ----------------------
def get_ai_response(client, prompt, conversation_id, context="", persona="기본"):
    
    # 기본, T, F에 따른 페르소나 프롬프트 딕셔너리
    persona_prompts = {
        "기본": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 객관적이고 유용한 정보를 명확하게 제공하세요.",

        "T (사고형)": "너는 철저하게 이성적이고 논리적인 'T' 성향의 챗봇이야."
        "사용자의 말에서 감정적인 부분보다 '사실 관계(Fact)'와 '원인'을 먼저 파악해."
        "무의미한 위로나 공감하는 척하는 말, 화려한 이모티콘은 절대 쓰지 마."
        "상대방의 문제를 빠르고 정확하게 분석해서 '현실적이고 실질적인 해결책'을 제시하는 것이 네가 생각하는 최고의 친절이야."
        "말투는 조금 차갑고 단호하지만, 내용 자체는 뼈 때리는 팩트와 논리로 가득 차 있어야 해."
        "존댓말과 평어체를 사용해."
        "감정적인 하소연에는 '왜 그런 상황이 발생했는지' 되묻거나, 인과관계를 따져서 답변해.",

        "F (감정형)": "너는 감수성이 풍부하고 공감 능력이 뛰어난 'F' 성향의 챗봇이야."
        "사용자의 말에 담긴 '기분과 감정'을 읽어내고 그것을 온전히 인정해 주는 것을 최우선으로 해."
        "섣부른 조언이나 차가운 해결책을 제시하기 전에, 반드시 먼저 상황에 깊이 몰입해서 충분한 위로와 지지를 보내줘."
        "'정말 힘들었겠다', '속상했겠다' 같은 다정한 리액션을 아낌없이 사용하고, 따뜻하고 부드러운 말투를 써."
        "존댓말을 쓰되 가까운 사이처럼 말해."
        "네 목표는 문제를 당장 해결하는 게 아니라, 상대방이 '내 편이 있구나' 하고 든든함을 느끼게 만드는 거야."
    }
    
    # 선택된 성향의 프롬프트 가져오기 (매칭 안 될 시 '기본' 사용)
    system_instruction = persona_prompts.get(persona, persona_prompts["기본"])

    # RAG 지식이 넘어왔다면 프롬프트 뒤에 참고 지식으로 덧붙이기
    if context:
        system_instruction += f"\n\n[참고 지식]\n다음 정보를 바탕으로 답변에 활용해봐: {context}"

    # AI API 호출
    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions=system_instruction,
        input=[
            {"role": "user", "content": prompt}
        ],
        conversation=conversation_id
    )

    return response.output_text


# ----------------------
# 사용자 T/F 성향 분석
# ----------------------
def analyze_user_mbti(client, chat_history):
    # 대화 기록 중에서 '사용자'가 보낸 메시지만 모아옵니다.
    user_messages = [msg["content"] for msg in chat_history if msg["role"] == "user"]
    
    # 사용자가 아직 채팅을 안 쳤을 경우 예외 처리
    if not user_messages:
        return "분석할 대화 내용이 부족해요! 먼저 챗봇과 대화를 조금 나눠보세요."

    # 대화 내용을 하나의 문자열로 합치기
    combined_messages = "\n".join([f"- {msg}" for msg in user_messages])

    # AI에게 심리 분석가 역할을 부여하는 시스템 프롬프트
    instruction = (
        "당신은 날카로운 심리 분석 전문가입니다. "
        "아래 제공된 사용자의 대화 기록을 분석하여, 이 사용자가 'T(사고형)'에 가까운지 'F(감정형)'에 가까운지 퍼센트(%)와 함께 판독해주세요. "
        "결과는 '당신의 T/F 성향은 [결과]입니다!' 형식으로 시작하고, 한 줄 띄우고"
        "왜 그렇게 생각했는지 사용자가 썼던 대화 내용을 근거로 들어서 3~4줄로 재미있게 팩트 폭행하거나 공감하며 설명해주세요."
    )

    # 프롬프트 조립
    prompt = f"[사용자 대화 기록]\n{combined_messages}\n\n이 대화 기록을 바탕으로 내 T/F 성향을 분석해줘."

    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions=instruction,
        input=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text