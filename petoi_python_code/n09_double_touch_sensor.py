"""
==============================================================================
Project: petoi basic code

File: n09_double_touch_sensor.py
Summary: 더블 터치 센서 측정 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-11-11

==============================================================================
Description
    - 더블 터치 센서 측정 python 코드

==============================================================================
Instruction
    - 동작 작동 함수:
        - readDigitalValue(핀 번호)
            - 핀 번호 두 개 입력 - 왼쪽, 오른쪽

==============================================================================
Note:
    - digital value
        - 0: 터치 X, 1: 터치 O 로 출력

==============================================================================
"""

from PetoiRobot import * # 기본 동작 정의 library

# ==============================================================================
# 더블 터치 센서 측정 예제

def read_DoubleTouchSensor(PIN_left, PIN_right):
    left = readDigitalValue(PIN_left)
    right = readDigitalValue(PIN_right)

    print(((str("left")) + "|" + (str("right"))))
    print(((str(left)) + "\t" + (str(right))))

if __name__ == "__main__":
    # 자동으로 포트 연결하기 
    #    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
    autoConnect() 

    # Gyro 비활성화 
    #    동작 작동 시 방해받을 수 있음
    # deacGyro()

    print("Start double touch sensor... \n")
    sendSkillStr('ksit', 0.1)

    try:
        while True:
            read_DoubleTouchSensor(35, 34)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] 측정을 중단합니다.")

    finally:
        # 포트 닫기
        closePort()





