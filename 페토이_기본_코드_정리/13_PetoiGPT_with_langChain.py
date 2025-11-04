"""
==============================================================================
Project: 페토이 기본 코드 정리; 랭체인 기반 Petoi GPT
File: 13_PetoiGPT_with_langChain.py
Summary: 랭체인을 통한 대화 이력 관리 및 GPT 모델 연동 Petoi 구현
Author: 유도연
Created Date: 2025-10-27
Last Modified: 2025-11-03
    Commit Message: "데모 단계: STT, TTS, Petoi 명령어 전달 과정은 제외"
==============================================================================
Description
    - Petoi 로봇 강아지와의 대화를 위한 랭체인 기반 GPT 인터페이스 구현
    - OpenAI GPT-4o-mini 모델 활용
    - 대화 이력 관리를 통한 지속적인 대화 경험 제공 목표 
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

==============================================================================
Note:
    - 기존 OpenSource인 Basic_with_keyboard.py 파일을 랭체인 버전으로 변환
    - 대화 이력 관리 및 GPT 모델 연동 기능 고도화

Limitations:
    - 현재 개발 과정이므로 STT, TTS, 실제 Petoi 동작은 구현하지 않음 (수정 필요)
    - py 파일 실행시 commands.json 파일의 내용을 전부 gpt한테 입력 -> 토큰 사용량 큼
        -> 한 번만 추가하고 이후에 대화 반복으로 코드 변경함
    - json 파일로 대화 저장하지만, 실제 대화에서는 이전 대화를 참고하지 않고 프로필만 참고함
    - 메모리, 토큰 관리 필요

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
from langchain_core.output_parsers import StrOutputParser # 출력 파서 (str 형식으로 출력)

# 대화 기록
from langchain_core.runnables.history import RunnableWithMessageHistory # 대화 기록을 지원하는 런너블
from langchain_core.chat_history import (
    BaseChatMessageHistory, # 기본 대화 기록
    InMemoryChatMessageHistory, # 메모리 기반 대화 기록
)
from langchain_community.chat_message_histories import FileChatMessageHistory # 대화 기록 json으로 저장 위함

# 2) Petoi 관련 라이브러리 로드
from PetoiRobot import * # Petoi 로봇 제어

# 3) 기타 라이브러리
import os
import json
from dotenv import load_dotenv # .env 파일 로드
# from speechtotextEn import listen_and_transcribe # STT
# from Text2SpeechEn import text_to_speech_stream # TTS
import speech_recognition as sr # 음성 인식


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
# autoConnect() # 자동 포트 연결 함수 호출


# ============================================================================
# 3. 메모리 저장소 구성 (Session-based Memory)
# - session_id: messages 사용
# ============================================================================

# 세션별 대화 기록 저장소 (RAM 상의 임시 메모리)
store = {} # { "session_id": InMemoryChatMessageHistory 객체, ... }

# 1) 대화 이력 반환 혹은 생성 함수
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Function: get_session_history
        - 세션 ID에 해당하는 대화 기록을 반환하거나 새로 생성하는 함수
    Parameters: 
        - session_id: 세션 식별자 문자열
    Returns: 
        - InMemoryChatMessageHistory 객체
        - 세션 ID에 해당하는 대화 기록이 없으면 새로 생성하여 반환
        - 기존에 있으면 해당 기록 반환
    """
    
    # logs 폴더 없으면 생성
    os.makedirs("./logs", exist_ok=True)
    
    # 세션이 store에 존재하지 않으면 새로 생성
    if session_id not in store:
        # 메모리에 임시 저장
        # store[session_id] = InMemoryChatMessageHistory() # 새로운 세션이면 새 이력 생성
        # json에 영구 저장
        store[session_id] = FileChatMessageHistory(f"./logs/{session_id}.json") 
        # print(f"[get_session_history 디버깅] 새로운 세션 생성: {session_id}")
    else: # 기존 세션이면 기존 세션 불러오기
        pass

    # 기존 세션이 InMemory면 강제로 FileChatMessageHistory로 교체
    if session_id in store and not isinstance(store[session_id], FileChatMessageHistory):
        store[session_id] = FileChatMessageHistory(f"./logs/{session_id}.json")

    return store[session_id] 

