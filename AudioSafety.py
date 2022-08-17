import sys
import re
import os
import subprocess

from vosk import Model, KaldiRecognizer, SetLogLevel

import json
import pandas as pd

import time
import datetime
import moviepy.editor as mp
from gtts import gTTS

argslen = len(sys.argv)

inputFile = ""

if argslen == 1:
    print("Enter a filename:")
    inputFile = input()
else:
    inputFile = sys.argv[1]


censorType = -1

if argslen == 3:
    censorType = sys.args[2]
elif argslen == 1:
    print("Enter censor type:")
    print("-t: Text To Speech")
    print("-b: beep")
    print("-s: Silence")
    censorType = input().replace(" ", "")
    
if (censorType == "-t"):
    censorType = 0
elif (censorType == "-b"):
    censorType = 1
elif (censorType == "-s"):
    censorType = 2
    

times = []

times.append(("Start", time.time()))

# Forbidden words
badWords = pd.read_csv("BadWords.txt", header=None, names=["word"])

# Vosk and ffmpeg setup
SetLogLevel(-1)
sample_rate=16000
model = Model(lang="en-us")
rec = KaldiRecognizer(model, sample_rate)
rec.SetWords(True)

times.append(("Setup done", time.time()))

# List of words with Timestamps
transcript = pd.DataFrame(columns = ["conf", "end", "start", "word"])
idx = 0

process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                            sys.argv[1],
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
                    
times.append(("STT done", time.time()))

if not os.path.exists("BadWords"):
    os.makedirs("BadWords")

badWordJoin = '|'.join(badWords["word"])

existingFiles = os.listdir("BadWords")

video = mp.VideoFileClip("Test.mp4")
audio = video.audio

times.append(("Video loaded", time.time()))

start = datetime.timedelta()
rx = re.compile(badWordJoin)
clips = []

for idx, row in transcript.iterrows():
    if not bool(rx.search(row["word"])):
        continue
    
    end = datetime.timedelta(seconds=row["start"])
    
    clips.append(audio.subclip(str(start), str(end)))
    
    start = datetime.timedelta(seconds=row["end"])
    duration = audio.subclip(str(end), str(start)).duration
    
    # TTS-Replacement
    if (censorType == 0):
        word = row["word"].lower()
        filename = word.replace(" ", "") + ".mp3"
        
        if filename not in existingFiles:
            outObj = gTTS(word.lower())
            outObj.save("BadWords/"+ filename)
            existingFiles.append(filename)
    
        replacementAudio = mp.AudioFileClip("BadWords/"+ filename)
        clips.append(replacementAudio.fx(mp.vfx.speedx, replacementAudio.duration / duration))
    # Beep-Replacement
    elif (censorType == 1):
        while (duration >= 5):
            clips.append(mp.AudioFileClip("beep.mp3"))
            duration = duration - 5
        clips.append(mp.AudioFileClip("beep.mp3").set_duration(duration))
    else:
        clips.append(mp.AudioFileClip("beep.mp3").set_duration(duration))
    

times.append(("Audio generation done", time.time()))

audio = mp.concatenate_audioclips(clips)

times.append(("Audio merge done", time.time()))

video = video.set_audio(audio)

times.append(("Audio on video replaced", time.time()))

video.write_videofile(sys.argv[1])

times.append(("Export done", time.time()))

prev_ts = times[0][1]
for text, ts in times:
    print(text, str(ts - prev_ts))