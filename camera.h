
#define GROVE_VISION_AI_V2


#include <Arduino.h>

#define I2C_MODE
// #define SERIAL_MODE

#ifdef I2C_MODE
#include <Wire.h>
#define SENTRY2_ADDRESS 0x60
#endif

TaskHandle_t TASK_HandleCamera = NULL;
bool cameraTaskActiveQ = 0;

bool detectedObjectQ = false;
bool cameraReactionQ = true;       
bool updateCoordinateLock = false;
bool followingMode = false;
unsigned long lastSeenTime = 0;


int8_t cameraPrintQ = 0;
int xCoord = -1, yCoord = -1, width = 0, height = 0; // the x y returned by the sensor
int lastXcoord = -1, lastYcoord = -1;
int imgRangeX = 100;               // the frame size 0~100 on X and Y direction
int imgRangeY = 100;

extern TaskHandle_t TASK_imu;
extern bool updateGyroQ;
extern bool imuLockI2c;
extern bool cameraLockI2c;
extern bool gestureLockI2c;
extern bool eepromLockI2c;

#ifdef BiBoard_V1_0
#define USE_WIRE1  // use the Grove UART as the Wire1, which is independent of Wire used by the main devices, such as
                   // the gyroscope and EEPROM.
#endif

#ifdef USE_WIRE1
#define CAMERA_WIRE Wire1
#else
#define CAMERA_WIRE Wire
#endif


#define I2C_MODE
// #define SERIAL_MODE
/*
   Choose MU address here: 0x60, 0x61, 0x62, 0x63
          default address: 0x60
*/

#ifdef I2C_MODE
#include <Wire.h>
#endif


#ifdef GROVE_VISION_AI_V2
#include "Seeed_Arduino_SSCMA/src/Seeed_Arduino_SSCMA.h"
// You need to install Seeed_Arduino_SSCMA via Arduino's library manager
// or download the library as a zip from https://github.com/Seeed-Studio/Seeed_Arduino_SSCMA

// ==== Gesture Class ====
enum GestureClass : uint8_t {
    GESTURE_PAPER   = 0,
    GESTURE_ROCK    = 1,
    GESTURE_SCISSOR = 2
};

// === Vision State Machine ===
enum VisionState {
  STATE_IDLE,     // 아무것도 안보임
  STATE_FOLLOW,   // 주먹 → 따라가기
  STATE_FREEZE    // 보자기 → 멈춤 + 앉기
};
VisionState visionState = STATE_IDLE;
unsigned long lastFollowSeenTime = 0;
#endif


#define T_TUNER '>'
bool cameraSetupSuccessful = false;
int widthCounter;
int xDiff, yDiff;  // the scaled distance from the center of the frame
int currentX = 0, currentY = 0;  // the current x y of the camera's direction in the world coordinate

int8_t lensFactor, proportion, tranSpeed, pan, tilt, frontUpX, backUpX, frontDownX, backDownX, frontUpY, backUpY,
    frontDownY, backDownY, tiltBase, frontUp, backUp, frontDown, backDown;
int8_t sizePars;
#ifdef ROBOT_ARM
float adjustmentFactor = 1.5;
#else
float adjustmentFactor = 1;
#endif

#ifdef NYBBLE
int8_t nybblePars[] = {30, 11, 8, 10, 15, 60, -50, 31, -50, 45, -40, 40, -36, 0, 25, -60, 60, 16};
#else  // BITTLE or CUB
#ifdef MU_CAMERA
int8_t bittleMuPars[] = {30, 10, 8, 15, 15, 60, 80, 30, 80, 60, 30, 30, 70, 40, 40, 60, 40, -30};
#endif
#if defined GROVE_VISION_AI_V2
int8_t bittleGroveVisionPars[] = {20,
                                  20,
                                  8,
                                  10,
                                  12,
                                  int8_t(60 * adjustmentFactor),
                                  int8_t(75 * adjustmentFactor),
                                  int8_t(30 * adjustmentFactor),
                                  int8_t(75 * adjustmentFactor),
                                  20,
                                  25,
                                  10,
                                  25,
                                  0,
                                  30,
                                  60,
                                  40,
                                  -10};
#endif
#endif

