"""
==============================================================================
Project: 페토이 기본 코드 정리

File: 8_gesture_sensor.py
Summary: 제스처 센서 측정 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-11-11

==============================================================================
Description
    - 제스처 측정 python 코드

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
# 제스처 센서 측정 예제

def read_GestureSensor():
    delayTime = 0.000005
    value = readGestureVal()    # 0: Up; 1: Down; 2:Left; 3:Right
    print(((str("value = ")) + (str(value))))
    if (value == 0): # Up -> hi
        sendSkillStr('khi', 0.2)
    elif (value == 1): # Down -> cheer
        sendSkillStr('kchr', 0.2)
    elif (value == 2): # Left -> stretch
        sendSkillStr('kstr', 0.2)
    elif (value == 3): # Right -> sniff
        sendSkillStr('ksnf', 0.2)
    else:
        # The length of list is 16. The list format is [angle, angle, angle...]
        # stand up
        sendLongCmd('L', [0,0,0,0,0,0,0,0,30,30,30,30,30,30,30,30], delayTime)

if __name__ == "__main__":
    # 자동으로 포트 연결하기 
    #    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
    autoConnect()

    # Gyro 비활성화 
    #    동작 작동 시 방해받을 수 있음
    # deacGyro()

    print("Start reading gesture sensor... \n")
    sendSkillStr('kup', 0.2)
    try: 
        while True:
            read_GestureSensor()
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] 측정을 중단합니다.")

    finally:
        # 포트 닫기
        closePort()



# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # get the gesture value from gesture sensor
# # The gesture value meaning: -1: No gesture detected; 0: Up; 1: Down; 2: Left; 3: Right.
# def readGestureVal():
#     global intoGestureMode
#     # Check if the camera task isactivated.
#     if intoGestureMode == False:
#         res = send(goodPorts, ['XGr', 0])
#         if res != -1 :
#             # printH("intoGestureMode is:",intoGestureMode)
#             logger.debug(f'res={res}')
#             # p = re.compile(r'^(.*),',re.MULTILINE)
#             p = re.compile(r'^(?=.*[01])(?=.*,).+$', flags=re.MULTILINE)
#             if res[1] != '':
#                 logger.debug(f'res[1]={res[1]}')
#                 for one in p.findall(res[1]):
#                     val = re.sub('\t','',one)
#                 val = val.replace('\r','').replace('\n','')    # delete '\r\n'
#                 strFlagList = val.split(',')[:-1]
#                 flagList = list(map(lambda x:int(x),strFlagList))    # flag value have to be integer
#                 logger.debug(f'flagList={flagList}')
#                 if flagList[modeDict['Gesture']] == 1:
#                     task = ['XGp', 0]
#                     intoGestureMode = True
#                     return getValue(task, dataType ="int")
#                 else:
#                     val = -1
#                     print("No gesture detected!")
#                     return val
#             else:
#                 task = ['XGp', 0]
#                 intoGestureMode = True
#                 return getValue(task, dataType ="int")
#     else:
#         # printH("intoGestureMode is:",intoGestureMode)
#         task = ['XGp', 0]
#         return getValue(task, dataType ="int")
