import sys
import os
import subprocess

import wave
import ffmpeg
from vosk import Model, KaldiRecognizer, SetLogLevel
import json

import moviepy

# Forbidden words
forbidden_words = ["fuck", "sex", "pussy"]

# Vosk and ffmpeg setup
SetLogLevel(-1)
sample_rate=16000
model = Model(lang="en-us")
rec = KaldiRecognizer(model, sample_rate)
rec.SetWords(True)


# List of words with Timestamps
input_text = []

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
            res = res["result"]
            for i in res:
                if i["word"] != "":
                    input_text.append(i)
        
for index in range(len(input_text)):
    word = input_text[index]["word"].lower()
    for xword in forbidden_words:
        if xword in word:
            print(index, ":", word, input_text[index]["start"], input_text[index]["end"])
    
    