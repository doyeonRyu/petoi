"""
==============================================================================
Project: 페토이 응용 코드 정리

File: 14_obstacle_avoidance.py
Summary: 이동 시 장애물 감지 및 피하기
Author: 유도연
Created Date: 2025-11-11
Last Modified: 2025-11-11

==============================================================================
Description
    - 앞으로 걸어가다가

==============================================================================
Instruction
    - 동작 작동 함수:
        - 
    - 명령어    
        - 

==============================================================================
Skill list: 


- 참고: 

==============================================================================
Note:
    - 

Limitations:
    - 카메라 센서가 없어 사람 감지 불가능

==============================================================================
"""

import time
from PetoiRobot import * # 기본 동작 정의 library   
from n11_ir_sensor import read_doubleIFDistance

# 자동으로 포트 연결하기 
#    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
autoConnect()

# Gyro 비활성화 
#    동작 작동 시 방해받을 수 있음
# deacGyro()

# ==============================================================================
# 이동 중 장애물 피하기

def avoidObstacle(SENSOR2, SENSOR1):
    # 1. IR 센서로부터 거리 좌우 거리 읽기 
    _, _, dL, dR = read_doubleIFDistance(SENSOR2, SENSOR1)
    print(f"Left IR: {dL:.2f} cm, Right IR: {dR:.2f} cm")

    # 2. 장애물 감지 임계값 설정
    threshold = 20  # cm 기준

    # 3. 장애물 감지 시 회피 동작 수행
    if dL 
    # # 3. 장애물 감지 시 회피 동작 수행
    # if dL < threshold or dR < threshold:
    #     # 1) 정면을 좌우로 스캔
    #     rotateJoints('I', absValList(0, 50), 0.3)
    #     _, _, dL, dR = read_doubleIFDistance(SENSOR2, SENSOR1)
    #     rotateJoints('I', absValList(0, -50), 0.3)

    #     # 2) 더 넓은 방향으로 회피
    #     if dL > dR:
    #         print("Turning Left to avoid obstacle")
    #         sendCmdStr("kvtL", 2) # 왼쪽 회전
    #         sendCmdStr("i", 0)
    #         sendSkillStr('kwkL', 2) # 왼쪽 보행
    #     else:
    #         print("Turning Right to avoid obstacle")
    #         sendCmdStr("kvtR", 2) # 오른쪽 회전
    #         sendCmdStr("i", 0)
    #         sendSkillStr('kwkR', 2) # 오른쪽 보행

    #     # (3) 회피 완료 후 정면 복귀
    #     print("Returning to forward direction")
    #     sendCmdStr("kvtF", 1)         # 정면 방향으로 복귀
    #     sendCmdStr("i", 0)

    #     # (4) 다시 직진 시작
    #     print("Resuming forward movement")
    #     sendSkillStr('kwkF', 0)

    # else:
    #     # 장애물이 없으면 계속 전진
    #     sendSkillStr('kwkF', 0)

if __name__ == "__main__":
    sendSkillStr('ksit', 1)
    sendSkillStr('kwkF', 0.2)

    SENSOR1 = 34
    SENSOR2 = 35

    try:
        while True:
            avoidObstacle(SENSOR2, SENSOR1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt]")

    finally:
        closePort()