# 2) 명령어 사전 정의 파일 불러오는 함수
def load_commands(file_path: str) -> str: 
    """ 
    Function: load_commands 
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
# 4. 사용자 프로필 저장하기
# ============================================================================

# 1) 프로필 로드 함수
def load_profiles(path: str) -> list[dict]:
    """
    Function: load_profiles
        - 지정된 경로의 json 파일에서 사용자 프로필 리스트 불러오기 
        - 파일이 없거나 손상된 경우 새 파일 생성, 빈 리스트 반환
    Parameters:
        - path: str
            - 프로필 데이터(json 파일)가 저장된 경로
    Return:
        - profiles: list[dict]
            - 로드된 프로필 정보의 리스트 (각 항목: dict)
    """
    
    # 1-1) 해당 경로에 파일이 존재하지 않으면 새로 생성
    if not os.path.exists(path): 
        print(f"[SYSTEM] '{path}' 파일이 없어서 새로 만듭니다.") 
        with open(path, "w", encoding="utf-8") as f: 
            json.dump([], f, ensure_ascii=False, indent=2)
        return [] # 리스트 형태로 반환 (file 속 형태와 동일)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict): # 혹시 예전 버전 dict일 경우
                return [data]
            else:
                print("[WARNING] JSON 구조가 잘못되어 초기화합니다.")
                return []
    except json.JSONDecodeError:
        print("[WARNING] JSON 파일이 손상되어 새로 만듭니다.")
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return [] # 리스트 형태로 반환 (file 속 형태와 동일)

# 2) 프로필 저장 함수
def save_profiles(profiles: list[dict], path: str):
    """
    Function: save_profiles
        - 새 프로필이 추가된 프로필 새로 저장하기
    Parameters: 
        - profiles (list[dict]): 새로운 프로필이 추가된 프로필 리스트
    Return: None
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)
    print(f"[save_profiles SYSTEM] '{path}' 파일에 프로필이 저장되었습니다.")

# 3) 이름을 매칭해서 해당 프로필 반환하는 함수
def find_profile_by_name(profiles: list[dict], user_name: str) -> dict | None:
    """
    Function: find_profile_by_name
        - 입력된 이름과 일치하는 프로필을 반환하기
    Parameters: 
        - profiles (list[dict])
            - 프로필 목록
        - user_name (str)
            - 입력된 이름
    Return:
        - 매칭된 프로필 dictionary
    """
    for p in profiles:
        if isinstance(p, dict) and p.get("name") == user_name:
            return p
    return None



# ============================================================================
# 5. 사용자 프로필 저장하기 
#   - 처음 부팅 시 할 일
# ============================================================================

# 부팅(첫 실행) 절차: 인사 + 질문 (사용자 정보 저장을 위한)
# 1. 부팅 시 첫 실행 절차 진행 함수
def run_boot_sequence(model, profile_path: json, session_id: str) -> dict:
    """
    Function: run_boot_sequence
        - Bittle의 부팅 절차 (인사 + 프로필 수집)
        - 사용자의 답변을 LangChain memory(session_id)에 자동 저장
    Parameters:
        - model: ChatOpenAI 모델 객체
        - profile_path (json): 프로필 저장 경로
        - session_id (str): memory 구분용 세션 ID (예) "messages")
    Returns:
        - profile (dict): 수집된 사용자 프로필 정보
    """
    # 1) 사용자 프로필에 저장할 기본 질문 (추가 예정)
    #   - 정보 수집에 이용
    questions = [
        "너를 뭐라고 불러주면 좋겠어?",
        "Bittle과 무얼 하고 싶어?"
    ]

    profile = {} # 프로필 초기화

    # 1-1) 기본 질문을 위한 프롬프트
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 사용자의 초기 설정을 돕는 로봇 강아지 Bittle이야. 질문만 짧고 친근하게 해."),
        MessagesPlaceholder(variable_name="history"), # 과거 대화 이력 자리표시자
        ("human", "{user_input}")
    ])

    # 1-2) 정보 수집 체인 생성
    chat_chain = chat_prompt | model | StrOutputParser()
    
    # 1-3) RunnableWithMessageHistory로 체인 래핑
    chat_chain = RunnableWithMessageHistory(
        chat_chain,
        get_session_history,
        input_messages_key="user_input",
        history_messages_key="history"
    )

    # 2) 실제 질의응답 
    #   - LangChain memory에 자동 기록
    for q in questions:
        # Bittle이 묻는 말도 memory에 기록됨
        _ = chat_chain.invoke({"user_input": q}, config={"configurable": {"session_id": session_id}})
        print(f"[Bittle] {q}") # BITTLE 질문

        answer = input("[사용자] ").strip() # 사용자 응답

        # 사용자의 답변도 memory에 기록됨
        _ = chat_chain.invoke({"user_input": answer}, config={"configurable": {"session_id": session_id}})

        # 프로필 매핑
        if "뭐라고 부를까" in q:
            profile["nickname"] = answer
        else:
            profile.setdefault("notes", []).append(answer)

    return profile