int8_t *par[] = {&lensFactor, &proportion, &tranSpeed, &pan,      &tilt,      &frontUpX,
                 &backUpX,    &frontDownX, &backDownX, &frontUpY, &backUpY,   &frontDownY,
                 &backDownY,  &tiltBase,   &frontUp,   &backUp,   &frontDown, &backDown};


#ifdef GROVE_VISION_AI_V2
void groveVisionSetup();
void read_GroveVision();
#endif

int8_t *initPars;
bool cameraSetup() {
  if (!MuQ && !GroveVisionQ && !Sentry2Q) {
    return false;
  }

#ifdef NYBBLE
  initPars = nybblePars;
  sizePars = sizeof(nybblePars) / sizeof(int8_t);
#else  // BITTLE or CUB

#if defined GROVE_VISION_AI_V2 || defined SENTRY2_CAMERA
  sizePars = sizeof(bittleGroveVisionPars) / sizeof(int8_t);
  if (GroveVisionQ || Sentry2Q) {
    initPars = bittleGroveVisionPars;
    imgRangeX = 240;  // the frame size 0~240 on X and Y direction
    imgRangeY = 240;
  }
#endif
#endif
    
    // Acquire camera I2C lock and wait for other I2C operations to complete
#ifndef USE_WIRE1
    cameraLockI2c = true;  // Signal that camera wants to use I2C bus
while (
#ifdef GYRO_PIN
    imuLockI2c ||  // wait for the imu to release lock
#endif
    gestureLockI2c ||  // wait for the gesture to release lock
    eepromLockI2c)     // wait for the EEPROM operations to complete
  delay(1);
#endif

#ifdef USE_WIRE1
  CAMERA_WIRE.begin(UART_TX2, UART_RX2, 400000);
#endif
  for (byte i = 0; i < sizePars; i++)
    *par[i] = initPars[i];
  transformSpeed = 0;
  widthCounter = 0;


#ifdef GROVE_VISION_AI_V2
  if (GroveVisionQ) {
    groveVisionSetup();
  }
#endif

  fps = 0;
  loopTimer = millis();

//   Release camera I2C lock
 #ifndef USE_WIRE1
   cameraLockI2c = false;
 #endif
  return cameraSetupSuccessful;
}

void showRecognitionResult(int xCoord, int yCoord, int width, int height = -1) {
  if(!cameraTaskActiveQ) return;
  printToAllPorts(xCoord - imgRangeX / 2.0, false);  // get vision result: x axes value
  printToAllPorts('\t', false);
  printToAllPorts(yCoord - imgRangeY / 2.0, false);  // get vision result: y axes value
  printToAllPorts('\t', false);
  printToAllPorts("size = ", false);
  printToAllPorts(width, false);
  if (height >= 0) {
    printToAllPorts('\t', false);
    printToAllPorts(height, false);
  }
  printToAllPorts('\t', true);
}

#define WALK  //let the robot move its body to follow people rather than sitting at the original position
// it works the best on the table so the robot doesn't need to loop upward.
#define ROTATE

