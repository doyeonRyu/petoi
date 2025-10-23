import sys
import time


from speechtotextEn import listen_and_transcribe
from Text2SpeechEn import text_to_speech_stream
from ardSerial import *
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
load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

store = {}
goodPorts = {}
connectPort(goodPorts)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

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
chain = prompt | model
config = {"configurable": {"session_id": "firstChat"}}
with_message_history = RunnableWithMessageHistory(chain, get_session_history)

user_input="Hi I am working on a programmable robot dog. I am developing a software to control this robot from remote. And also I want to chat with this dog. I will tell some sentences to this robot and you will answer me as a robot dog. Your name is Bittle. You will respond to my words as a robot dog and you will translate what I give as a sentence into the appropriate command according to the command set we have and give me the string command expression. I will give you the command list as json. Here I want you to talk to me and say the command that is appropriate for this file. On the one hand, you will tell me the correct command and on the other hand, you will say a sentence to chat with me. For example, when I say 'dude, let's jump', you will respond like 'of course I love jumping. The relevant command is:##ksit##'. Not in any other format. Write the command you find in the list as ##command##. For example, ##ksit## With normal talking you don't have to do same movement like 'khi' you can do anything you want."
response = with_message_history.invoke(
    [HumanMessage(content=user_input)],
    config=config,
)
print(response.content)

file_path = 'C:\\Users\\USER\\Desktop\\유도연\\robotdog\\petoi\\OpenCat\\OpenCat\\PetoiBittleChatGPT\\Commands.json'
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

user_input = "This is my dataset I mention." + file_content
response = with_message_history.invoke(
    [HumanMessage(content=user_input)],
    config=config,
)
user_input="Hi buddy, you welcome. Tell me about yourself shortly."
response = with_message_history.invoke(
    [HumanMessage(content=user_input)],
    config=config,
)
print(response.content)
command=response.content
command=command.replace("The relevant command for your greeting is:","")
command=command.replace("The relevant command is:","")
command=command.replace("The relevant command is:","")



text_to_speech_stream(command)

if __name__ == "__main__":

    while True:
        user_input = listen_and_transcribe()

        if user_input:
            response = with_message_history.invoke(
                [HumanMessage(content=user_input)],
                config=config,
            )
            command = response.content
            print(command)

            if command:

                if "The relevant command for your greeting is:" in command:
                    command=command.replace("The relevant command for your greeting is:","The relevant command is:")

                if "The relevant command is:" in command:
                    parts = command.split("The relevant command is:")
                    description = parts[0].strip()
                    match = re.search(r"##(.*?)##", command)

                    if match:
                        dogcommand = match.group(1)
                        print(command)
                    description = description.replace("The relevant command is:", "")
                    text_to_speech_stream(description)
                    dogcommand=dogcommand.replace(".","")
                    print (dogcommand)

                    task = [dogcommand, 1]
                    send(goodPorts, task)
                    time.sleep(1)
                    task = ["ksit", 1]
                    send(goodPorts, task)

                else:
                    description = command.strip()
                    description = description.replace("The relevant command is:", "")
                    text_to_speech_stream(description)