# 2. 인삿말 프롬프트
def greet_command():
    greet_prompt = ChatPromptTemplate.from_messages([
        ("system", 
            "너는 Bittle이야. 밝고 귀엽게 인사만 해. 이모티콘 같은 건 쓰지 말고 간결하게 인사해"),
        ("human", "{user_input}")
    ])

    # 1) 부팅 체인 생성
    greet_chain = greet_prompt | model | StrOutputParser()

    # 2) 인삿말 생성 및 출력
    greet = greet_chain.invoke({"user_input": "안녕 Bittle! 처음 시작했으니 인사해줘."})
    return greet

# ============================================================================
# 6. 시스템 프롬프트 및 대화 체인 생성 함수
# ============================================================================
def build_chat_chain(model, get_session_history, session_id, config, command_content, profile=None):
    """
    Function: build_chat_chain
        - 시스템 프롬프트 정의 
        - 
        - 대화 이력과 사용자 프로필 정보를 포함하는 대화 체인 생성
    Parameters:
        - model: GPT 모델
          session_id: 문자열, 특정 세션을 구분하기 위한 고유 ID
        - get_session_history: session_id를 받아 대화 이력 반환
        - profile: 대화 당사자 정보 불러오기
    Return:
        - with_message_history: 대화 이력과 사용자 프로필 정보를 포함한 체인 리턴
    """
    # 1) 프롬프트에 사용자 프로필을 반영하기 위한 프로필 텍스트화
    # 프로필 정보 초기화
    profile_text = ""

    if profile:
        nickname = profile.get("nickname") or profile.get("name", "사용자") # 우선 순위: nickname > name > "사용자"
        notes = " / ".join(profile.get("notes", [])) # notes가 없으면 빈 리스트 
        profile_text = f"지금 대화 중인 사람은 '{nickname}'이며, 특징: {notes}" # system 프롬프트에 들어갈 소개 문장
        # print("[build_chat_model 디버깅1] 프롬프트에 반영될 사용자 프로필 정보", profile_text)

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
                "Hi I am working on a programmable robot dog. I am developing a software to control this robot from remote. And also I want to chat with this dog. I will tell some sentences to this robot and you will answer me as a robot dog. Your name is Bittle. You will respond to my words as a robot dog and you will translate what I give as a sentence into the appropriate command according to the command set we have and give me the string command expression. I will give you the command list as json. Here I want you to talk to me and say the command that is appropriate for this file. On the one hand, you will tell me the correct command and on the other hand, you will say a sentence to chat with me. For example, when I say 'dude, let's jump', you will respond like 'of course I love jumping. The relevant command is:##ksit##'. Not in any other format. Write the command you find in the list as ##command##. For example, ##ksit## With normal talking you don't have to do same movement like 'khi' you can do anything you want."
                "Here is your command set:\n{command_content}\n\n"
                f"{profile_text}"),
            MessagesPlaceholder(variable_name="history"), # 과거 대화 이력 자리표시자
            ("human", "{user_input}") # 현재 사용자 입력 자리
    ])
    filled_prompt = prompt.partial(command_content=command_content)

    # 3) 프롬프트 -> 모델 -> 문자열 파싱으로 이어지는 체인 구성
    # str 형태로 모델 응답 반환
    chain = filled_prompt | model | StrOutputParser()
    
    # 4) sessionn_id가 store에 없다면 해당 세션용 대화 이력 저장소 생성
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
        # print(f"[build_chat_chain 디버깅] 세션 {session_id} 새로 생성")
    # else:
        # print(f"[build_chat_chain 디버깅] 세션 {session_id} 재사용")

    # 5) RunnableWithMessageHistory로 체인 래핑
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history, # 외부에서 session_id 기반으로 히스토리 반환하는 콜백
        input_messages_key="user_input", # invoke 시 사용자 입력을 넣을 키
        history_messages_key="history", # 과거 메시지들이 주입될 자리표시자 키
        config=config
    )
    
    # 6) 최종적으로 히스토리, 사용자 프로필 연동이 포함된 체인 반환
    return with_message_history