void cameraBehavior(int xCoord, int yCoord, int width) {

  // freeze 상태면 아무것도 하지 않음
  if (visionState == STATE_FREEZE) return;

  // follow 상태일 때만 걷기 제어
  if (visionState != STATE_FOLLOW) return;

  if (cameraReactionQ) {
    while (updateCoordinateLock)
      ;
  
#ifdef WALK //인식되는 물체에 따라 width값 조정
    
    if (width > 140) { // maybe a noise signal
      widthCounter++;
    }
    else {
      widthCounter = 0;
    }

    // 2) 적정 거리(30~100) → 앞으로/좌우 이동
    if (width >= 30) {        
      tQueue->addTask('k', currentX < -15 ? "wkR" : (currentX > 15 ? "wkL" : "wkF"),
                      (50 - width) * 50);  // walk towards you
//      tQueue->addTask('k', "sit");
//      tQueue->addTask('i', "");
//      currentX = 0;

    } else if (widthCounter > 3) {      
      tQueue->addTask('k', "bk", 1000);  // the robot will walk backward if you get too close!
//      tQueue->addTask('k', "sit");
//      tQueue->addTask('i', "");
      widthCounter = 0;
      currentX = 0;
      
    } else
#endif
    {
      xDiff = (xCoord - imgRangeX / 2.0);  // atan((xCoord - imgRangeX / 2.0) / (imgRangeX / 2.0)) * degPerRad;//almost the same      
      yDiff = (yCoord - imgRangeY / 2.0);  // atan((yCoord - imgRangeY / 2.0) / (imgRangeX / 2.0)) * degPerRad;
      if (abs(xDiff) > 15 || abs(yDiff) > 15) {
        xDiff = xDiff / (lensFactor / 6.0);
        yDiff = yDiff / (lensFactor / 6.0);
//        currentX = max(min(currentX - xDiff, 125), -125) / (proportion / 10.0);
        currentX = currentX - xDiff * 1.2;     // 변화량 강화
        currentX = constrain(currentX, -40, 40); // 너무 커지지 않게 제한

        currentY = max(min(currentY - yDiff, 125), -125) / (proportion / 10.0);

        // PT('\t');
        // PT(currentX);

        // ===== DEBUG =====
        Serial.print("[RAW] xCoord="); Serial.print(xCoord);
        Serial.print(" xDiffRaw="); Serial.print(xCoord - imgRangeX/2);
        Serial.print("  visionState="); Serial.println(visionState);
    
        Serial.print("[ADJ] xDiff="); Serial.print(xDiff);
        Serial.print(" currentX="); Serial.println(currentX);
        // =================
        // PT('\t');
        // PTL(currentY);

        // if (abs(currentX) < 60) {
        int8_t base[] = {0,       tiltBase, 0,      0,      0,         0,         0,        0,
                         frontUp, frontUp,  backUp, backUp, frontDown, frontDown, backDown, backDown};
        int8_t feedBackArray[][2] = {
            {pan, 0},
            {0, tilt},
            {0, 0},
            {0, 0},
            {0, 0},
            {0, 0},
            {0, 0},
            {0, 0},
            {frontUpX, (int8_t)-frontUpY},  // explicitly convert the calculation result to int8_t
            {(int8_t)-frontUpX, (int8_t)-frontUpY},
            {(int8_t)-backUpX, backUpY},
            {backUpX, backUpY},
            {(int8_t)-frontDownX, frontDownY},
            {frontDownX, frontDownY},
            {backDownX, (int8_t)-backDownY},
            {(int8_t)-backDownX, (int8_t)-backDownY},
        };
        transformSpeed = tranSpeed / 4.0;
        for (int i = 0; i < DOF; i++) {
          float adj = float(base[i]) + (feedBackArray[i][0] ? currentX * 10.0 / feedBackArray[i][0] : 0)
                      + (feedBackArray[i][1] ? currentY * 10.0 / feedBackArray[i][1] : 0);
          newCmd[i] = min(125, max(-125, int(adj)));
          // if (i == 0)//print adjustment of head pan joint
          // {
          //   PT(i);
          //   PT('\t');
          //   PT(adj);
          //   PT('\t');
          //   PT(int8_t(newCmd[i]));
          //   PTF(",\t");
          // }
        }
        // PTL();
        // newCmd[16] = '~';
        // printList((int8_t *)newCmd);
        transform((int8_t *)newCmd, 1, transformSpeed);
        token = '\0';  // avoid  conflicting with the balancing reaction
      }  
#ifdef ROTATE
      else {
          tQueue->addTask('k', (currentX < 0 ? "vtR" : "vtL"), abs(currentX) * 60);  // spin its body to follow you
          currentX = 0;
      }
#endif
      
    }
  }
}

int coords[3];

void taskReadCamera(void *par) {
  // PTHL("cameraTaskActiveQ = ", cameraTaskActiveQ);
  while (cameraTaskActiveQ) {
    // PTHL("imuLockI2c = ", imuLockI2c);
    // PTHL("gestureLockI2c = ", gestureLockI2c);
    // PTHL("eepromLockI2c = ", eepromLockI2c);
#ifndef USE_WIRE1
    while (
#ifdef GYRO_PIN
        imuLockI2c ||  // wait for the imu to release lock. potentially to cause dead lock with camera
#endif
        gestureLockI2c ||  // wait for the gesture to release lock. potentially to cause dead lock with camera
        eepromLockI2c)     // wait for the EEPROM operations to complete
      delay(1);
    cameraLockI2c = true;
#endif
    if (xCoord != lastXcoord || yCoord != lastYcoord) {
      lastXcoord = xCoord;
      lastYcoord = yCoord;
    }

#ifdef GROVE_VISION_AI_V2
    if (GroveVisionQ)
      read_GroveVision();
#endif

    cameraLockI2c = false;

    // for checking the size of unused stack space
    // vTaskDelay(50 / portTICK_PERIOD_MS);  
    // Serial.println("Stack high water mark: " + String(uxTaskGetStackHighWaterMark(NULL)) + " bytes");
  }
  vTaskDelete(NULL);
}

