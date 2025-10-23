import asyncio, edge_tts

async def list_ko_voices():
    voices = await edge_tts.list_voices()
    for v in voices:
        if v["Locale"].lower() == "ko-kr":
            print(v["ShortName"])

asyncio.run(list_ko_voices())
# ko-KR-AriyaNeural, ko-KR-InJoonNeural, ko-KR-SunHiNeural 등이 출력되면 사용 가능
