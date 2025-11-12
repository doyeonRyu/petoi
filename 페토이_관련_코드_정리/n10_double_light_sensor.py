"""
==============================================================================
Project: 페토이 기본 코드 정리

File: 10_double_light_sensor.py
Summary: LED light 센서 예제
Author: 유도연
Created Date: 2025-10-17
Last Modified: 2025-10-17

==============================================================================
Description
    - 광감지 센서 python 코드
    - 밝을 수록 높은 값

==============================================================================
Instruction
    - 동작 작동 함수:
        - readAnalogValue(핀 번호)
            - 핀 번호 두 개 입력 - 왼쪽, 오른쪽

==============================================================================
Note:
    - analog value
        - 0, 1아닌 실제 값으로 나옴

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
# LED light 센서 예제

def read_LEDlight(PIN_1, PIN_2):
    light1 = readAnalogValue(PIN_1)
    light2 = readAnalogValue(PIN_2)

    print("light1 = ", str(light1))
    print("light2 = ", str(light2))

if __name__ == "__main__":
    print("Start reading LED light sensor... \n")
    sendSkillStr('ksit', 0.1)
    try:
        while True:
            read_LEDlight(35, 34)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] 측정을 중단합니다.")

    finally:
        closePort()