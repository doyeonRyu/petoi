"""
==============================================================================
Project: petoi basic code

File: n04_load_new_skill.py
Summary: 새롭게 추출한 스킬 불러오기 예제
Author: 유도연
Created Date: 2025-10-16
Last Modified: 2025-10-16

==============================================================================
Description
    - 새롭게 추출한 스킬 불러오기 python 코드 

==============================================================================
Instruction
    - 동작 작동 함수:
        - loadSkill("새로운 스킬 명", 동작 시간)

==============================================================================
new skill이란?  
    - 데스크탑 앱 혹은 아두이노 등으로 새롭게 정의해 추출된 skill
    - petoi desktop app skill composer에서 추출함
    - 저장 위치:    
        - C:/Users/USER/.config/Petoi/SkillLibrary/{모델 명}/
    - default: 
        - skillFileName

==============================================================================
Note:
    - 해당 모델 폴더에 새로운 스킬이 존재해야 함

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
# 새롭게 추출한 스킬 불러오기 예제

loadSkill("skillCreationTest", 3) 
loadSkill("standButtupStretchSit", 3)

# ==============================================================================
# 대기 상태
time.sleep(1) # 초 단위

# ==============================================================================
# 포트 닫기
closePort()




# ==============================================================================
# 관련 함수 참고 
# PetoiRobot/robot.py

# # perform a skill exported from the Skill Composer
# # the file directory is: "/$HOME/.config/Petoi/SkillLibrary/{model}/xxx.md" for Linux and macOS
# # the file directory is: "%HOMEDRIVE%\%HomePath%\.config\Petoi\SkillLibrary\{model}\xxx.md" for Windows
# def loadSkill(fileName, delayTime):
#     global modelName
#     # get the path of the exported skill file
#     if ".md" in fileName:
#         skillFilePath = configDir + seperation + 'SkillLibrary' + seperation + modelName + seperation + fileName
#     else:
#         skillFilePath = configDir + seperation + 'SkillLibrary' + seperation + modelName + seperation + fileName +'.md'

#     logger.debug(f'skillFilePath:{skillFilePath}')

#     # open the skill file
#     with open(skillFilePath,"r",encoding='utf-8') as f:
#         line = f.readline()  # get the whole line content
#         while line:
#             #key words
#             if ("# Token") in line:
#                 # get the token
#                 line = next(f) #get the next line
#                 token = line.replace("\n","")
#                 logger.debug(f'token:{token}')
#             if ("# Data") in line:
#                 # get the skill data
#                 lines = f.readlines()  # get the rest lines of the file
#                 logger.debug(f'lines:{lines}')
#             line = f.readline()
#     skillDataString = ''.join((str(x) for x in lines))
#     logger.debug(f'skillDataString:{skillDataString}')
#     skillDataString = ''.join(skillDataString.split()).split('{')[1].split('}')[0].split(',')
#     logger.debug(f'skillDataString:{skillDataString}')
#     if skillDataString[-1] == '':
#         skillDataString = skillDataString[:-1]
#     cmdList = list(map(int, skillDataString))
#     logger.debug(f'cmdList:{cmdList}')

#     send(goodPorts, [token, cmdList, delayTime])
