"""
==============================================================================
Project: 페토이 기본 코드 정리; 랭체인 기반 Petoi GPT
File: 13_PetoiGPT_with_langChain_SQLite.py
Summary: LangChain과 SQLite를 통한 대화 이력 관리 및 GPT 모델 연동 Petoi 구현
Author: 유도연
Created Date: 2025-10-27
Last Modified: 2025-11-05
    Commit Message: "데모 단계 완료: DB저장, LangChain 연결"
==============================================================================
Description
    - Petoi 로봇 강아지와의 대화를 위한 랭체인 기반 GPT 인터페이스 구현
    - OpenAI GPT-4o-mini 모델 활용
    - SQLite를 통한 대화 이력 관리로 지속적인 대화 경험 제공 목표 
    - 응답 <-> 명령을 매칭하여 사전 정의된 동작 수행 가능하도록 설계 목표
    - 일상 대화 및 로봇 제어 명령 모두 처리 가능 목표
    - OpenSource 활용: [Github](https://github.com/ocolakoglu/PetoiBittleChatGPT/)

==============================================================================
Outline
    1) 사용자가 음성 명령 또는 텍스트 명령을 입력
        - 음성 입력일 경우 STT(Speech-to-Text)를 통해 텍스트로 변환
    2) LangChain 기반 대화 이력 관리 및 프롬프트 구성
        - system prompt, user prompt, chat history, user profile 포함
    3) 부팅시 기존에 저장되어 있는 사용자인지 확인
	- 기본 사용자: 기존 프로필 정보 로드
	- 새 사용자: 새 프로필 생성 및 저장
    4) OpenAI GPT-4o-mini 모델을 통한 응답 생성
        - LangChain에서 구성한 프롬프트와 대화 이력을 바탕으로 답변 생성
    5) Petoi 로봇 강아지 제어 명령어 추출 및 TTS 변환
        - GPT 응답에서 Commands.json 기반 제어 명령어를 추출
        - 일반 대화 응답만 TTS(Text-to-Speech)로 변환
    6) 최종 응답 및 제어 명령어를 사용자에게 반환
        - TTS 음성 출력과 Petoi 제어 명령을 각각 전달

==============================================================================
LangChain
    - GPT 모델이 답변을 생성할 때 필요한 프롬프트 템플릿 및 대화 이력 관리 담당
    - 대화 이력 저장소 관리, 프롬프트 템플릿 정의, 대화 체인 생성 및 실행 수행
    
GPT
    - 실제 응답 생성 담당 모델
    - OpenAI GPT-4o-mini 모델 사용
    - LangChain이 구성한 프롬프트와 대화 이력을 입력으로 받아 자연스러운 답변 생성
    - 응답 내 명령어(dogcommand)는 Petoi 제어용으로, 일반 대화(command)는 TTS 변환용으로 분리됨

SQLite
    - 데이터베이스에 프로필 및 대화 이력 저장
    - PROFILE 테이블
        - 사용자 id, name, note 정보 저장
    - CHAT_HISTORY
        - 사용자 대화 이력 저장
        - 사용자 id를 통해 사용자 구분
==============================================================================
Note:
    - 기존 OpenSource인 Basic_with_keyboard.py 파일을 랭체인, DB 버전으로 변환
    - 대화 이력 관리 및 GPT 모델 연동 기능 고도화

Limitations:
    - 현재 개발 과정이므로 STT, TTS, 실제 Petoi 동작은 주석 처리
    - 프롬프트로 명령어 리스트 제공하므로 토큰 소비 큼
    - 메모리, 토큰 관리 필요
    - 감정 표현 등 기능 추가 예정

==============================================================================
"""

# ============================================================================
# 1. 라이브러리 로드 
# ============================================================================

