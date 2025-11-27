/* 
==============================================================================
Project: Ai vision 카메라 

File: send_image_to_python.ino
Summary: 카메라 객체 인식 결과를 python으로 보내 이미지 형태로 저장하는 코드 
Author: 유도연
Created Date: 2025-11-25
Last Modified: 2025-11-25

==============================================================================
Description
    - 목표: ESP32에서 가위, 바위, 보 감지 시 -> python으로 이미지, box 정보 전달
    - 과정: 
        1. eps32에서 추론 시작
        2. 객체 인식 시 box 정보, last_image 출력
        3. 연결된 파이썬으로 box, image 정보를 문자열로 받아 이미지 형태로 변환하여 저장
    - n12_camera.py와 연동
==============================================================================
Skill list: 
    - AI.boxes(): 박스 탐지 결과 (detection 모델)
    - AI.last_image(): 마지막 입력 프레임
        - 이미지를 base64 형태로 출력

==============================================================================
Limitations:
    - box 출력과 이미지 정보 추출 사이의 시간 지연으로 정확한 위치에 box가 생성되지 않음

==============================================================================
*/

#include <Arduino.h> 
#include <Wire.h> // I2C 통신을 위한 라이브러리 
#include <Seeed_Arduino_SSCMA.h> // Seeed의 AI 모듈 SSCMA 제어 라이브러리

SSCMA AI; // SSCMA(추론 엔진) 객체 생성

// 연결 대상 선택
// 1 -> XIAO ESP32-S3와 I2C로 연결된 경우
// 0 -> Grove Vision AI 모듈과 연결된 경우
#define SSCMA_CONNECT_TO_XIAO_S3         1
#define SSCMA_CONNECT_TO_GORVE_VISION_AI 0

// setup
void setup()
{
    Serial.begin(115200); // serial monitor 시작; 속도 115200 bps
    while (!Serial) delay(1000); // 시리얼 연결될 때까지 대기 

#if SSCMA_CONNECT_TO_XIAO_S3
    Wire.begin(); // I2C 통신 시작 (SDA/SCL 자동 설정)
    AI.begin(&Wire); // SSCMA AI 모듈 초기화 (XIAO S3와 연결)
#endif

#if SSCMA_CONNECT_TO_GORVE_VISION_AI
    Wire.begin(); // I2C 시작
    AI.begin(&Wire, D3); // Grove Vision AI를 사용하는 경우 
#endif

}

// loop
void loop() {
    // 추론 실행 명령
    if (!AI.invoke(1, false, false)) { // (run_mode=1, save_image=false, debug_info=fale) 
        /*
        Function:
            bool AI.invoke(int run_mode, bool save_image, bool debug_info)
        Parameters: 
            - run_mode: 0 or 1 (default: 1 = 기본값 / 추론 실행)
            - save_image: false. true -> last_image()에 현재 프레임 저장 (shape: Base64 문자열)
            - debug_info: false, true -> 내부 디버그 출력 (성능, 세부 정보)
        Return: 
            - true (실패) / false (성공)
        */

        int detected = -1; // detected 초기화 (감지된 클래스 없음)

        // 박스 탐지
        for (int i = 0; i < AI.boxes().size(); i++) {
            /*
            Function: 
                AI.boxes()
                    - x: 박스 왼쪽 상단 X 좌표
                    - y: 박스 왼쪽 상단 Y 좌표
                    - w: 박스 너비
                    - h: 박스 높이 
                    - score: 신뢰도 (0-100 정수)
                    - target: 클래스 ID
                - detection 기반 모델일 때 사용
            Return: 객체 탐지 결과 반환
                예) Box[0] target=1, score=72, x=142, y=103, w=113, h=116
                    -  "class 1을 0.72 확률로 인식했고, 위치는 (142,103) / 크기 113×116"
            */
            // c: 박스 감지된 클래스 번호  
            int c = AI.boxes()[i].target;
            int score = AI.boxes()[i].score;
            if (score > 60) {
                detected = c;
            }
        }

        // 가위 / 바위 / 보 감지된 경우만 저장
        if (detected == 0 || detected == 1 || detected == 2) { 
            // 보자기 0 | 주먹 1 | 가위 2

            // 프레임 저장용 invoke
            if (!AI.invoke(1, true, false)) { // save_image = True

                String img = AI.last_image();

                Serial.println("-----BEGIN_FRAME-----");
                Serial.print("{\"gesture\":");
                Serial.print(detected);
                Serial.print(",\"boxes\":[");

                // 박스 정보 JSON에 넣기
                for (int i = 0; i < AI.boxes().size(); i++) {
                    auto b = AI.boxes()[i];
                    Serial.print("{\"target\":");
                    Serial.print(b.target);
                    Serial.print(",\"score\":");
                    Serial.print(b.score);
                    Serial.print(",\"x\":");
                    Serial.print(b.x);
                    Serial.print(",\"y\":");
                    Serial.print(b.y);
                    Serial.print(",\"w\":");
                    Serial.print(b.w);
                    Serial.print(",\"h\":");
                    Serial.print(b.h);
                    Serial.print("}");
                    if (i < AI.boxes().size() - 1) Serial.print(",");
                }

                Serial.print("],\"image\":\"");
                Serial.print(img);
                Serial.println("\"}");
                Serial.println("-----END_FRAME-----");
            }
        }
    }
    delay(100);
}