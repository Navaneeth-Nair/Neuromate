import requests
import concurrent.futures
from queue import Queue
import threading
import os
import sounddevice as sd
import soundfile as sf
import yaml
import re
from gradio_client import Client, file

def call_api(sentence, **kwargs):
    '''
    Makes a request to the Tortoise TTS GUI. Relies on tort.yaml, so make sure it's set-up

    Args:
        Various arguments for TTS conversion

    Returns:
        audio_path (str): Path of the audio to be played
    '''
    start_port = 7860
    tries = 0

    while tries < 3:
        try:
            url = f"http://localhost:{start_port}/"
            client = Client(url, verbose=False)
            
            print("Parameters being sent to Gradio app:")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

            result = client.predict(
                sentence,  
                kwargs.get("delimiter", "\n"),  
                kwargs.get("emotion", "None"),  
                kwargs.get("custom_emotion", ""),  
                kwargs.get("voice_name", "mel"),  
                None,  
                kwargs.get("voice_chunks", 0),  
                kwargs.get("candidates", 1),  
                kwargs.get("seed", 0),  
                kwargs.get("samples", 1),  
                kwargs.get("iterations", 32),  
                kwargs.get("temperature", 0.8),  
                kwargs.get("diffusion_sampler", "DDIM"),  
                kwargs.get("pause_size", 8),  
                kwargs.get("cvvp_weight", 0),  
                kwargs.get("top_p", 0.8),  
                kwargs.get("diffusion_temp", 1),  
                kwargs.get("length_penalty", 6),  
                kwargs.get("repetition_penalty", 6),  
                kwargs.get("conditioning_free_k", 2),  
                kwargs.get("experimental_flags", ["Half Precision", "Conditioning-Free"]),  
                kwargs.get("use_original_latents_ar", True),  
                kwargs.get("use_original_latents_diffusion", True),  
                api_name="/generate"
            )
            client.close()
            
            return result[0]
            
        except Exception as e:
            tries += 1
            start_port += 1
            print(f"Error: {e}, retrying... ({tries}/3)")

    raise Exception("API call failed after 3 attempts")


def load_config(tort_yaml_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    with open(tort_yaml_path, "r") as file:
        tort_conf = yaml.safe_load(file)

    return tort_conf

import re

def filter_paragraph(paragraph):
    lines = paragraph.strip().split('\n')
    
    filtered_list = []
    i = 0
    while i < len(lines):
        split_sentences = lines[i].split('. ')
        for part_sentence in split_sentences:
            if not part_sentence:
                continue

            line = part_sentence.strip()

            while line.endswith(",") and (i + 1) < len(lines):
                i += 1
                line += " " + lines[i].split('. ')[0].strip()

            
            line = re.sub(r'\[|\]', '', line).strip()

            
            if line and any(c.isalpha() for c in line):
                filtered_list.append(line)

        i += 1

    return filtered_list


def load_sentences(file_path) -> list:
    '''
    Utility function for toroise to load sentences from a text file path

    Args:
        file_path(str) : path to some text file

    '''
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        paragraphs = content.split('\n\n')  
        filtered_sentences = []
        for paragraph in paragraphs:
            filtered_list = filter_paragraph(paragraph)
            filtered_sentences.extend(filtered_list)
    return filtered_sentences

def read_paragraph_from_file(file_path):
    with open(file_path, 'r') as file:
        paragraph = file.read()
    return paragraph

if __name__ == "__main__":
    
    
    
    
    
    
    sentence = "[en]This is a test sentence and I want to generate audio for it"
    result = call_api(sentence=sentence)
    audio_file = result[2]["choices"][0][0]
    data, sample_rate = sf.read(audio_file)
    sd.play(data, sample_rate)
    sd.wait()
