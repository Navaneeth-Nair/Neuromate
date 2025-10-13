#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import shutil
import threading
import time
import wave
from pathlib import Path
from typing import Optional, Tuple, List

try:
	from pydub import AudioSegment
except Exception:
	AudioSegment = None

try:
	import pyaudio
except Exception:
	pyaudio = None

try:
	import keyboard
except Exception:
	keyboard = None

try:
	import speech_recognition as sr
except Exception:
	sr = None

try:
	from textblob import Word
except Exception:
	Word = None


def ensure_ffmpeg_available():
	if AudioSegment is None:
		return False, "pydub not installed"
	ffmpeg_path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
	if ffmpeg_path:
		return True, ffmpeg_path
	return False, "ffmpeg not found in PATH"


def preprocess_audio(input_path: str, dest_path: str, target_sr: int = 22050) -> None:
	if AudioSegment is None:
		raise RuntimeError("pydub is required for audio preprocessing")
	ok, info = ensure_ffmpeg_available()
	if not ok:
		raise RuntimeError(f"ffmpeg required but not available: {info}")
	audio = AudioSegment.from_file(input_path)
	audio = audio.normalize()
	audio = audio.high_pass_filter(80)
	audio = audio.set_frame_rate(target_sr).set_channels(1)
	audio = audio.set_sample_width(2)
	audio.export(dest_path, format="wav")


def try_noise_reduction(wav_path: str) -> Optional[str]:
	try:
		import librosa
		import noisereduce as nr
		import soundfile as sf
	except Exception:
		return None
	y, sr = librosa.load(wav_path, sr=None)
	noise_clip = y[: int(sr * 0.5)]
	reduced = nr.reduce_noise(y=y, sr=sr, y_noise=noise_clip)
	out = wav_path.replace('.wav', '.nr.wav')
	sf.write(out, reduced, sr)
	return out


def auto_expand(text: str) -> str:
	if Word is None:
		return text.strip()
	
	fixed = []
	for w in text.split():
		suggestion = Word(w).correct()
		fixed.append(str(suggestion))
	return " ".join(fixed)

def transcribe_audio_simple(wav_path: str) -> str:
	if sr is None:
		return "SpeechRecognition library not available"
	
	recognizer = sr.Recognizer()
	recognizer.energy_threshold = 100
	recognizer.dynamic_energy_threshold = False
	recognizer.pause_threshold = 1.5
	recognizer.phrase_threshold = 0.1
	recognizer.non_speaking_duration = 1.0
	
	try:
		print("Loading audio file...")
		with sr.AudioFile(wav_path) as source:
			print("Reading audio data...")
			recognizer.adjust_for_ambient_noise(source, duration=0.5)
			audio_data = recognizer.record(source)
			print("Audio data loaded successfully")
			
			try:
				print("Trying Google Speech Recognition...")
				text = recognizer.recognize_google(
					audio_data, 
					language='en-US',
					show_all=False,
					with_confidence=False
				)
				if text.strip():
					return auto_expand(text.strip())
				else:
					print("Google returned empty result, trying alternative...")
					text = recognizer.recognize_google(audio_data, language='en-IN')
					if text.strip():
						return auto_expand(text.strip())
					else:
						return "No speech detected"
					
			except sr.RequestError as e:
				print(f"Google service error: {e}")
				try:
					print("Trying offline recognition...")
					text = recognizer.recognize_sphinx(audio_data)
					if text.strip():
						return auto_expand(text.strip())
					else:
						return "No speech detected (offline)"
				except sr.RequestError as e2:
					return f"All recognition services failed: {e2}"
				except Exception as e2:
					return f"Offline recognition error: {e2}"
			except sr.UnknownValueError:
				print("Trying with adjusted settings...")
				recognizer.energy_threshold = 100
				try:
					with sr.AudioFile(wav_path) as source2:
						audio_data2 = recognizer.record(source2)
						text = recognizer.recognize_google(audio_data2, language='en-US')
						if text.strip():
							return auto_expand(text.strip())
						else:
							return "Could not understand audio clearly"
				except:
					return "Could not understand the audio clearly"
			except Exception as e:
				print(f"Google recognition error: {e}")
				return f"Recognition failed: {e}"
	
	except Exception as e:
		return f"Error processing audio file: {e}"


def write_text(output_path: str, text: str) -> None:
	Path(output_path).write_text(text, encoding="utf-8")


