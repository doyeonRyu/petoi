"""
==============================================================================
Project: 페토이 기본 코드 정리

File: 9_double_touch_sensor.py
Summary: 더블 터치 센서 측정 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-10-16

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

# 자동으로 포트 연결하기 
#    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
autoConnect() 

# Gyro 비활성화 
#    동작 작동 시 방해받을 수 있음
# deacGyro()

# ==============================================================================
# 더블 터치 센서 측정 예제

sendSkillStr('ksit', 0.1)
# writeAnalogValue(16., 120) # 확장 모듈의 스위치를 Uart2로 설정하십시오. (BiBoard V1_0 부터는 없음.)
# writeDigitalValue(16., 1) # 확장 모듈의 스위치를 Uart2로 설정하십시오. (BiBoard V1_0 부터는 없음.)
# while True:
#     d34 = readDigitalValue(16.) # 확장 모듈의 스위치를 Uart2로 설정하십시오. (BiBoard V1_0 부터는 없음.)
#     d35 = readDigitalValue(17.) # 확장 모듈의 스위치를 Uart2로 설정하십시오. (BiBoard V1_0 부터는 없음.)
#     print(((str("d34=")) + (str(d34))))
#     print(((str("d35=")) + (str(d35))))
#     if ((d34 == 1) or (d35 == 1)): # 둘 중 하나라도 눌렸을 때
#         d34 = readDigitalValue(34)
#         time.sleep(0.01) 
#         d35 = readDigitalValue(35)
#         time.sleep(0.01)                           
#     if ((d34 == 1) and (d35 == 1)): # 둘 다 눌렸을 때
#         sendSkillStr('kbk', 1) # back
#         sendSkillStr('kup', 0.5) # stand up
#         sendSkillStr('ksit', 0.5) # sit
#     else:
#         if (d34 == 1): # 34번 핀만 눌렸을 때
#             # 리스트 형식: [관절 인덱스, 각도, 관절 인덱스, 각도...]
#             #    Head panning (to 60 -> to 0 degree)
#             rotateJoints('M', (absValList(0, 60) + absValList(0, 0)), 0.5)
#         else:
#             if (d35 == 1): # 35번 핀만 눌렸을 때
#                 # 리스트 형식: [관절 인덱스, 각도, 관절 인덱스, 각도...]
#                 #   Head panning (to -60 -> to 0 degree)
#                 rotateJoints('M', (absValList(0, -60) + absValList(0, 0)), 0.5)

while True:
    left = readDigitalValue(35)
    right = readDigitalValue(34)

    print(((str("left")) + "|" + (str("right"))))
    print(((str(left)) + "\t" + (str(right))))
    
    time.sleep(0.5)

# ==============================================================================
# 포트 닫기 # while문이라 쓰이지 않음
# closePort()




