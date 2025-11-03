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

# 자동으로 포트 연결하기 
#    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
autoConnect()

# Gyro 비활성화 
#    동작 작동 시 방해받을 수 있음
# deacGyro()

# ==============================================================================
# LED light 센서 예제

SENSOR1 = 34
SENSOR2 = 35
MAX_READING = 1024

def readAnalogValue(pin):
    # 가상의 아날로그 센서값 읽기 (0~1023 임의값)
    return random.randint(0, 1023)

def read_doubleInfraredDistance():
    # 두 개의 IR 센서 값을 읽고 거리로 변환 후 출력
    rawL = readAnalogValue(SENSOR2) - 24
    rawR = readAnalogValue(SENSOR1) - 24

    # 거리 변환식 (아두이노 코드와 동일)
    dL = rawL / 4.0 if rawL < 30 else 200.0 / math.sqrt(MAX_READING - rawL)
    dR = rawR / 4.0 if rawR < 30 else 200.0 / math.sqrt(MAX_READING - rawR)

    # 결과 출력
    print(f"rawLeft: {rawL}\trawRight: {rawR}\tdL: {dL:.2f}\tdR: {dR:.2f}")

# 메인 루프
while True:
    read_doubleInfraredDistance()
    time.sleep(0.5)


# ==============================================================================
# 대기 상태
# time.sleep(1) # 초 단위

# ==============================================================================
# 포트 닫기
# closePort()




# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

