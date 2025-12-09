import speech_recognition as sr

def listen_and_transcribe():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='ko-KR')
        print(f"{text}")
        return text

    except sr.UnknownValueError:
        # 음성을 이해하지 못했을 때 안내 메시지
        print("[SYSTEM] 음성을 인식하지 못했습니다. 다시 시도해주세요.")
        return ""
    except sr.RequestError:
        print("[SYSTEM] 서비스에 연결할 수 없습니다.")
        return ""

if __name__ == "__main__":
    listen_and_transcribe()