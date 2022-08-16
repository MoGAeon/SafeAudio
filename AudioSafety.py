import sys
import os
import subprocess

import wave
import ffmpeg
from vosk import Model, KaldiRecognizer, SetLogLevel
import json

import pandas as pd

import moviepy

# Forbidden words
forbidden_words = pd.read_csv("BadWords.txt", header=None, names=["word"])


# Vosk and ffmpeg setup
SetLogLevel(-1)
sample_rate=16000
model = Model(lang="en-us")
rec = KaldiRecognizer(model, sample_rate)
rec.SetWords(True)

# List of words with Timestamps
transcript = pd.DataFrame(columns = ["conf", "end", "start", "word"])
idx = 0

process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                            "Test.mp4",
                            '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                            stdout=subprocess.PIPE)

while True:
    data = process.stdout.read(4096)
    if len(data) == 0:
        process.kill()
        break
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        if len(res) != 1:
            for i in res["result"]:
                if i["word"] != "":
                    transcript.loc[idx] = i
                    idx += 1
                    
print("Extraction finished")

tts_input = transcript[(transcript["word"]).str.contains('|'.join(forbidden_words["word"]))]