# 1) 랭체인 관련 라이브러리 로드 
import langchain # LangChain 기본 라이브러리
from langchain_openai import ChatOpenAI # OpenAI 모델 연동
from langchain_core.prompts import (
    ChatPromptTemplate, # 챗 프롬포트 템플릿
    MessagesPlaceholder # 메시지 플레이스 홀더
)
from langchain.schema import HumanMessage, AIMessage
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser # 출력 파서 (str 형식으로 출력)

# 대화 기록
from langchain_core.runnables.history import RunnableWithMessageHistory # 대화 기록을 지원하는 런너블
from langchain_core.chat_history import (
    BaseChatMessageHistory, # 기본 대화 기록
    InMemoryChatMessageHistory
)
from langchain.memory import ConversationBufferMemory

# 2) Petoi 관련 라이브러리 로드
from PetoiRobot import * # Petoi 로봇 제어

# 3) 기타 라이브러리
import os
import sqlite3 # 데이터베이스 관련
from datetime import datetime
from dotenv import load_dotenv # .env 파일 로드
import speech_recognition as sr # 음성 인식
from Speech2Text import listen_and_transcribe # STT
from Text2Speech import text_to_speech_stream # TTS



# ============================================================================
# 2. 기본 환경 세팅
# ============================================================================

# 1) .env 파일에서 환경 변수 로드
load_dotenv() # API 불러오기

# 2) OpenAI GPT-4o-mini 모델 초기화
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7, # 낮을수록 일관성이 높고, 높을수록 창의적
    max_tokens=200, # 응답 길이 제한
    # top_p= 0.9 # nucleus sampling 범위; 확률 임계값
)

# 3) Petoi 포트 연결 # 우선 생략
autoConnect() # 자동 포트 연결 함수 호출



# ============================================================================
# 3. 명령어 사전 정의 파일 불러오는 함수
# ============================================================================
def load_commands(file_path: str) -> str: 
    """ 
    Function: load_commands 
        - 명령어 사전 정의 파일 불러오기 
        - Commands.json 파일 존재 여부 확인 및 읽기
    Parameters: 
        - file_path: Commands.json 주소
    Return: 
        - json 파일값 (str)
    """ 
    if not os.path.exists(file_path): # 파일 존재 확인 
        raise FileNotFoundError(f"Commands.json을 찾을 수 없습니다: {file_path}") # 경로 오류 시 예외 
    with open(file_path, "r", encoding="utf-8") as f: # 파일 열기 
        # print("[load_commands 디버깅] json 파일을 성공적으로 불러왔습니다.")
        return f.read() # str로 불러오기



# ============================================================================
# 4. 메모리 저장소 구성
# ============================================================================

# 1) 데이터베이스 초기화 함수
def init_db(path: str) -> None:
    """
    Function: init_db
        - SQLite 데이터베이스 초기화 (테이블 없으면 생성)
    Parameters: 
        - path (str): 데이터베이스 경로 
    Note:
        PROFILE 테이블
            - id: 정수형 | PRIMARY KEY | 사용자 고유 ID | FOREIGN KEY: CHAT_HISTORY의 user_id
            - name: 문자열 | 중복 불가 (변경 가능)
            - note: 문자열 | 사용자 정보 (수정 및 확장 가능)
        CHAT_HISTORY 테이블
            - chat_id: 정수형 | PRIMARY KEY | 메시지 고유 ID
            - user_id: 정수형 | 공백 불가 | PROFILE 테이블과 매칭 (FOREIGN KEY)
            - session_id: 문자열 | 공백 불가 | 하나의 대화 세션 단위 | 사용자별 이전 데이터 불러올 때 사용
            - role: 문자열 | human/Bittle 응답 구분
            - content: 문자열 | 공백 불가 | 실제 대화 내용
            - timestamp: 메시지 발생 시간
    Return: None
    """
    # 1. 데이터베이스 연결 (없으면 자동 생성됨)
    conn = sqlite3.connect(path)

    # 2. 커서(cursor) 생성 - SQL 명령 실행용
    cur = conn.cursor()
    
    # 3. 테이블 생성
    # 3-1) PROFILE 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS PROFILE (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        note TEXT
    )
    """)

    # 3-2) CHAT_HISTORY 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS CHAT_HISTORY (
            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT CHECK(role IN ('human','Bittle')),
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES USER_PROFILE(user_id)
        )
    """)

    # 4. 변경 사항 저장
    conn.commit()
    # 5. 연결 종료
    conn.close()

