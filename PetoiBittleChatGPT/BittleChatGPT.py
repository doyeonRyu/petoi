# -*- coding: utf-8 -*-

# ==============================
# 설치 참고 (없으면 먼저 설치)
# pip install langchain-openai langchain-core python-dotenv SpeechRecognition pyserial
# Windows에서 마이크 사용 시 pyaudio 필요:
#   pip install pipwin && pipwin install pyaudio
# ==============================

import os                           # 환경변수 접근용
import sys                          # 시스템 관련 기능
import time                         # 지연(sleep) 사용
import re                           # 정규식 파싱
from pathlib import Path            # 경로 처리

# 외부 모듈: 사용자 제공 파일들
from speechtotextEn import listen_and_transcribe   # 음성 → 텍스트
from Text2SpeechEn import text_to_speech_stream     # 텍스트 → 음성
# from ardSerial import *                              # 직렬 포트 연결/전송
from PetoiRobot import *
# STT 라이브러리 (에러 핸들링 목적으로 import)
import speech_recognition as sr

# LangChain + OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import BaseMessage
from langchain_core.messages import SystemMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import AnyMessage
from langchain_core.messages import FunctionMessage
from langchain_core.messages import ChatMessage
from langchain_core.messages import RemoveMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# ==============================
# 환경 변수 로드 및 LLM 초기화
# ==============================
# 한 줄 주석: .env 파일에서 OPENAI_API_KEY 등을 불러옴
load_dotenv()

# 한 줄 주석: OpenAI LLM 모델 지정 (경량/저지연 목적)
model = ChatOpenAI(model="gpt-4o-mini")

# 한 줄 주석: 세션별 메모리를 담아둘 딕셔너리
store = {}

# 한 줄 주석: 직렬 통신 포트 사전 (ardSerial.connectPort 가 채움)
autoConnect() 


'''
함수 설명
- 세션별 대화 이력을 저장/조회하는 헬퍼 함수
입력값
- session_id: 문자열, 세션 식별자
출력값
- BaseChatMessageHistory 구현체 (여기서는 InMemoryChatMessageHistory)
'''
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    # 한 줄 주석: 세션 ID가 아직 없으면 메모리 기반 히스토리 생성
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    # 한 줄 주석: 세션 히스토리 객체 반환
    return store[session_id]


'''
함수 설명
- Commands.json 내용을 system 프롬프트에 고정하여 모델이 반드시 지정된 명령만 사용하도록 강제
입력값
- commands_json_str: 문자열, 명령 세트(JSON 문자열)
출력값
- ChatPromptTemplate 객체
'''
def build_prompt() -> ChatPromptTemplate:
    system_text = (
        "You are Bittle, a robot dog.\n"
        "User talks casually; you reply in a friendly short sentence PLUS one control command.\n"
        "Choose exactly one command from the given JSON command set.\n"
        "Output format MUST be exactly two parts in one line:\n"
        "1) a short chat reply to the user (any style)\n"
        "2) the command line: The relevant command is: ##<command_code>##\n"
        "Never output additional '#' or backticks. Never invent commands outside the set.\n"
        "Command set (JSON):\n"
        "```json\n{commands_json}\n```"
    )
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_text),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )


'''
함수 설명
- 모델 응답 문자열에서 설명 문장과 ##명령코드##를 튜플로 분리
입력값
- reply_text: 문자열, 모델이 생성한 원문
출력값
- (description, command) 튜플
  - description: 사용자에게 읽어줄 말풍선
  - command: 명령 코드(문자열) 또는 None(파싱 실패 시)
'''
def parse_model_reply(reply_text: str):
    # 한 줄 주석: 앞뒤 공백 제거
    text = (reply_text or "").strip()

    # 한 줄 주석: "The relevant command is:" 다음에 ##명령## 포맷을 찾는 정규식
    m = re.search(
        r"The\s+relevant\s+command\s+is:\s*##\s*([A-Za-z0-9_.-]+)\s*##",
        text,
        re.IGNORECASE
    )

    # 한 줄 주석: 명령이 매치되면
    if m:
        # 한 줄 주석: 그룹 1에 명령 코드가 들어있음
        cmd = m.group(1)
        # 한 줄 주석: 설명 부분은 명령 라인 앞쪽 텍스트로 간주
        desc = text[:m.start()].strip()
        # 한 줄 주석: 설명이 비어 있으면 기본 응답으로 대체
        if not desc:
            desc = "Okay!"
        # 한 줄 주석: (설명, 명령) 튜플 반환
        return desc, cmd

    # 한 줄 주석: 못 찾았으면 설명만 반환하고 명령은 None
    return text, None


