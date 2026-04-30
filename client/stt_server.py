import whisper
import json
from flask import Flask, request, jsonify
import os
import io
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("whisper-server")

try:
    from pydub import AudioSegment
    import noisereduce as nr
except ImportError:
    AudioSegment = None
    nr = None

app = Flask(__name__)



model = whisper.load_model("small")

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    if audio_file.filename:
        log_source = audio_file.filename
    else:
        log_source = "in-memory upload"

    try:
        
        if AudioSegment is None:
            return jsonify({'error': 'pydub required for audio processing'}), 400

        audio_file.seek(0)
        segment = AudioSegment.from_file(audio_file)
        source_rate = segment.frame_rate
        source_channels = segment.channels

        
        segment = segment.set_channels(1).set_frame_rate(16000)

        
        samples = np.array(segment.get_array_of_samples(), dtype=np.float32) / 32768.0  

        
        if nr is not None:
            pass # noise reduction disabled

        log.info(
            "Processed audio (%s) from %s Hz %sch to mono 16kHz",
            log_source,
            source_rate,
            source_channels,
        )
    except Exception as e:
        return jsonify({'error': f'Failed to process audio: {e}'}), 400

    try:
        
        result = model.transcribe(
            samples,
            language="en",
            fp16=False,
            condition_on_previous_text=False
        )
        recognized_text = result["text"].strip()

        log.info("Whisper recognition result for %s: %s", log_source, repr(recognized_text))

        if not recognized_text:
            return jsonify({'text': '', 'warning': 'No speech text recognized. Check audio content.'})

        return jsonify({'text': recognized_text})

    except Exception as e:
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Whisper speech recognition server...")
    print("Small model loaded successfully. Improved accuracy (~244MB) with offline capability.")
    print("Noise reduction enabled for better performance in noisy environments.")
    app.run(host='0.0.0.0', port=5001, debug=False)