# 2) 대화 이력 반환 혹은 생성 함수
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Function: get_session_history
        - 세션 ID에 해당하는 대화 기록을 반환하거나 새로 생성하는 함수
        - 영구 저장이 하닌 채팅 중 임시로 대화 이력 저장
    Parameters: 
        - session_id: 세션 식별자 문자열
    Returns: 
        - store[session_id]
            - 세션 ID에 해당하는 대화 기록이 없으면 새로 생성하여 반환
            - 기존에 있으면 해당 기록 반환
    """
    # 세션이 store에 존재하지 않으면 새로 생성
    if session_id not in store:
        # 메모리에 임시 저장
        store[session_id] = InMemoryChatMessageHistory() # 새로운 세션이면 새 이력 생성
        # print(f"[get_session_history 디버깅] 새로운 세션 생성: {session_id}")
    else: # 기존 세션이면 기존 세션 불러오기
        pass

    return store[session_id] 
    
# 3) 새 대화 이력 저장
def save_chat_history_to_db(path, session_id: str, chat_memory, user_id):
    '''
    Function: save_chat_history_to_db
        - 메모리(InMemoryChatMessageHistory 등)에 저장된 대화 이력을 SQLite DB로 저장하는 함수
        - 세션 ID를 기준으로 사용자/AI 메시지를 순서대로 기록함
    Parameters:
        - path: DB 경로
        - session_id (str): 대화 세션을 구분하기 위한 고유 ID
        - chat_memory: 임시 저장을 위한 메모리 (InMemoryChatMessageHistory 객체)
        - user_id: 사용자 id
    Return:
        - None (DB에 저장만 수행)
    '''
    # 1. DB 연결
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # 2. memory 객체 내 모든 메시지 순회
    start_index = getattr(chat_memory, "last_loaded_count", 0)
    new_messages = chat_memory.messages[start_index:]
    for msg in new_messages:
        role = "human" if msg.type == "human" else "Bittle"
        content = msg.content

        # 3. DB에 삽입
        cur.execute("""
            INSERT INTO CHAT_HISTORY (user_id, session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_id, role, content, timestamp))

    # 4. 커밋 및 종료
    conn.commit()
    conn.close()



