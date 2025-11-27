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