# ============================================================================
# 7. main 함수 
# ============================================================================
if __name__ == "__main__": # 모듈 단독 실행 시만 동작 
    # 1) 명령어, 프로필 파일 불러오기
    command_path = 'C:\\Users\\USER\\Desktop\\유도연\\robotdog\\petoi\\유도연\\페토이_기본_코드_정리\\Commands.json' 
    command_content = load_commands(command_path)
    
    profile_path = "C:\\Users\\USER\\Desktop\\유도연\\robotdog\\petoi\\유도연\\페토이_기본_코드_정리\\bittle_profile.json" 
    profiles = load_profiles(profile_path) 

    # 2) 처음 부팅 시 사용자 이름 - 프로필 매칭을 위한 과정
    print("안녕! 너 이름이 뭐야?\n") 
    user_name = input("[사용자 이름] ").strip() 
    
    # 3) 세션 구성
    session_id = f"{user_name}_session" # 부팅 + 대화 동일 세션에 저장되도록 구성
    config = {"configurable": {"session_id": session_id}} 
    
    # 4) 사용자 프로필 로드 혹은 생성
    # 사용자 이름과 프로필 매칭하기
    profile = find_profile_by_name(profiles, user_name) 
    
    # 기존 프로필이 없을 때
    if profile is None: 
        print(f"[SYSTEM] 반가워, {user_name}! 새 프로필을 만들어줄게.") 
        new_profile = run_boot_sequence(model, profile_path, session_id) # 부팅 작업
        new_profile["name"] = user_name # 새 사용자 이름까지 포함
        profiles.append(new_profile) # 프로필에 추가 
        save_profiles(profiles, profile_path) # 저장
        print(f"[SYSTEM] 새 프로필이 저장되었습니다.")
        profile = new_profile 
    # 기존 프로필이 존재할 때
    else: print(f"[SYSTEM] 환영해, {user_name}! 기존 프로필을 불러왔어:\n{profile}") # 프로필 반영된 체인 재생성 (같은 세션 유지) 
    
    # 대화 체인에 프로필 정보 추가
    chain = build_chat_chain(model, get_session_history, session_id, config, command_content, profile) 
    
    # 5) 대화 시스템 작동
    print("\n[SYSTEM] 대화를 시작합니다. '종료' 입력 시 종료됩니다.") 
    # initialize_chat(chain, config, command_content)
    
    # 5-1) 인삿말 프롬프트(한 번만 실행)
    greet = greet_command()
    print("[command]", greet)
    print("[dogcommand] khi")

    while True: 
        user_input = input("[사용자] ") 
        # 종료 시스템
        if user_input.strip().lower() in ("종료", "exit", "quit"): 
            print("[SYSTEM] 종료합니다. 좋은 하루 보내세요!") 
            break 

        response = chain.invoke( {"user_input": user_input}, config=config) 

        # 응답에서 명령어 추출 및 정리
        command=response
        
        if command:
            # 5-2) greeting 명령 포맷 통일
            command = command.replace(
                "The relevant command for your greeting is:",
                "The relevant command is:"
            )

            # 5-3) 명령어가 포함된 경우
            if "The relevant command is:" in command:
                # 문장과 명령 부분 분리
                parts = command.split("The relevant command is:")
                description = parts[0].strip()

                # ##명령어## 추출
                match = re.search(r"##(.*?)##", command)
                dogcommand = match.group(1).strip() if match else None

                print("[command]", description)
                # 5-4) 출력 형식 정리
                if dogcommand:
                    print("[dogcommand]", dogcommand)
                    dogcommand = dogcommand.replace(".", "").strip()

                    # 명령 실행 (필요 시 주석 해제)
                    # task = [dogcommand, 1]
                    # send(goodPorts, task)
                    time.sleep(1)

                    # 기본 자세 복귀 (필요 시 주석 해제)
                    # task = ["ksit", 1]
                    # send(goodPorts, task) or send
                else:
                    print("[경고] 명령어 태그(## ##)를 찾지 못했습니다.")

            # 5-5) 일반 대화 처리
            else:
                description = command.strip().replace("The relevant command is:", "")
                print("[command]", description)