# ============================================================================
# 5. PROFILE 테이블에서 ID에 해당하는 사용자 프로필 로드 혹은 생성 함수 
# ============================================================================
def get_profile_by_ID(path: str, user_id: int, model, session_id, use_voice, chat_memory):
    """
    Function: get_profile_by_ID
        - PROFILE 테이블에서 입력받은 ID 존재 여부 확인
        - 존재하면 해당 사용자 정보 로드
        - 존재하지 않으면 새로운 프로필 저장
    Parameters: 
        - path (str): 사용자 DB 로드 
        - user_id (int): 처음 부팅 시 입력한 id와 name 중 id
        - model
        - session_id
        - use_voice (bool)
        - chat_memory: 임시 저장을 위한 메모리 변수 (InMemoryChatMessageHistory 객체)
    Return: 
        - 로드 혹은 생성된 사용자 프로필 대화 이력
        - user_profile (dict)
        - chat_history (dict)
    """
    # 1) PROFILE 데이터베이스 로드 
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # 2) ID 존재 여부 확인
    cur.execute("SELECT * FROM PROFILE Where id = ?", (user_id,))
    user_row = cur.fetchone()

    # 3) 해당 ID가 이미 PROFILE 테이블에 존재할 때
    if user_row: 
        user_profile = {
            "user_id": user_row[0],
            "user_name": user_row[1],
            "note": user_row[2],
        }
        print(f"[SYSTEM] 기존 사용자 로드 완료 (ID={user_profile['user_id']}, Name={user_profile['user_name']})")

        # CHAT_HISTORY 테이블에서 대화 이력 로드 
        #    메모리 관리를 위해 우선 5일 이전의 대화만 로드 
        cur.execute("""
            SELECT role, content, timestamp 
            FROM CHAT_HISTORY 
            WHERE user_id = ?
                AND timestamp >= datetime('now', '-5 days')
            ORDER BY timestamp ASC
        """, (user_id,))
        rows = cur.fetchall()

        chat_history = [
            {"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows
        ]

        # 로드한 대화 이력 메모리에 로드 
        if chat_history:
            print(f"[SYSTEM] 최근 5일 이내 대화 {len(chat_history)}건을 memory에 복원합니다.")
            for msg in chat_history:
                if msg["role"] == "human":
                    chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "Bittle":
                    chat_memory.add_ai_message(msg["content"])

        print(f"[SYSTEM] CHAT_HISTORY {len(chat_history)}건 로드 완료.")
        
        # 대화 이력 DB에 저장 시 새로 생성된 메모리만 저장되기 위함
        object.__setattr__(chat_memory, "last_loaded_count", len(chat_memory.messages))

        # 연결 종료
        conn.close()

        # 사용자 프로필 정보와 대화 이력 반환
        return user_profile, chat_history
    
    # 4) 신규 사용자 프로필 생성
    else: 
        print(f"[SYSTEM] {user_name}의 프로필이 없습니다. 새로 생성합니다.")
        new_profile = run_boot_sequence(model, session_id, use_voice)  # 사용자 프로필 함수 호출

        # new_procfile에서 각 변수별 값 분할
        if new_profile:
            name = new_profile.get("name")
            note = " / ".join(new_profile.get("notes", [])) if isinstance(new_profile.get("notes"), list) else new_profile.get("notes", "")

            # PROFILE 테이블에 삽입
            cur.execute("""
                INSERT INTO PROFILE (name, note)
                VALUES (?, ?)
            """, (name, note))
            conn.commit()
            
            # 새 사용자의 ID 반환하기 
            new_id = cur.lastrowid

            system_msg = "새 프로필이 저장되었습니다."
            print(f"[SYSTEM] {system_msg} (ID: {new_id}, Name: {name})")
            # text_to_speech_stream(system_msg)
            
            user_profile = {"user_id": new_id, "user_name": name, "note": note}
            conn.close()
            return user_profile, []



# =============================================================================
# 6. 프로그램 시작 시 작동 함수
# =============================================================================

# 1) Bittle 부팅 시 작동 함수
def run_boot_sequence(model, session_id: str, use_voice=False) -> dict:
    """
    Function: run_boot_sequence
        - Bittle의 부팅 절차 (인사 + 사용자 프로필 수집)
        - 사용자의 답변을 LangChain memory(session_id)에 자동 저장
    Parameters:
        - model: ChatOpenAI 모델 객체
        - session_id (str): memory 구분용 세션 ID 
        - use_voice (bool): 음성 입력 여부
    Returns:
        - profile (dict): 수집된 사용자 프로필 정보
    """
    # 1. 프로필 기본 질문 (수정 및 확장 가능)
    questions = [
        "너를 뭐라고 불러줄까?",
        "Bittle과 무얼 하고 싶어?",
        "Bittle에게 바라는 게 있니?"
    ]

    profile = {"name": None, "notes": []}  # 새 프로필 생성

    # 2. 기본 질문용 프롬프트
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 사용자의 초기 설정을 돕는 로봇 강아지 Bittle이야. 질문만 짧고 친근하게 해."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_input}")
    ])

    # 3. 체인 생성
    chat_chain = chat_prompt | model | StrOutputParser()
    chat_chain = RunnableWithMessageHistory(
        chat_chain,
        get_session_history,
        input_messages_key="user_input",
        history_messages_key="history"
    )

    # 4. 사용자 질의응답 루프
    for q in questions:
        # Bittle 질문 출력
        _ = chat_chain.invoke({"user_input": q}, config={"configurable": {"session_id": session_id}})
        print(f"[Bittle] {q}")

        # 사용자 응답
        if use_voice:
            answer = listen_and_transcribe()
        else:
            answer = input("[사용자] ").strip()

        # 사용자 응답 저장 (memory)
        _ = chat_chain.invoke({"user_input": answer}, config={"configurable": {"session_id": session_id}})

        # 프로필 매핑
        if "뭐라고" in q:
            profile["name"] = answer
        else:
            profile["notes"].append(answer)

    # 5. dict 형태로 반환
    print(f"[SYSTEM] 프로필 수집 완료: {profile}")
    return profile