'''
함수 설명
- 음성 인식 실패 시 키보드 입력으로 폴백하는 안전 입력 함수
입력값
- 없음
출력값
- 사용자가 최종적으로 입력한 문자열
  - "/exit" 입력 시 종료 신호 반환
'''
def safe_get_user_input():
    try:
        # 한 줄 주석: 바로 텍스트로 입력할 수 있는 기회를 먼저 제공
        print("\n[입력] 말해주세요. (그냥 Enter를 누르면 음성 입력 시도 후 키보드로 폴백)")
        pre = input("음성 대신 즉시 텍스트 입력하려면 여기에 입력(Enter=건너뛰기): ").strip()

        # 한 줄 주석: 사용자가 미리 텍스트를 입력했다면 그대로 사용
        if pre:
            if pre == "/exit":
                return "/exit"
            return pre

        # 한 줄 주석: 아무것도 안 치고 Enter면 음성 인식 시도
        try:
            text = listen_and_transcribe()
            if text:
                return text
            else:
                print("[폴백] 음성 인식 결과가 비었습니다.")
        except Exception as e:
            print(f"[폴백] 음성 입력 실패: {e}")

        # 한 줄 주석: 폴백으로 키보드 입력
        kb = input("You (keyboard): ").strip()
        if kb == "/exit":
            return "/exit"
        return kb

    except KeyboardInterrupt:
        # 한 줄 주석: Ctrl+C 시 안전 종료
        return "/exit"


'''
함수 설명
- 직렬 포트 연결을 초기화하고 성공/실패를 출력
입력값
- 없음 (전역 goodPorts 사용)
출력값
- bool: True(성공), False(실패)
'''
# def init_serial_ports() -> bool:
#     try:
#         # 한 줄 주석: ardSerial.connectPort(goodPorts) 호출로 연결 시도
#         connectPort(goodPorts)
#         # 한 줄 주석: 연결 후 상태 출력
#         print("[직렬] 연결 상태:", goodPorts)
#         # 한 줄 주석: 최소 한 개라도 연결됐는지 확인
#         return bool(goodPorts)
#     except Exception as e:
#         print(f"[오류] 직렬 포트 초기화 실패: {e}")
#         return False


'''
함수 설명
- 명령 코드와 지속시간을 받아 로봇에게 전송
입력값
- command_code: 문자열, Commands.json에 정의된 코드 (예: 'ksit', 'khi')
- duration: int, 동작 시간(초)
출력값
- bool: True(성공), False(실패)
'''
def send_robot_command(command_code: str, duration: int = 1) -> bool:
    try:
        if not command_code:
            print("[경고] 빈 명령입니다. 전송하지 않습니다.")
            return False
        sendSkillStr(command_code.strip(), int(duration))
        print(f"[전송됨] {command_code}, duration={duration}")
        sendSkillStr('krest', 1)  # 명령 후 자동으로 앉기
        return True
    except Exception as e:
        print(f"[오류] 명령 전송 실패: {e}")
        return False


