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


import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import os

def text_to_speech_stream(text: str):
    async def _run():
        # 음성 설정
        voice = "ko-KR-SunHiNeural"
        output_file = os.path.join(os.getcwd(), "Output.mp3")

        # TTS 변환 및 저장
        tts = edge_tts.Communicate(text, voice=voice)
        await tts.save(output_file)

        # 파일 재생
        sound = AudioSegment.from_file(output_file, format="mp3")
        play(sound)

    try:
        asyncio.run(_run())
    except RuntimeError as e:
        # 이미 이벤트 루프가 돌고 있을 때 대체 실행
        if "event loop is running" in str(e).lower():
            loop = asyncio.get_event_loop()
            loop.create_task(_run())
        else:
            print(f"[TTS 오류] {e}")
    except Exception as e:
        print(f"[TTS 오류] {e}")