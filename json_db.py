import json
from pathlib import Path

DB_FILE = Path("chat_history.json")

# 기본 저장 구조를 반환하는 함수
def get_default_data():
    return {
        "conversation_id" : None,
        "nick_name" : "방문객",
        "my_mbti" : None,
        "messages" : [],
        "relation_messages" : []
    }

# JSON 파일 초기화 함수
def init_db():

    # DB_FILE(chat_history.json)이 존재하지 않으면 새 JSON 파일을 생성함
    if not DB_FILE.exists():

        DB_FILE.write_text(
            json.dumps(get_default_data(), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

# 전체 JSON 데이터 불러오기 함수
def load_data():

    init_db()

    # JSON 파일 내용을 문자열로 읽기
    text = DB_FILE.read_text(encoding="utf-8")
    data = json.loads(text)

    if "conversation_id" not in data:
        data["conversation_id"] = None

    if "messages" not in data:
        data["messages"] = []

    if "relation_messages" not in data:
        data["relation_messages"] = []

    return data


# 전체 JSON 데이터 저장 함수
def save_data(data):
    DB_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

# 전체 메시지 불러오기 함수
def load_messages():
    data = load_data()
    return data["messages"]


# 메세지 1개 저장 함수
def save_messages(role, content, persona="기본"):
    data = load_data()
    data["messages"].append({
        "role" : role,
        "content" : content,
        "persona" : persona
    })
    save_data(data)

# conversation_id 저장 함수
def save_conversation_id(conversation_id):
    data = load_data()
    data["conversation_id"] = conversation_id
    save_data(data)

# conversation_id 불러오기 함수
def load_conversation_id():
    data = load_data()
    return data["conversation_id"]


# 전체 대화 삭제 함수
def clear_messages():
    data = load_data()

    # conversation_id는 유지하고 messages만 초기화
    data["messages"] = []

    save_data(data)



# ----------------------------
# 관계 상담 챗봇용 JSON
# ----------------------------
def load_relation_messages():
    data = load_data()
    return data["relation_messages"]

def save_relation_messages(role, content):
    data = load_data()
    data["relation_messages"].append({
        "role" : role,
        "content" : content
    })
    save_data(data)

def clear_relation_messages():
    data = load_data()
    data["relation_messages"] = []
    save_data(data)