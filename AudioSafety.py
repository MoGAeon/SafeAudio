import re
import os
import subprocess

from vosk import Model, KaldiRecognizer, SetLogLevel

import json
import pandas as pd

import datetime
import moviepy.editor as mp
from gtts import gTTS

# Forbidden words
badWords = pd.read_csv("BadWords.txt", header=None, names=["word"])

censorType = 0

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

if not os.path.exists("BadWords"):
    os.makedirs("BadWords")

badWordJoin = '|'.join(badWords["word"])

existingFiles = os.listdir("BadWords")

video = mp.VideoFileClip("Test.mp4")
audio = video.audio

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
    # Silence-Replacement
    elif (censorType == 2):
        while (duration >= 2):
            clips.append(mp.AudioFileClip("silence.mp3"))
            duration = duration - 2
        clips.append(mp.AudioFileClip("silence.mp3").set_duration(duration))


audio = mp.concatenate_audioclips(clips)

video = video.set_audio(audio)

video.write_videofile("output.mp4")