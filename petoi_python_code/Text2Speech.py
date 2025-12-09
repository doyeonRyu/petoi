from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os

def text_to_speech_stream(text: str, lang: str = "ko"):
    tts = gTTS(text=text, lang=lang, slow=False)
    file_path = "output.mp3"
    tts.save(file_path)

    sound = AudioSegment.from_file(file_path, format="mp3")
    play(sound)

if __name__ == "__main__":
    text_to_speech_stream("안녕하세요.")
