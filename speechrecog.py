#!/usr/bin/env python3
import speech_recognition as sr
import keyboard
import pyaudio
import tempfile
import os
import wave
import audioop
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
    keyboard.wait(key)
    print("Recording... Release key to stop.")
    while keyboard.is_pressed(key):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)
    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    raw = b"".join(frames)
    rms = audioop.rms(raw, 2)
    target_rms = 250
    if rms > 0:
        ratio = target_rms / rms
        raw = audioop.mul(raw, 2, ratio)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(raw)

    duration = len(raw) / (rate * 2)
    final_rms = audioop.rms(raw, 2)
    print(f"Audio length: {duration:.2f}s | Loudness (RMS): {final_rms}")
    return raw, rate


def transcribe_audio(raw_bytes, rate):
    recognizer = sr.Recognizer()
    audio_data = sr.AudioData(raw_bytes, rate, 2)
    try:
        print("Transcribing...")
        text = recognizer.recognize_google(audio_data, language="en-US")
        print(f"\nYou said: {text}\n")
        with open("client_question.txt", "w", encoding="utf-8") as f:
            f.write(text.strip())
        return text.strip()
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Connection error: {e}")
        return None


def main():
    print(">>> Hold ENTER to record, release to stop. Press ESC to quit.\n")
    while True:
        if keyboard.is_pressed("esc"):
            print("Exiting...")
            break
        if keyboard.is_pressed("enter"):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                filename = tmp.name
            raw, rate = record_while_key_held(filename)
            text = transcribe_audio(raw, rate)
            if os.path.exists(filename):
                os.unlink(filename)
            if text:
                ai.response()
                speak.speak()
            keyboard.wait("enter")


if __name__ == "__main__":
    main()
