"""
==============================================================================
Project: 페토이 관련 코드 정리

File: n14_obstacle_avoidance.py
Summary: 이동 시 장애물 감지 및 피하기
Author: 유도연
Created Date: 2025-11-11
Last Modified: 2025-11-21

==============================================================================
Description
    - 앞으로 걸어가다가 장애물 감지 시 양쪽 센서 거리 계산 후 더 거리가 먼 방향으로 이동

    Function: avoidObstacle
        - 이동 중 장애물을 피해가는 함수 
        - 앞으로 걸어가다가 장애물 감지 시 양쪽 센서 거리 계산 후 더 거리가 먼 방향으로 이동
        
==============================================================================
Skill list: 
    - read_doubleIFDistance(SENSOR2, SENSOR1): IR 센서 측정 함수 
        - return: dL: 왼쪽 센서 측정 거리, dR: 오른쪽 센서 측정 거리
    - sendSkillStr("동작", "작동 시간"): 동작 작동 함수
        - return: None, 동작만 실행

==============================================================================
Limitations:
    - 카메라 센서가 없어 사람 감지 등 정교한 감지 불가능
    - 함수가 다시 실행되는 과정에서 잠시 멈춤 과정 존재

==============================================================================
"""

from PetoiRobot import * # 기본 동작 정의 library   
from n11_ir_sensor import read_doubleIFDistance

# ==============================================================================
# 이동 중 장애물 피하기

def avoidObstacle(SENSOR2, SENSOR1):
    """
    Function: avoidObstacle
        - 이동 중 장애물을 피해가는 함수 
        - 앞으로 걸어가다가 장애물 감지 시 양쪽 센서 거리 계산 후 더 거리가 먼 방향으로 이동
    Parameters:
        - Sensor2: 왼쪽 센서 값, Pin 번호 중 더 큰 값
        - Sensor1: 오른쪽 센서 값, Pin 번호 중 더 작은 값
    Logic: 
        1. IR 센서로부터 거리 읽기
        2. 장애물 인지 
            1) 정면 장애물 인지 시 
                - 거리가 더 먼 방향으로 회피
            2) 왼쪽만 장애물 인지 시
                - 오른쪽으로 회피
            3) 오른쪽만 장애물 인지 시 
                - 왼쪽으로 회피
            4) 장애물 없음
                - 계속 직진
    Return: 
        - None, 동작만 실행
    """ 
    
    # 1. IR 센서로부터 거리 읽기
    _, _, dL, dR = read_doubleIFDistance(SENSOR2, SENSOR1)
    print(f"Left IR: {dL:.2f} cm, Right IR: {dR:.2f} cm")

    # 2. 장애물 감지 임계값 설정
    threshold = 5  # cm 기준

    # 3. 장애물 인지 시
    # 1) 정면 장애물 (양쪽 다 가까움)
    if dL < threshold and dR < threshold:
        print("[정면 장애물 감지] 거리가 더 먼 방향으로 회피합니다.")
        sendSkillStr("kup", 0.5) # 정지
        sendSkillStr("kbkF", 1) # 뒤로 빠지기

        # 넓은 방향(더 먼 IR 값)으로 회피
        if dL < dR:
            print("-> 오른쪽으로 회피")
            sendSkillStr("kwkR", 1.5)
        else:
            print("-> 왼쪽으로 회피")
            sendSkillStr("kwkL", 1.5)

        return
    
    # 2) 왼쪽만 막힘 -> 오른쪽으로 회피
    if dL < threshold:
        print("[왼쪽 장애물 감지] 오른쪽으로 회피합니다.")
        sendSkillStr("kwkR", 1.5)
        return

    # 3) 오른쪽만 막힘 -> 왼쪽으로 회피
    if dR < threshold:
        print("[오른쪽 장애물 감지] 왼쪽으로 회피합니다.")
        sendSkillStr("kwkL", 1.5)
        return

    # 4. 장애물 없음 -> 계속 직진
    print("[장애물 없음] 계속 직진합니다.")
    sendSkillStr("kwkF")
    return

if __name__ == "__main__":
    # 자동으로 포트 연결하기 
    #    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
    autoConnect()

    # Gyro 비활성화 
    #    동작 작동 시 방해받을 수 있음
    deacGyro()

    # 초기 자세 설정
    sendSkillStr('ksit', 1)
    sendSkillStr('kwkF', 0.2)

    SENSOR1 = 34  # 오른쪽 IR
    SENSOR2 = 35  # 왼쪽 IR

    try:
        while True:
            avoidObstacle(SENSOR2, SENSOR1)
            # time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] 프로그램 종료")

    finally:
        closePort()