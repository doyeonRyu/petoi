"""
==============================================================================
Project: 페토이 기본 코드 정리

File: 11_ir_sensor.py
Summary: ir 센서 예제
Author: 유도연
Created Date: 2025-10-17
Last Modified: 2025-10-17

==============================================================================
Description
    - IR Reflective 센서 측정 python 코드
    - 양 쪽에서 거리 계산

==============================================================================
Instruction
    - 동작 작동 함수:
        - readAnalogValue(핀 번호)
            - 핀 번호 두 개 입력 - 왼쪽, 오른쪽

==============================================================================
Result
    - rawLeft: 왼쪽 센서의 아날로그 입력값
    - rawRight: 오른쪽 센서의 아날로그 입력값
    - dL: 왼쪽 센서 거리 (cm 단위 근사)
    - dR: 오른쪽 센서 거리 (cm 단위 근사)

    - 센서 값이 더 클수록 해당 센서에 가까운 거리
    - rawLeft > rawRight -> dL < dR 로 나옴

==============================================================================
Note:
    - analog value
        - 0, 1아닌 실제 값으로 나옴

==============================================================================
"""

from PetoiRobot import * # 기본 동작 정의 library

import time
import math
import random

# ==============================================================================
# LED light 센서 예제

def read_doubleIFDistance(SENSOR2, SENSOR1):
    """
    Function: read_doubleInfraredDistance
        - 두 개의 IR 센서로부터 값을 읽고 거리로 변환한 후 출력
    Description:
        - 아두이노 코드의 analogRead(SENSORx)/ratio 부분을
          readAnalogValue() 기반으로 변환
        - raw 값이 30 미만이면 단순 비례식 사용, 그 외엔 비선형 보정식 사용
    """
    READING_COUNT = 30
    SENSOR_DISPLACEMENT = 3.7
    MAX_READING = 4096  # 4096
    ratio = MAX_READING / 1024 # 1024로 나눈 비율
    # 1. 센서 값 읽기
    rawL = int(readAnalogValue(SENSOR2) / ratio)
    rawR = int(readAnalogValue(SENSOR1) / ratio)

    # 2. 거리로 변환 (아두이노 코드의 공식 그대로)
    dL = rawL / 4.0 if rawL < 30 else 200.0 / math.sqrt(1024 + 24 - rawL)
    dR = rawR / 4.0 if rawR < 30 else 200.0 / math.sqrt(1024 + 24 - rawR)

    # 3. 결과 리턴
    return rawL, rawR, dL, dR

if __name__ == "__main__":
    # 자동으로 포트 연결하기 
    #    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
    # autoConnect()

    # Gyro 비활성화 
    #    동작 작동 시 방해받을 수 있음
    # deacGyro()

    print("Start reading double IR distance... \n")

    try:
        while True:
            SENSOR1 = 34
            SENSOR2 = 35
            rawL, rawR, dL, dR = read_doubleIFDistance(SENSOR2, SENSOR1)
            # 3. 결과 출력 (Serial.print -> print)
            print(f"rawLeft: {rawL}\trawRight: {rawR}\tdL: {dL:.2f}\tdR: {dR:.2f}")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] 측정을 중단합니다.")

    finally:
        closePort()

# ==============================================================================
# 대기 상태
# time.sleep(1) # 초 단위

# ==============================================================================
# 포트 닫기
# closePort()




# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

