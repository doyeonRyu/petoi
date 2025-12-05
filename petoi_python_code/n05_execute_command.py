"""
==============================================================================
Project: petoi basic code

File: n05_execute_command.py
Summary: 직렬 명령 수행하기 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-10-16

==============================================================================
Description
    - 직렬 명령 수행하기 python 코드
        - 시리얼 모니터에 작성하듯 직렬 명령어 작성

==============================================================================
Instruction
    - 동작 작동 함수:
        - sendCmdStr("직렬 명령어", 동작 시간)

==============================================================================
Note:
    - 직렬 명령어 예시 참고: https://docs.petoi.com/apis/serial-protocol

==============================================================================
"""

from PetoiRobot import * # 기본 동작 정의 library

# 자동으로 포트 연결하기 
#    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
autoConnect()

# Gyro 비활성화 
#    동작 작동 시 방해받을 수 있음
deacGyro()

# ==============================================================================
# 직렬 명령 수행하기 예제

sendCmdStr("kit", 0.2) # sit
sendCmdStr("kup", 0.2) # stand up
sendCmdStr("m0 -60 0 60 0 0", 0.2) # m0: head panning

i = 8
while i != 15: # 8-14: 다리 관절
    sendCmdStr(f"m{i} 0 30 60 30 0 -30 -60 -30 0", 0.2) 
    i+=1

# ==============================================================================
# 대기 상태
time.sleep(1) # 초 단위

# ==============================================================================
# 포트 닫기
closePort()




# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # send a command string
# def sendCmdStr(cmdStr, delayTime):
#     logger.debug(f'serialCmd={cmdStr}')
#     if cmdStr != '':
#         token = cmdStr[0]
#         logger.debug(f'cmdList={token}')
#         cmdList = cmdStr[1:].replace(',',' ').split()
#         logger.debug(f'cmdList={cmdList}')

#         if len(cmdList) <= 1:
#             send(goodPorts, [cmdStr, delayTime])
#         else:
#             cmdList = list(map(lambda x:int(x),cmdList))
#             send(goodPorts, [token, cmdList, delayTime])