def write_srt(output_path: str, segments: List[dict]) -> None:
	def fmt(t: float) -> str:
		hrs = int(t // 3600)
		mins = int((t % 3600) // 60)
		secs = int(t % 60)
		ms = int((t - int(t)) * 1000)
		return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"
	lines = []
	for i, s in enumerate(segments, start=1):
		lines.append(str(i))
		lines.append(f"{fmt(s['start'])} --> {fmt(s['end'])}")
		lines.append(s['text'].strip())
		lines.append("")
	Path(output_path).write_text("\n".join(lines), encoding="utf-8")


class AudioRecorder:
	def __init__(self, sample_rate=44100, channels=1, chunk_size=4096):
		if pyaudio is None:
			raise RuntimeError("pyaudio is required for recording")
		self.sample_rate = sample_rate
		self.channels = channels
		self.chunk_size = chunk_size
		self.format = pyaudio.paInt16
		self.audio = pyaudio.PyAudio()
		self.frames = []
		self.is_recording = False
		self.stream = None
	
	def start_recording(self):
		if self.is_recording:
			return
		
		self.frames = []
		self.is_recording = True
		
		self.stream = self.audio.open(
			format=self.format,
			channels=self.channels,
			rate=self.sample_rate,
			input=True,
			frames_per_buffer=self.chunk_size
		)
		
		print("Recording started... Press 'M' again to stop.")
		
		def record():
			while self.is_recording:
				try:
					data = self.stream.read(self.chunk_size, exception_on_overflow=False)
					self.frames.append(data)
				except Exception as e:
					print(f"Recording error: {e}")
					break
		
		self.record_thread = threading.Thread(target=record)
		self.record_thread.start()
	
	def stop_recording(self):
		if not self.is_recording:
			return
		
		self.is_recording = False
		if self.record_thread:
			self.record_thread.join()
		
		if self.stream:
			self.stream.stop_stream()
			self.stream.close()
		
		print("Recording stopped.")
	
	def save_recording(self, output_path: str):
		if not self.frames:
			print("No audio data to save.")
			return False
		
		with wave.open(output_path, 'wb') as wf:
			wf.setnchannels(self.channels)
			wf.setsampwidth(self.audio.get_sample_size(self.format))
			wf.setframerate(self.sample_rate)
			wf.writeframes(b''.join(self.frames))
		
		print(f"Recording saved to: {output_path}")
		return True
	
	def cleanup(self):
		if self.is_recording:
			self.stop_recording()
		if self.audio:
			self.audio.terminate()


def start_recording_mode():
	if keyboard is None:
		print("Error: 'keyboard' package is required for recording mode.")
		print("Install it with: pip install keyboard")
		return
	
	if pyaudio is None:
		print("Error: 'pyaudio' package is required for recording mode.")
		print("Install it with: pip install pyaudio")
		return
	
	recorder = AudioRecorder()
	
	print("Recording Mode Active")
	print("Press 'M' to start/stop recording and get transcription")
	print("Press 'Q' to quit recording mode")
	
	try:
		while True:
			event = keyboard.read_event()
			if event.event_type == keyboard.KEY_DOWN:
				key = event.name.lower()
				
				if key == 'm':
					if not recorder.is_recording:
						recorder.start_recording()
					else:
						recorder.stop_recording()
						transcribe_recording_direct(recorder)
				
				elif key == 'q':
					print("Exiting recording mode...")
					break
	
	except KeyboardInterrupt:
		print("\nExiting recording mode...")
	
	finally:
		recorder.cleanup()


def transcribe_recording_direct(recorder: AudioRecorder):
	try:
		if not recorder.frames:
			print("No audio data to transcribe.")
			return
		
		print("Transcribing recording...")
		
		with tempfile.TemporaryDirectory() as td:
			# Create temporary file just for processing
			temp_wav = os.path.join(td, "temp_recording.wav")
			
			# Save to temporary file
			with wave.open(temp_wav, 'wb') as wf:
				wf.setnchannels(recorder.channels)
				wf.setsampwidth(recorder.audio.get_sample_size(recorder.format))
				wf.setframerate(recorder.sample_rate)
				wf.writeframes(b''.join(recorder.frames))
			
			processed_wav = os.path.join(td, "processed.wav")
			preprocess_audio(temp_wav, processed_wav)
			text = transcribe_audio_simple(processed_wav)
			print("\nTRANSCRIPTION:")
			print(text)
			recorder.frames = []
	
	except Exception as e:
		print(f"Transcription failed: {e}")


def transcribe_recording(recording_path: str):
	try:
		with tempfile.TemporaryDirectory() as td:
			temp_wav = os.path.join(td, "recording.wav")
			preprocess_audio(recording_path, temp_wav)
			
			text = transcribe_audio_simple(temp_wav)
			print("\nTRANSCRIPTION:")
			print(text)
	
	except Exception as e:
		print(f"Transcription failed: {e}")


def main(argv=None):
	p = argparse.ArgumentParser(prog="transcribe")
	p.add_argument("--input", "-i", required=False)
	p.add_argument("--output", "-o", required=False)
	p.add_argument("--language", "-l", default=None)
	p.add_argument("--model", default=None)
	p.add_argument("--noisereduce", action="store_true")
	p.add_argument("--srt", action="store_true")
	p.add_argument("--record", "-r", action="store_true", help="Start recording mode (press M to record)")
	args = p.parse_args(argv)
	
	if args.record:
		start_recording_mode()
		return
	
	if not args.input:
		print("Error: --input is required when not using --record mode")
		print("Use --record to start recording mode, or provide --input for file transcription")
		sys.exit(1)
	
	inp = Path(args.input)
	if not inp.exists():
		print(f"Input file not found: {inp}")
		sys.exit(2)
	out_path = args.output or str(inp.with_suffix('.txt'))
	with tempfile.TemporaryDirectory() as td:
		temp_wav = os.path.join(td, "input.wav")
		preprocess_audio(str(inp), temp_wav)
		if args.noisereduce:
			nr = try_noise_reduction(temp_wav)
			if nr:
				temp_wav = nr
		text = transcribe_audio_simple(temp_wav)
		write_text(out_path, text)
		print(f"Transcription saved to: {out_path}")


if __name__ == '__main__':
	main()

