import speech_recognition as sr
from Text2Speech import text_to_speech_stream

def listen_and_transcribe():
    recognizer = sr.Recognizer() # Recognizer 객체 생성
    microphone = sr.Microphone() # Microphone 객체 생성

    # 마이크로부터 오디오 캡처
    with microphone as source:
        print("Talk...")
        # 마이크로부터 오디오 캡처
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Google의 음성 인식 API를 사용하여 음성을 텍스트로 변환
        text = recognizer.recognize_google(audio, language='ko-KR')
        return text
    except sr.UnknownValueError:
        text="Sory I could not understand audio."
        return text
    except sr.RequestError:
        print("Servise was not found")

if __name__ == "__main__":
    listen_and_transcribe()


