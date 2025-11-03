#!/usr/bin/env python3
import speech_recognition as sr
import keyboard
import pyaudio
import wave
import tempfile
import os
import ai_chat as ai
import tts as speak

def record_while_key_held(filename="temp.wav", key="enter", rate=16000, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    print(f"\nHold '{key.upper()}' to record...")

    # Wait for key press
    keyboard.wait(key)
    print("Recording... Release key to stop.")

    # Record while key is held down
    while keyboard.is_pressed(key):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save to WAV file
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
        return text.strip()
    except sr.UnknownValueError:
        print(" Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None


def main():
    print("🎙️ Hold ENTER to record, release to stop. Press ESC to quit.\n")

    while True:
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break

        # Wait until the Enter key is pressed
        if keyboard.is_pressed('enter'):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                filename = tmp.name

            # Record and transcribe
            record_while_key_held(filename)
            text = transcribe_audio(filename)

            # Delete the temp file safely
            if os.path.exists(filename):
                os.unlink(filename)

            # If transcription succeeded, generate AI response
            if text:
                ai.response()
                speak.speak()

            # Prevent retriggering too fast
            keyboard.wait('enter')  # Wait until Enter is released

if __name__ == "__main__":
    main()
