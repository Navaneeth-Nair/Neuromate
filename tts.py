# tts.py
import pyttsx3
import keyboard

def speak():
    keyboard.block_key('enter')
    keyboard.block_key('esc')
    with open("response.txt",'r',encoding='utf-8') as tetovoice:
        text = tetovoice.read().strip()

    engine = pyttsx3.init()
    engine.setProperty("rate", 250)
    engine.setProperty("volume", 1.0)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id if len(voices) > 1 else voices[0].id)
    engine.say(text)
    engine.runAndWait()
    open('response.txt', 'w').close()
    keyboard.unblock_key('enter')
    keyboard.unblock_key('esc')
    


if __name__ == "__main__":
    speak()

