"""
==============================================================================
Project: 페토이 기본 코드 정리

File: 1_basic_skills.py
Summary: 기본 정의된 동작 작동 예제
Author: 유도연
Created Date: 2025-10-15
Last Modified: 2025-10-15

==============================================================================
Description
    - Petoi 자체에서 기본으로 정의된 동작 python 코드

==============================================================================
Instruction
    - 동작 작동 함수:
        - sendSkillStr(동작 명령어, 작동 시간)
        - PetoiRobot/robot.py에 정의
    - 명령어    
        - 기본: k + 단축어 형태 

==============================================================================
Skill list: 
    - stand up | kup
    - sit | ksit
    - butt up | kbuttUp
    - stretch | kstr
    - rest | krest
    - zero | kzero
    - hi | khi
    - walk forward | kwkF
    - 등

- 참고: MindPlus, Petoi doc center

==============================================================================
Note:
    - Bittle X + Arm으로 작동 시 무게 중심 등의 문제로 동작 작동 어려울 수 있음

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
# 대표 동작 작동 테스트
sendSkillStr('kup', 1) # stand up
sendSkillStr('ksit', 1) # sit
sendSkillStr('kbuttUp', 1) # butt up
sendSkillStr('kstr', 1) # stretch
sendSkillStr('krest', 1) # rest
sendSkillStr('kzero', 1) # zero
sendSkillStr('kbx', 1) # boxing
sendSkillStr('kchr', 1) # cheer
sendSkillStr('kck', 1) # check around
sendSkillStr('kdg', 1) # dig
sendSkillStr('khds', 1) # stand on hands
sendSkillStr('khg', 1) # hug
sendSkillStr('khi', 1) # hi
sendSkillStr('khu', 1) # hands up
sendSkillStr('kjmp', 1) # jump
sendSkillStr('kkc', 1) # kick
sendSkillStr('knd', 1) # nod
sendSkillStr('kpd', 1) # play dead
sendSkillStr('kpee', 1) # pee
sendSkillStr('kcrF', 1) # crawl
sendSkillStr('kphF', 1) # push forward
sendSkillStr('kwkF', 1) # walk forward
sendSkillStr('kwkL', 1) # walk left
sendSkillStr('kbk', 1) # back
sendSkillStr('ktrF', 1) # trot

# ==============================================================================
# 대기 상태
time.sleep(1) # 초 단위

# ==============================================================================
# 포트 닫기
closePort()




# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # send a short skill string
# def sendSkillStr(skillStr, delayTime):
#     # in_str = skillStr + '\n'
#     # com.write(bytes(skillStr, 'utf-8'))
#     # com.Send_data(encode(in_str))
#     # checkResponse('k')
#     # time.sleep(delayTime)
#     logger.debug(f'skillStr={skillStr}')
#     send(goodPorts, [skillStr,delayTime])

