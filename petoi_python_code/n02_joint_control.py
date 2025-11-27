"""
==============================================================================
Project: petoi basic code

File: n02_joint_control.py
Summary: 관절 하나씩 움직이기 예제 
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-10-16

==============================================================================
Description
    - 정의된 관절 인덱스를 통해 관절 하나씩 움직이기 python 코드

==============================================================================
Instruction
    - 동작 작동 함수:
        - rotateJoints('M', absValList(관절 인덱스, 각도), 동작 시간)
            - absValList 대신 list 형태 그대로 넣어줘도 됨 [인덱스, 각도, 인덱스, 각도 ...]
            - M: 순차적 작동
            - I: 동시 작동 (absValList() 사용 시 여러 관절 동시 정의가 아니기 때문에 무시됨)
        - sendLongCmd('L', [angle, angle, angle, ... ],0.2)
            - angle 리스트로 동작
==============================================================================
관절 정의 목록
    - Head panning joint index = 0
    - Left Front arm joint index = 8
    - Right Front arm joint index = 9
    - Left Back arm joint index = 10
    - Right Back arm joint index = 11
    - Left Front knee joint index = 12
    - Right Front knee joint index = 13
    - Left Back knee joint index = 14
    - Right Back knee joint index = 15
    - 총 9개 

Bittle X + Arm 버전
    - Claw Pan joint index = 0
    - Claw Lift joint index = 1
    - Claw Open joint index = 2
    - 다리 관절은 동일
    - 총 11개

- 참고: Petoi doc center
    - arm: 어께 (윗 관절)
    - knee: 팔목 발목 (아래 관절)
    - Bittle X + Arm 동작 시 아래 관련 코드 주석 해제 필요
==============================================================================
"""

from PetoiRobot import * # 기본 동작 정의 library

# 자동으로 포트 연결하기 
#    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
autoConnect()

# Gyro 비활성화 
#    동작 작동 시 방해받을 수 있음
# deacGyro()

# ==============================================================================
# 관절 움직임 예제

# 순서
#    Head panning (혹은 Claw pan, lift, open)
#    LF arm, RF arm, LB arm, RB arm
#    LF knee, RF knee, LR knee, RB knee

rotateJoints('M', absValList(0, 30), 0.2) # Head panning # 왼쪽 # Claw Pan
#    Bittle X + Arm 버전
# rotateJoints('M', absValList(1, 30), 0.2) # Claw Lift
# rotateJoints('M', absValList(2, 30), 0.2) # Claw Open
# 다리 관절
rotateJoints('M', absValList(8, 30), 0.2) # LF arm
rotateJoints('M', absValList(9, 30), 0.2) # RF arm
rotateJoints('M', absValList(10, 30), 0.2) # LB arm
rotateJoints('M', absValList(11, 30), 0.2) # RB arm
rotateJoints('M', absValList(12, 30), 0.2) # LF knee
rotateJoints('M', absValList(13, 30), 0.2) # RF knee
rotateJoints('M', absValList(14, 30), 0.2) # LB knee
rotateJoints('M', absValList(15, 30), 0.2) # RB knee


rotateJoints('M', absValList(0, -30), 0.2) # Head panning # 오른쪽 # Claw Pan
#    Bittle X + Arm 버전
# rotateJoints('M', absValList(1, -30), 0.2) # Claw Lift
# rotateJoints('M', absValList(2, -30), 0.2) # Claw Open
# 다리 관절
rotateJoints('M', absValList(8, -30), 0.2) # LF arm
rotateJoints('M', absValList(9, -30), 0.2) # RF arm
rotateJoints('M', absValList(10, -30), 0.2) # LB arm
rotateJoints('M', absValList(11, -30), 0.2) # RB arm
rotateJoints('M', absValList(12, -30), 0.2) # LF knee
rotateJoints('M', absValList(13, -30), 0.2) # RF knee
rotateJoints('M', absValList(14, -30), 0.2) # LB knee
rotateJoints('M', absValList(15, -30), 0.2) # RB knee

# absValList 대신 list 형태 그대로 넣어주기
#    The list format is [joint index, angle, joint index, angle...]
rotateJoints('M', [0, 0, 8, 0, 9, 0, 10, 0, 11, 0, 12, 0, 13, 0, 14, 0, 15, 0], 0.2) # zero 상태 
#    Bittle X + Arm 버전
# rotateJoints('M', [0, 0, 1, 0, 2, 0, 8, 0, 9, 0, 10, 0, 11, 0, 12, 0, 13, 0, 14, 0, 15, 0], 0.2) # zero 상태

#    The length of list is 16. The list format is [angle, angle, angle...]
sendLongCmd('L', [0,0,0,0,0,0,0,0,30,30,30,30,30,30,30,30],0.2)

# ==============================================================================
# 대기 상태
time.sleep(1) # 초 단위

# ==============================================================================
# 포트 닫기
closePort()




# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # rotate the joints sequentially or simultaneously
# def rotateJoints(token, var, delayTime):
#     # currentAngleList = getAngleList()
#     newList = []
#     # delay = delayTime
#     for iA in var:
#         if isinstance(iA, int):
#             newList += [iA]
#         elif isinstance(iA, tuple):
#             if len(iA)==2:
#                 newList += [iA[0], iA[1]]
#                 # currentAngleList[iA[0]] = iA[1]
#             elif len(iA)==3:
#                 currentAngleList = getAngleList()
#                 currentAngleList[iA[0]] += iA[1]*iA[2]
#                 currentAngleList[iA[0]] = min(125,max(-125,currentAngleList[iA[0]]))
#                 newList += [iA[0], currentAngleList[iA[0]]]
#             # printH("iA[0]:", iA[0])
#             # if iA[0] == 2 and modelName == 'BittleR':
#             #     delay = 0.1
#             #     printH("delay:", delay)

#     sendLongCmd(token, newList, delayTime)


# # creat an absolut value list
# def absValList(num1, num2):
#     return [(int(num1), num2)]