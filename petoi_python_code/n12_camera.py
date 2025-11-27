"""
==============================================================================
Project: petoi basic code

File: n12_camera.py
Summary: AI 비전 카메라 가위, 바위, 보 제스터 인식 예제
Author: 유도연
Created Date: 2025-10-20
Last Modified: 2025-10-20

==============================================================================
Description
    - 아두이노에서 AI 비전 카메라 모듈을 통해 객체 인식 데이터 수신
    - Python에서 시리얼 통신으로 데이터 읽기 및 이미지 디코딩 -> 이미지 형태로 저장
    - send_image_to_python.ino 연동
==============================================================================
Note:
    - box 출력과 이미지 정보 추출 사이의 시간 지연으로 정확한 위치에 box가 생성되지 않음

==============================================================================
"""

# from PetoiRobot import * # 기본 동작 정의 library
# 자동으로 포트 연결하기 
#    포트 정의하지 않아도 모든 포트 접근 -> 연결된 Petoi 포트로 연결됨
# autoConnect()

# Gyro 비활성화 
#    동작 작동 시 방해받을 수 있음
# deacGyro()

# ==============================================================================
# AI 비전 카메라 예제

import serial
import json
import base64
from datetime import datetime
from PIL import Image, ImageDraw
import io
import os

# 저장 경로 설정
save_dir = r"C:\\Users\\USER\\Desktop\\유도연\\petoi\\myCode\\image"
os.makedirs(save_dir, exist_ok=True)

# 시리얼 포트 설정 (포트 이름과 속도)
ser = serial.Serial('COM7', 115200, timeout=1) 

# buffer, capture 초기화
buf = "" # 데이터 버퍼
capture = False # 프레임 캡쳐 상태 플래그

while True:
    # 시리얼 포트에서 한 줄 읽기
    line = ser.readline().decode(errors="ignore").strip()

    # 프레임 시작-끝 확인
    if line == "-----BEGIN_FRAME-----":
        buf = ""
        capture = True
        continue

    if line == "-----END_FRAME-----":
        capture = False

        try:
            data = json.loads(buf) # JSON 데이터 파싱
        except:
            print("JSON decode error") # 디코딩 오류 시 무시
            continue

        gesture = data.get("gesture") # 제스처 정보 (보자기 = 0, 주먹 = 1, 가위 = 2)
        boxes = data.get("boxes", []) # 인식된 박스 정보
        img_b64 = data.get("image") # 이미지 데이터 (Base64)

        if gesture == 0:
            print(f"[Paper] {len(boxes)} box(es)") # 제스처 및 박스 개수 출력
        elif gesture == 1:
            print(f"[Rock] {len(boxes)} box(es)")
        elif gesture == 2:
            print(f"[Scissors] {len(boxes)} box(es)")
        if img_b64 and len(img_b64) > 100: # 유효한 이미지 데이터 확인
            img_bytes = base64.b64decode(img_b64) # Base64 디코딩
            img = Image.open(io.BytesIO(img_bytes)) # 이미지 열기 
            draw = ImageDraw.Draw(img) # 이미지에 그리기 객체 생성

            # box 시각화
            for b in boxes:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # 형식: 년월일_시분초_밀리초
                x, y, w, h = b["x"], b["y"], b["w"], b["h"] # 박스 좌표 정보 
                if gesture == 0: # 보자기
                    draw.rectangle((x, y, x + w, y + h), outline="red", width=3)
                    draw.text((x, y - 10), f"Paper:{b['score']}%", fill="red")
                    filename = f"paper_{timestamp}.jpg"
                elif gesture == 1: # 주먹
                    draw.rectangle((x, y, x + w, y + h), outline="green", width=3)
                    draw.text((x, y - 10), f"Rock:{b['score']}%", fill="green")
                    filename = f"Rock_{timestamp}.jpg"
                elif gesture == 2: # 가위
                    draw.rectangle((x, y, x + w, y + h), outline="blue", width=3)
                    draw.text((x, y - 10), f"Scissors:{b['score']}%", fill="blue")
                    filename = f"Scissors_{timestamp}.jpg"
            img.save(os.path.join(save_dir, filename))
            print("saved:", filename)

        continue

    if capture:
        buf += line # 데이터 버퍼에 추가