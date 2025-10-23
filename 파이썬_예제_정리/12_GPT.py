"""
==============================================================================
Project: 파이썬 예제 정리

File: 12_GPT.py
Summary: GPT 작동 예제
Author: 유도연
Created Date: 2025-10-20
Last Modified: 2025-10-20

==============================================================================
Description
    - AI 비전 카메라 모듈을 통한 실시간 모니터링 python 코드 
    - 작성 중...

==============================================================================
Instruction
    - 동작 작동 함수:
        - 

==============================================================================
Note:
    - 

==============================================================================
"""

import sys
import time

from speechtotextEn import listen_and_transcribe
from Text2SpeechEn import text_to_speech_stream
from PetoiRobot import * # 기본 동작 정의 library

import speech_recognition as sr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import re

# ==============================================================================
# GPT 작동 예제

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI GPT-4o-mini 모델 초기화
model = ChatOpenAI(model="gpt-4o-mini")

store = {} # 세션별 대화 기록 저장소
goodPorts = {} # 연결된 포트 정보 저장
connectPort(goodPorts) # 포트 연결 함수 호출
#  autoconnect()

"""
Function: get_session_history
    - 세션별 대화 이력을 저장/조회하는 헬퍼 함수
Parameters:
    - session_id: 세션 식별자 문자열.
Returns:
    BaseChatMessageHistory 객체 (InMemoryChatMessageHistory 인스턴스)
"""
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory() # 새로운 세션이면 새 이력 생성
    return store[session_id] # 기존 세션이면 기존 이력 반환

# 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
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
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | model # 대화 체인 생성
config = {"configurable": {"session_id": "firstChat"}} # 세션 설정
with_message_history = RunnableWithMessageHistory(chain, get_session_history) # 메시지 이력과 함께 실행 가능한 래퍼 생성

# 초기 대화 설정
user_input="Hi I am working on a programmable robot dog. I am developing a software to control this robot from remote. And also I want to chat with this dog. I will tell some sentences to this robot and you will answer me as a robot dog. Your name is Bittle. You will respond to my words as a robot dog and you will translate what I give as a sentence into the appropriate command according to the command set we have and give me the string command expression. I will give you the command list as json. Here I want you to talk to me and say the command that is appropriate for this file. On the one hand, you will tell me the correct command and on the other hand, you will say a sentence to chat with me. For example, when I say 'dude, let's jump', you will respond like 'of course I love jumping. The relevant command is:##ksit##'. Not in any other format. Write the command you find in the list as ##command##. For example, ##ksit## With normal talking you don't have to do same movement like 'khi' you can do anything you want."
# 첫 사용자 입력에 대한 응답 생성
response = with_message_history.invoke(
    [HumanMessage(content=user_input)], # HumanMessage 객체로 사용자 입력 래핑
    config=config,
)
print(response.content)

# Commands.json
file_path = 'C:\\Users\\USER\\Desktop\\유도연\\robotdog\\petoi\\OpenCat\\OpenCat\\PetoiBittleChatGPT\\Commands.json'
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

# 두 번째 사용자 입력에 대한 응답 생성
user_input = "This is my dataset I mention." + file_content
response = with_message_history.invoke(
    [HumanMessage(content=user_input)],
    config=config,
)

# 세 번째 사용자 입력에 대한 응답 생성
user_input="Hi buddy, you welcome. Tell me about yourself shortly."
response = with_message_history.invoke(
    [HumanMessage(content=user_input)],
    config=config,
)

print(response.content) 

# 세 번째 응답에서 명령어 추출 및 정리
command=response.content
command=command.replace("The relevant command for your greeting is:","") 
command=command.replace("The relevant command is:","")
command=command.replace("The relevant command is:","")

# TTS로 응답 읽기
text_to_speech_stream(command) 

# main 루프
if __name__ == "__main__":
    # 입력 방식 선택
    print("입력 방식을 선택하세요:")
    print("1. 음성 입력")
    print("2. 키보드 입력")
    choice = input("번호 입력 (1 or 2): ")

    use_voice = (choice.strip() == "1")

    while True:
        if use_voice:
            user_input = listen_and_transcribe() # STT로 부터 입력 텍스트로 전환
            print("사용자 입력:", user_input)
        else:
            user_input = input("입력: ")

        if user_input: # 입력 있을 때 
            # 답변 생성
            response = with_message_history.invoke(
                [HumanMessage(content=user_input)],
                config=config,
            )
            command = response.content
            print("[command]", command)

            if command:
                # 초기 부팅 인사 명령어 처리
                if "The relevant command for your greeting is:" in command:
                    command = command.replace(
                        "The relevant command for your greeting is:", 
                        "The relevant command is:"
                    )
                # 일반 명령어 처리
                if "The relevant command is:" in command:
                    parts = command.split("The relevant command is:")
                    description = parts[0].strip()
                    match = re.search(r"##(.*?)##", command)
                    # 명령어 추출
                    if match:
                        dogcommand = match.group(1)
                        print("[command]", command)
                    description = description.replace("The relevant command is:", "")
                    
                    text_to_speech_stream(description) # TTS로 답변 출력
                    dogcommand = dogcommand.replace(".", "")
                    print("[dogcommand]", dogcommand)

                    task = [dogcommand, 1] # [명령어, 반복횟수] 형식의 태스크 생성
                    send(goodPorts, task) # 명령어 전송
                    time.sleep(1)
                    task = ["ksit", 1] # 기본 자세로 복귀 명령어
                    send(goodPorts, task) # 명령어 전송

                else: # 일반 대화 처리
                    description = command.strip()
                    description = description.replace("The relevant command is:", "")
                    text_to_speech_stream(description)
