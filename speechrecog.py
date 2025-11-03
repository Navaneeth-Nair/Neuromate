#!/usr/bin/env python3
import speech_recognition as sr
import keyboard
import pyaudio
import wave
import tempfile
import os

def record_while_key_held(filename="temp.wav", key="enter", rate=16000, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    print(f"Hold '{key.upper()}' to record...")

    keyboard.wait(key)
    print("Recording... Release key to stop.")

    while keyboard.is_pressed(key):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    return filename

def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print("\nYou said:", text)
        with open("client_question.txt", "w", encoding="utf-8") as f:
            f.write(text.strip())
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

def main():
    print("Hold Enter to record, release to stop. Press Esc to quit.\n")
    while True:
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break
        if keyboard.is_pressed('enter'):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                filename = tmp.name
            record_while_key_held(filename)
            transcribe_audio(filename)
            os.unlink(filename)

if __name__ == "__main__":
    main()
