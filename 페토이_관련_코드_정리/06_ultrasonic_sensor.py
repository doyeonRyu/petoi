"""
==============================================================================
Project: 페토이 기본 코드 정리

File: 6_ultrasonic_sensor.py
Summary: 초음파 센서 측정 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-11-11

==============================================================================
Description
    - RX2 번호를 통해 초음파 센서 측정값 출력 python 코드

==============================================================================
Instruction
    - 동작 작동 함수:
        - readUltrasonicDistance(triggerPin, echoPin)
    - triggerPin: 처음 신호 보내는 핀. Bittle - RX2 번호
    - echoPin: 돌아오는 신호 받는 핀. -1(default) = same trigger
    - 둘 사이의 시간 계산을 통해 거리 측정
    
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
# 초음파 센서 측정 예제

def read_UltrasonicSensor(RX2, TX2):
    result = readUltrasonicDistance(TX2, -1) # RX2: 9, TX2: 10, -1: same trigger

    # 튜플이면 첫 번째 값만 사용
    if isinstance(result, tuple):
        distance = float(result[0])
    else:
        distance = float(result) 

    return distance

if __name__ == "__main__":
    print("Start reading ultrasonic sensor.. \n")

    try:
        while True:
            distance = read_UltrasonicSensor(9, 10) # RX2, TX2
            print(f"The distance is: {distance:.2f}")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] 측정을 중단합니다.")

    finally:
        # 포트 닫기
        closePort()



# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # get distance value(cm) from ultrasonic sensor
# def readUltrasonicDistance(triggerPin, echoPin):
#     token = 'XU' # 시리얼 모니터 값
#     task = [token, [int(triggerPin), int(echoPin)], 0]
#     return getValue(task, dataType ="float")