void read_camera() {
  if (!cameraTaskActiveQ) {
    // Serial.print("Free heap: ");
    // Serial.println(ESP.getFreeHeap());
    PTLF("Create Camera Task...");
    BaseType_t result = xTaskCreatePinnedToCore(
      taskReadCamera,      // task function
      "TaskReadCamera",    // task name
      6000,                // task stack size​​
      NULL,                // parameters
      0,                   // priority
      &TASK_HandleCamera,  // handle
      0);                  // core
    if (result == pdPASS) {
      Serial.println("Camera task created successfully");
    } else {
      Serial.println("Failed to create camera task, error code: " + String(result));
    }
    cameraTaskActiveQ = 1;
    PTLF("Camera task activated.");
  }

  if (detectedObjectQ) {
    cameraBehavior(xCoord, yCoord, width);
    detectedObjectQ = false;
  }
}

#ifdef GROVE_VISION_AI_V2
SSCMA AI;

// OPT_ANGLE values
enum OptAngle : uint16_t {
  OPT_ANGLE_0 = 0,
  OPT_ANGLE_90 = 0xffff & (1 << 12),
  OPT_ANGLE_180 = 0xffff & (1 << 13),
  OPT_ANGLE_270 = 0xffff & (1 << 14),
};

// OPT_DETAIL values
enum OptResolution : uint8_t {
  OPT_DETAIL_240 = 0,  // 240*240 Auto
  OPT_DETAIL_480,  // 480*480 Auto
  OPT_DETAIL_640,  // 640*480 Auto
};
void groveVisionSetup() {
  PTLF("Setup Grove Vision AI Module");
  // CAMERA_WIRE.begin(10, 9, 400000);
  
  // End the TASK_imu task when activating Grove Vision AI V2
#ifdef GYRO_PIN
  if (TASK_imu != NULL) {
    while (eTaskGetState(TASK_imu) != eDeleted) {
      PTHL("task state:", eTaskGetState(TASK_imu));
//      if (eTaskGetState(TASK_imu) == eReady) {      Task 포인터를 NULL로 만든 것
//        TASK_imu = NULL;
//        break;
//      }
        if (TASK_imu != NULL) {                       //메모리 삭제
          vTaskDelete(TASK_imu);
          TASK_imu = NULL;
        }

      vTaskDelay(100 / portTICK_PERIOD_MS);
    }
  }
#endif

  // Adjust I2C clock frequency, reduce to improve stability
  CAMERA_WIRE.setClock(100000); // Reduce to 100kHz, more stable than default 400kHz
  
  // Wait longer before initializing AI module
  Serial.println("Waiting for Grove Vision AI to boot...");
  delay(1500); // 🔸 extended delay to ensure module is ready

  // 🔹 Check whether device is ready (without AI.ping)
  bool ready = false;
  for (int i = 0; i < 50; i++) { // up to ~5s
    CAMERA_WIRE.beginTransmission(0x62);
    if (CAMERA_WIRE.endTransmission() == 0) {
      delay(1000);
      ready = true;
      Serial.println("✅ Grove Vision AI I2C device detected!");
      break;
    }
    delay(100);
  }

  if (!ready) {
    Serial.println("⚠ Grove Vision AI not ready after waiting!");
  }



  // ✅ 여기서 Heap 메모리 확인!
  Serial.print("Free heap before AI.begin(): ");
  Serial.println(ESP.getFreeHeap());


  

  Serial.println("Initializing Grove Vision AI Module...");
  bool aiInitSuccess = false;
  
  // Method 1: Try standard initialization
  if (AI.begin(&CAMERA_WIRE)) {  
    aiInitSuccess = true;
    Serial.println("Standard AI.begin() succeeded!");
  } else {
    Serial.println("Standard AI.begin() failed, using manual method...");
    
    // Method 2: Manual initialization (more reliable under Bluetooth interference)
    AI.set_rx_buffer(4096);  // 8KB receive buffer
    AI.set_tx_buffer(512);  // 1KB transmit buffer
    
    // Manually set sensor parameters
    uint8_t result = AI.setSensor(true, OPT_DETAIL_240 + OPT_ANGLE_90);
    Serial.printf("Manual init result: 0x%02X\n", result);
    if (result == CMD_OK) {
      aiInitSuccess = true;
      Serial.println("Manual initialization succeeded!");
    } else {
      Serial.println("Manual initialization failed!");
    }
  }
  
  if (!aiInitSuccess) {
    Serial.println("❌ AI module initialization failed!");
    Serial.println("Please check power stability and wiring (0x03 = not ready).");
    return;
  }

  uint8_t count = 0;
  bool sensorEnable = true;
  uint16_t sensorVal =
      OPT_DETAIL_240
      + (strcmp(MODEL, "Bittle X+Arm") ? OPT_ANGLE_90 : OPT_ANGLE_0);  // 240*240, rotate 90° if Bittle R

  Serial.println("Set sensor angle and resolution...");
  do {
    delay(10);
    uint8_t res = AI.setSensor(sensorEnable, sensorVal);
    if (res == CMD_OK) {
      cameraSetupSuccessful = true;
      Serial.println("✅ Sensor configured successfully!");
      break;
    }
    count++;
    PTHL("count:", count);
  } while (count < 3);

  if (!cameraSetupSuccessful)
    Serial.println("⚠ Failed to configure sensor after retries.");
    
}






