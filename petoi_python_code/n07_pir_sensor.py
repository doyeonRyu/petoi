"""
==============================================================================
Project: petoi basic code

File: n07_pir_sensor.py
Summary: PIR 모션 센서 측정 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-11-11

==============================================================================
Description
    - PIR 모션 센서 측정 예제

==============================================================================
Instruction
    - 동작 작동 함수:
        - readDigitalValue(핀 번호)
            - 해당 핀 번호에서 디지털 신호 받아서 출력하기 
            - 0: 사람 감지 X, 4-16mm 내에 반응 없음
            - 1: 사람 감지 O 혹은 터치 감지
    - 핀번호    
        - PIR 센서 핀 번호 34, 35 중 34

==============================================================================
Note:
    - digital value
        - 0: X, 1: O로 출력

==============================================================================
"""

from PetoiRobot import * # 기본 동작 정의 library

# ==============================================================================
# PIR 모션 센서 측정 예제

def read_PIRSensor(PIN):
    val = readDigitalValue(PIN) # PIR 센서 핀 번호 34, 35 중 34

    if val == 0:
        print(val)
    elif val == 1:
        print("사람 움직임 감지 혹은 터치 감지")

if __name__ == "__main__":
    # 자동으로 포트 연결하기 
    #    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
    autoConnect()

    # Gyro 비활성화 
    #    동작 작동 시 방해받을 수 있음
    # deacGyro()
    
    print("Start reading PIR sensor.. \n")

    sendSkillStr('kup', 0.2)
    try:
        while True: 
            read_PIRSensor(34) 
            time.sleep(1)

    except KeyboardInterrupt:
        # Ctrl + C 입력 시 실행됨
        print("\n[KeyboardInterrupt] 측정을 중단합니다.")

    finally:
        # 포트 닫기
        closePort()



# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # get digital value of a pin
# def readDigitalValue(pin):
#     token = 'R'
#     task = [token, [100, pin], 0]

#     # p = getPortList()
#     # rawData = sendTask(goodPorts, p[0], task)
#     return getValue(task)

# ==============================================================================
# 아두이노 코드 

# //connects to the digital Grove socket with I34 and I35
# #define DIGITAL1 34
# #define DIGITAL2 35

# int val;
# void setup()
# {
#   Serial.begin(115200);
#   Serial.setTimeout(2);
#   pinMode(DIGITAL1, INPUT);
#   pinMode(DIGITAL2, INPUT);
# }
 
# void loop()
# {
#   val = digitalRead(DIGITAL1);
#   Serial.println(val); //prints 1 if there's human or touch event
#                          //prints 0 if there's reflection within 4-16mm.
#   delay(100);
# }