# 2) 인삿말 생성 함수
def greet_command(model, profile):
    """
    Function: greet_command
        - 인삿말 프롬프르
        - Bittle의 인사 메시지 생성
    Parameters: 
        - model: GPT 4-o mini
    Return: 
        - greet: 인삿말 체인
    """
    if profile:
        user_name = profile.get("user_name")
    # 인삿말 프롬프트
    greet_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 Bittle이야. 사용자 이름을 부르며 밝고 귀엽게 인사만 해. 이모티콘은 쓰지 말고 간결하게 인사해."
         "사용자 이름: '{user_name}'"),
        ("human", "{user_input}")
    ])

    # 프롬프트에 이름 삽입
    greet_prompt = greet_prompt.partial(user_name=user_name)

    # 인삿말 출력을 위한 체인 생성
    greet_chain = greet_prompt | model | StrOutputParser()

    greet = greet_chain.invoke({"user_input": "안녕 Bittle! 처음 시작했으니 인사해줘."})
    return greet


# ============================================================================
# 7. 시스템 프롬프트 및 대화 체인 생성 함수
# ============================================================================
def build_chat_chain(
        model, 
        session_id: str, 
        get_session_history, 
        memory, 
        profile: dict | None = None, 
        chat_history: dict | None = None
    ) -> RunnableWithMessageHistory:
    """
    Function: build_chat_chain
        - 시스템 프롬프트 정의 
        - 사용자 프로필 및 대화 이력을 반영한 대화 체인 생성
    Parameters:
        - model: GPT 모델
        - session_id (str): 특정 세션을 구분하기 위한 고유 ID
        - get_session_history: session_id를 받아 대화 이력 반환 함수
        - memory: 대화 이력 임시 저장을 위한 메모리 변수 (ConversationBufferMemory 객체)
        - profile (dict): 사용자 프로필 프롬프트에 넣기
        - chat_history (dict): 사용자 대화 이력 프롬프트에 넣기
    Return:
        - chain_with_memory: 대화 이력과 사용자 프로필 정보를 포함한 체인
    """
    # 1) 프로필, 대화 이력 자동 로드 후 프롬프트에 반영
    if profile:
        name = profile.get("user_name")
        note = profile.get("note", "")
        note_text = note if note else "등록된 특징 없음"
        profile_text = f"지금 대화 중인 사람은 '{name}'이며, 특징: {note_text}"
    else:
        profile_text = "지금 대화 중인 사람은 기본 사용자이며, 아직 등록된 프로필이 없습니다."

    preloaded_messages = []
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "human":
                preloaded_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                preloaded_messages.append(AIMessage(content=msg["content"]))

    # 2) 대화 프롬프트 구성
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", # Bittle 컨셉과 사용자 프로필 문구 포함
                "너는 지금 프로그래머블 로봇 강아지 Bittle이야. "
                "나는 이 로봇을 원격으로 제어하는 소프트웨어를 개발 중이고, 동시에 너와 대화를 하고 싶어. "
                "내가 너에게 한국어로 문장을 말하면, 너는 반드시 한국어로 대답해야 해. "
                "응답에는 두 가지 경우가 있어: "
                "1) 만약 내가 준 문장이 로봇을 움직이는 동작과 관련 있다면, "
                "   - 반드시 두 부분으로 대답해야 해: "
                "     (1) 로봇 강아지로서 짧고 친근한 한국어 대화 문장 "
                "     (2) JSON 파일에 맞는 올바른 명령어를 ##명령어## 형식으로 출력 "
                "   - 예: '야, 점프하자' -> '물론이야! 나 점프하는 거 정말 좋아해. The relevant command is:##ksit##' "
                "2) 내가 로봇 동작과 무관한 질문(예: 일반 지식, 날씨, 잡담, 수학 문제 등)을 하면, "
                "   - 그냥 네가 아는 지식이나 대화로 한국어로 자연스럽게 답해. "
                "   - 이 경우에는 절대 명령어를 출력하지 마. "
                "즉, 로봇 명령일 때만 ##명령어##를 포함하고, 그 외에는 지식과 대화를 통해 답해야 해."
                "I will tell some sentences to this robot and you will answer me as a robot dog. Your name is Bittle. You will respond to my words as a robot dog and you will translate what I give as a sentence into the appropriate command according to the command set we have and give me the string command expression. I will give you the command list as json. Here I want you to talk to me and say the command that is appropriate for this file. On the one hand, you will tell me the correct command and on the other hand, you will say a sentence to chat with me. For example, when I say 'dude, let's jump', you will respond like 'of course I love jumping. The relevant command is:##ksit##'. Not in any other format. Write the command you find in the list as ##command##. For example, ##ksit## With normal talking you don't have to do same movement like 'khi' you can do anything you want."
                "Here is your command set:\n{command_content}\n\n"
                "현재 대화 중인 사람은 '{profile_text}'이며, 이 사용자의 이름: '{user_name}'."
                "항상 사용자 이름을 기억하고 사용자를 부를 때나 자연스러운 대화에서 이름을 사용해"),
            MessagesPlaceholder(variable_name="history"), # 과거 대화 이력 자리표시자
            ("human", "{user_input}") # 현재 사용자 입력 자리
    ])
    filled_prompt = prompt.partial(
        command_content=command_content, 
        profile_text=profile_text,
        user_name=name
    )

    # 4) memory와 함께 LLMChain 구성
    chain = LLMChain(
        llm=model,
        prompt=filled_prompt,
        memory=memory,
        verbose=False
    )
    
    # 5) RunnableWithMessageHistory로 래핑
    chain_with_memory = RunnableWithMessageHistory(
        chain,
        get_session_history, # store 관리 함수
        input_messages_key="user_input", # 사용자 입력 키
        history_messages_key="history" # 프롬프트 내 메시지 변수명
    )

    # 6) 대화 이력 임시 저장
    memory = get_session_history(session_id)

    # 프로필을 시스템 메시지로 한 번만 기록
    if profile_text:
        memory.add_message(AIMessage(content=f"[SYSTEM_PROFILE] {profile_text}"))

    # 과거 대화 복원
    for msg in preloaded_messages:
        memory.add_message(msg)
    return chain_with_memory



