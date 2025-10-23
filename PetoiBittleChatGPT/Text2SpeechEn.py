# import requests
# import base64
# from pydub import AudioSegment
# from pydub.playback import play
# import io

# def text_to_speech_stream(text):
#     api_key = "AIzaSyC17dnNbnSO6WRa6ZNgwJDgfrCSUThqidc"
#     # Google Text-to-Speech API endpoint
#     url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"

#     # İstek verisi (JSON formatında)
#     data = {
#         "input": {"text": text},
#         "voice": {
#             "languageCode": "en-US",  # Türkçe dil kodu
#             "ssmlGender": "MALE"  # Erkek sesi
#         },
#         "audioConfig": {
#             "audioEncoding": "MP3",  # Çıkış formatı MP3
#             "speakingRate": 1  # Konuşma hızı
#         }
#     }

#     # Send post request to api
#     response = requests.post(url, json=data)

#     # Check the response
#     if response.status_code == 200:
#         # Get the voice
#         audio_content = response.json().get("audioContent")

#         if audio_content:

#             audio_data = base64.b64decode(audio_content)


#             audio_stream = io.BytesIO(audio_data)


#             sound = AudioSegment.from_file(audio_stream, format="mp3")
#             play(sound)
#         else:
#             print("Error:")
#     else:
#         print(f"Error: {response.status_code}")
#         print(response.text)


# import asyncio
# import edge_tts
# from pydub import AudioSegment
# from pydub.playback import play
# import os

# def text_to_speech_stream(text: str):
#     async def _run():
#         # 음성 설정
#         voice = "ko-KR-SunHiNeural"
#         output_file = os.path.join(os.getcwd(), "Output.mp3")

#         # TTS 변환 및 저장
#         tts = edge_tts.Communicate(text, voice=voice)
#         await tts.save(output_file)

#         # 파일 재생
#         sound = AudioSegment.from_file(output_file, format="mp3")
#         play(sound)

#     try:
#         asyncio.run(_run())
#     except RuntimeError as e:
#         # 이미 이벤트 루프가 돌고 있을 때 대체 실행
#         if "event loop is running" in str(e).lower():
#             loop = asyncio.get_event_loop()
#             loop.create_task(_run())
#         else:
#             print(f"[TTS 오류] {e}")
#     except Exception as e:
#         print(f"[TTS 오류] {e}")

import asyncio
import edge_tts
from pydub import AudioSegment
import os

'''
함수 설명:
    전달한 텍스트를 edge-tts로 음성 합성(MP3)한 뒤,
    ESP32 내장 DAC 재생에 적합한 WAV(PCM 16kHz/16bit/모노)로 변환하여 저장하고
    (옵션) 로컬 장치에서 aplay로 재생한다.

입력값:
    text: str
        - TTS로 변환할 텍스트
    wav_path: str (기본값 "output.wav")
        - 최종 저장할 WAV 파일 경로 (ESP32에서는 SPIFFS에 "/output.wav"로 업로드해서 사용)
    voice: str (기본값 "ko-KR-SunHiNeural")
        - edge-tts 음성 이름
    sample_rate: int (기본값 16000)
        - WAV 샘플레이트(ESP32 DAC 안정권: 16000 권장)
    channels: int (기본값 1)
        - 채널 수(모노=1)
    play_locally: bool (기본값 False)
        - True면 로컬 장치에서 aplay로 즉시 재생
    alsa_device: str | None (기본값 None)
        - 로컬 재생 시 사용할 ALSA 디바이스. 예: "plughw:1,0"
        - None이면 기본 장치 사용

출력값:
    str
        - 생성된 WAV 파일 경로
'''

def text_to_speech_stream(
    text: str,
    wav_path: str = "output.wav",
    voice: str = "ko-KR-SunHiNeural",
    sample_rate: int = 16000,
    channels: int = 1,
    play_locally: bool = False,
    alsa_device: str | None = None,
) -> str:
    # 내부 비동기 함수 정의
    async def _run():
        # 1) 임시 MP3 경로 설정
        mp3_path = os.path.join(os.getcwd(), "_edge_tts_tmp.mp3")

        # 2) edge-tts로 MP3 생성
        #    - edge-tts는 기본적으로 MP3로 저장되므로 일단 MP3로 받은 뒤 WAV로 변환
        tts = edge_tts.Communicate(text, voice=voice)
        await tts.save(mp3_path)

        # 3) MP3 → WAV(PCM 16kHz/16bit/모노) 변환
        #    - pydub은 ffmpeg 필요(사전 설치 필수: sudo apt install ffmpeg)
        sound = AudioSegment.from_file(mp3_path, format="mp3")  # MP3 파일 로드
        sound = sound.set_frame_rate(sample_rate)               # 샘플레이트 16kHz로 설정
        sound = sound.set_sample_width(2)                       # 16-bit(=2byte) PCM
        sound = sound.set_channels(channels)                    # 모노(1)
        sound.export(wav_path, format="wav")                    # WAV로 저장

        print(f"[변환 완료] {wav_path}")

        # 4) (옵션) 로컬에서 즉시 재생
        if play_locally:
            # aplay로 재생(장치 지정 시 -D 추가)
            if alsa_device:
                os.system(f'aplay -D {alsa_device} "{wav_path}"')
            else:
                os.system(f'aplay "{wav_path}"')

        # 5) 임시 MP3 정리
        try:
            os.remove(mp3_path)
        except OSError:
            pass

        return wav_path

    # 이벤트 루프 처리(주피터/비동기 환경 대비)
    try:
        return asyncio.run(_run())
    except RuntimeError as e:
        if "event loop is running" in str(e).lower():
            loop = asyncio.get_event_loop()
            task = loop.create_task(_run())
            # 주의: 호출측에서 event loop가 끝날 때까지 기다리거나, 콜백으로 결과 사용
            return wav_path  # 즉시 경로 반환(실제 완료는 비동기)
        else:
            raise

# 사용 예시:
# wav = text_to_speech_stream(
#     "안녕하세요. 테스트 음성입니다.",
#     wav_path="output.wav",        # ESP32에는 SPIFFS에 /output.wav로 업로드
#     voice="ko-KR-SunHiNeural",
#     sample_rate=16000,
#     channels=1,
#     play_locally=False,           # 라즈베리파이에서 바로 들어보려면 True
#     alsa_device="plughw:1,0"      # I2S 카드라면 예: "plughw:1,0"
# )
# print("WAV 저장:", wav)