void read_GroveVision() {  
  if (!cameraSetupSuccessful) return;
  if (AI.invoke()) return;   // invoke 실패면 반환

  if (AI.boxes().size() >= 1) {
    // === 가장 큰 박스 선택 (노이즈 제거) ===
    int bestIdx = -1;
    int bestArea = -1;
    for (int i = 0; i < AI.boxes().size(); i++) {
      int area = AI.boxes()[i].w * AI.boxes()[i].h;
      if (area > bestArea) {
        bestArea = area;
        bestIdx = i;
      }
    }

    auto &b = AI.boxes()[bestIdx];
    GestureClass gesture = (GestureClass)b.target;   // 0=보자기, 1=주먹, 2=가위

    // === 디버깅 출력 ===
    const char* gestureName = 
        (gesture == GESTURE_PAPER)   ? "Paper" :
        (gesture == GESTURE_ROCK)    ? "Rock"  :
        (gesture == GESTURE_SCISSOR) ? "Scissor" :
                                       "Unknown";
      
    Serial.print("Gesture Detected: ");
    Serial.println(gestureName);

    // === 상태 전환 로직 ===
    if (gesture == GESTURE_PAPER) {
      if (visionState != STATE_FREEZE) {   // 중복 금지
         tQueue->clear();
         tQueue->addTask('k', "d");   
         tQueue->addTask('k', "sit", 300);
      }
      visionState = STATE_FREEZE;
      return;
        
    } else if (gesture == GESTURE_ROCK) {
        
      // 주먹 → 따라오기 모드 활성화
      visionState = STATE_FOLLOW;   // freeze 상태 → follow로 전환

      // 따라오기 위해 좌표 업데이트
      updateCoordinateLock = true;
      xCoord = b.x;
      yCoord = b.y;
      width = b.w;
      height = b.h;
      updateCoordinateLock = false;
      detectedObjectQ = true;  // → cameraBehavior() 호출 트리거
      lastSeenTime = millis();
      return;
      
    } else {
      // 가위(2) → 무시
      // 따라오는 중이면 손 사라진 것으로 처리 X
      lastSeenTime = millis();
      return;
    }
    if (cameraPrintQ == 2 && cameraTaskActiveQ) {
      FPS();
    }
      
  } else {
    // 박스가 하나도 없음 → 손 사라짐 감지
    if (visionState == STATE_FOLLOW) {
      if (millis() - lastSeenTime > 400) {  // 0.4초 동안 손 없음
          visionState = STATE_IDLE;
          tQueue->addTask('k', "d");
      }
    }
  }
}

#endif