'''
함수 설명
- 메인 대화 루프: 입력→모델 호출→파싱→TTS→직렬 전송까지의 전체 흐름 수행
입력값
- with_message_history: RunnableWithMessageHistory 체인
- config: dict, 세션 설정 (예: {"configurable": {"session_id": "firstChat"}})
- auto_sit_after: bool, 명령 후 자동으로 'ksit' 수행할지 여부
출력값
- 없음
'''
def main_loop(with_message_history: RunnableWithMessageHistory, config: dict, auto_sit_after: bool = False):
    # 한 줄 주석: 무한 루프 시작
    while True:
        # 한 줄 주석: 안전 입력 함수로 사용자 발화 획득(음성→키보드 폴백)
        user_input = safe_get_user_input()

        # 한 줄 주석: 종료 커맨드 처리
        if user_input == "/exit":
            print("[종료] 대화를 종료합니다.")
            break

        # 한 줄 주석: 공백 입력 방지
        if not user_input:
            print("[안내] 입력이 비어 있습니다. 다시 시도하세요.")
            continue

        # 한 줄 주석: LLM 호출
        # 3) main_loop 내부의 모델 호출
        response = with_message_history.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=session_cfg,
        )

        # 한 줄 주석: 원문 저장/출력 (디버깅에 유용)
        raw = response.content or ""
        print("\n[모델 원문]\n", raw)

        # 한 줄 주석: 응답 파싱 (설명 + 명령코드)
        description, dogcommand = parse_model_reply(raw)

        # 한 줄 주석: 설명 출력
        print("\n[설명]\n", description)

        # 한 줄 주석: TTS로 설명 음성 출력
        try:
            text_to_speech_stream(description)
            print("[TTS] 재생 완료")
        except Exception as e:
            print(f"[경고] TTS 실패: {e}")

        # 한 줄 주석: 명령이 있다면 로봇에게 전송
        if dogcommand:
            print(f"[전송] {dogcommand}, duration=1")
            ok = send_robot_command(dogcommand, duration=1)
            if ok and auto_sit_after:
                time.sleep(0.8)
                send_robot_command("ksit", duration=1)



# ==============================
# 진입부: 프롬프트/체인/직렬 초기화 후 루프 시작
# ==============================
if __name__ == "__main__":
    try:
        # 한 줄 주석: 직렬 포트 초기화
        # serial_ok = init_serial_ports()
        # if not serial_ok:
        #     print("[주의] 직렬 포트가 비어 있거나 연결 실패했습니다. 명령 전송은 스킵될 수 있습니다.")

        # 한 줄 주석: 명령셋 JSON 파일 경로 지정 (환경에 맞게 수정 가능)
        # 예시: E:\gachon\robotdog\petoi\OpenCat\OpenCat\PetoiBittleChatGPT\Commands.json
        commands_path = Path(r"C:\Users\USER\Desktop\유도연\robotdog\petoi\OpenCat\OpenCat\PetoiBittleChatGPT\Commands.json")

        # 한 줄 주석: 파일 존재 확인
        if not commands_path.exists():
            print(f"[오류] Commands.json 파일을 찾을 수 없습니다: {commands_path}")
            sys.exit(1)

        # 한 줄 주석: JSON 문자열 로드
        commands_json_str = commands_path.read_text(encoding="utf-8")

        # 한 줄 주석: 프롬프트 구성 (명령셋을 system에 고정)
        # 파일에서 읽은 commands_json_str가 있다고 가정
        prompt = build_prompt().partial(commands_json=commands_json_str)

        chain = prompt | model

        with_message_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="messages",
            history_messages_key="messages",
        )
        session_cfg = {"configurable": {"session_id": "firstChat"}}
        # 부팅 호출 시에도 dict 형태로
        boot_resp = with_message_history.invoke(
            {"messages": [HumanMessage(content="Hi buddy, tell me who you are in one sentence.")]},
            config=session_cfg,
        )

        boot_desc, boot_cmd = parse_model_reply(boot_resp.content or "")
        print("[부팅 응답]", boot_desc, "| cmd:", boot_cmd or "none")

        # 한 줄 주석: 메인 루프 시작 (명령 후 자동으로 앉히고 싶으면 True)
        main_loop(with_message_history, config, auto_sit_after=False)
    finally:
        closePort()