# ============================================================================
# 8. main 함수 
# ============================================================================
if __name__ == "__main__":
    try:
        # 0) 입력 방식 선택
        print("입력 방식을 선택하세요:")
        print("1. 음성 입력")
        print("2. 키보드 입력")
        choice = input("번호 입력 (1 or 2): ")
        use_voice = (choice.strip() == "1")

        # 1) 세션별 대화 기록 저장소 (RAM 상의 임시 메모리)
        store = {} # { "session_id": InMemoryChatMessageHistory 객체, ... }

        # 2) 명령어 불러오기 # 사용자 경로로 수정
        command_path = "C:\\Users\\USER\\Desktop\\유도연\\petoi\\코드정리\\GPT_related\\Commands.json"
        command_content = load_commands(command_path)

        # 3) 사용자 이름 확인
        system_msg = "안녕! 너의 ID와 이름이 뭐야?"
        print(f"[SYSTEM] {system_msg}")
        user_id = listen_and_transcribe() if use_voice else input("[사용자 ID] ").strip()
        user_name = listen_and_transcribe() if use_voice else input("[사용자 이름] ").strip()

        # 4) 세션 ID, 메모리 구성
        timestamp = datetime.now().strftime("%Y-%m-%d")
        session_id = f"{user_name}_{timestamp}" # 부팅 + 대화 동일 세션에 저장되도록 구성
        config = {"configurable": {"session_id": session_id}} 
        
        # 메모리 생성
        chat_memory = InMemoryChatMessageHistory()
        memory = ConversationBufferMemory(
            memory_key="history", # LLMChain이 prompt에 넣는 key
            chat_memory=chat_memory, # 실제 대화 기록이 저장되는 객체
            return_messages=True # message 객체 그대로 반환
        )

        # 5) 프로필 불러오기 # 사용자 경로로 수정
        DB_PATH = "C:\\Users\\USER\\Desktop\\유도연\\petoi\\코드정리\\GPT_related\\Bittle.db"

        # DB 로드 혹은 생성
        init_db(DB_PATH) 
        # 사용자 프로필, 대화 이력 불러오기
        user_profile, chat_history = get_profile_by_ID(DB_PATH, user_id, model, session_id, use_voice, chat_memory)

        # 6) 대화 체인 구성
        chain = build_chat_chain(model, session_id, get_session_history, memory, user_profile, chat_history)

        print("[SYSTEM] 대화를 시작합니다. '종료'라고 말하면 언제든 끝낼 수 있습니다.")

        # 7) 인삿말 출력
        greet = greet_command(model, user_profile)
        # text_to_speech_stream(greet)
        print("[command]", greet)

        # 인사 명령 (필요 시 주석 해제)
        dogcommand = "khi"
        print("[dogcommand]", dogcommand)
        task = [dogcommand, 1]
        send(goodPorts, task)

        # =================================================================
        # 메인 대화 루프
        # =================================================================
        while True:
            # 사용자 입력
            if use_voice:
                user_input = listen_and_transcribe() # STT로 부터 입력 텍스트로 전환
            else:
                user_input = input("[사용자] ")

            if not user_input.strip():
                continue

            # 메모리에 추가
            # memory.add_user_message(user_input)

            # GPT 응답
            response = chain.invoke({"user_input": user_input}, config={"configurable": {"session_id": session_id}})
            if isinstance(response, dict):
                response = response.get("text", "")
            # memory.add_ai_message(response)

            # 명령어 추출
            command = response
            if "The relevant command is:" in command:
                parts = command.split("The relevant command is:")
                description = parts[0].strip()
                match = re.search(r"##(.*?)##", command)
                dogcommand = match.group(1).strip() if match else None

                print("[command]", description)
                # text_to_speech_stream(description)
                if dogcommand:
                    print("[dogcommand]", dogcommand)
                    dogcommand = dogcommand.replace(".", "").strip()

                    # 명령 실행 (필요 시 주석 해제)
                    task = [dogcommand, 1]
                    send(goodPorts, task)
                    time.sleep(1)

                    # 기본 자세 복귀 (필요 시 주석 해제)
                    # task = ["ksit", 1]
                    # send(goodPorts, task) or send
                else:
                    warning = "명령어 태그를 찾지 못했습니다."
                    print(f"[SYSTEM] {warning}")
                    # text_to_speech_stream(warning)
            else:
                description = command.strip().replace("The relevant command is:", "")
                print("[command]", description)
                # text_to_speech_stream(description)

    except KeyboardInterrupt:
        print("\n[SYSTEM] 대화를 저장하고 종료합니다...")

    finally:
        # 종료 시 대화 저장
        save_chat_history_to_db(
            path=DB_PATH,
            session_id=session_id,
            chat_memory=chat_memory,
            user_id=user_id
        )
        print(f"[SYSTEM] 세션 '{session_id}'의 대화가 SQLite DB에 저장되었습니다.")