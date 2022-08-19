import re
import os
import sys
import subprocess

from vosk import Model, KaldiRecognizer, SetLogLevel

import json
import pandas as pd

import time
import datetime
import nltk
import moviepy.editor as mp
from gtts import gTTS
import soundfile
import librosa

censorType = 0
censorAll = False
input_File = ""
start_ts = time.time()

def writeHelp():
    os.write(1, b'Usage: python AudioSafety.py [-h | -a | -c=[beep | silence]]*\n')
    os.write(1, b'Censors all files in the "input"-folder with Text-To-Speech on the words \n')
    os.write(1, b'in any .txt file in the "src"-folder with "BadWords" in its name.\n\n')
    os.write(1, b'Options:\n')
    os.write(1, b'-h \t Help\n')
    os.write(1, b'-a \t Censor all words (WARNING! Increases calculation time)\n')
    os.write(1, b' \t overrides -c\n')
    os.write(1, b'-c \t Allows selection for type of censor:\n')
    os.write(1, b'\t beep: Censors with a "beep" sound.\n')
    os.write(1, b'\t silence: Censors by removing the audio.\n')

if len(sys.argv) != 1:
    params = sys.argv[1:]
    for param in params:
        if "-h" == param:
            writeHelp()
            sys.exit()
        elif "-a" == param:
            censorAll = True
            pass
        elif "-c=" in param:
            param_val = param[3:]
            if param_val == "beep":
                censorType = 1
            elif param_val == "silence":
                censorType = 2
            else:
                writeHelp()
                sys.exit()
        else:
            writeHelp()
            sys.exit()

# Forbidden words

badWords = []

for file in os.listdir("src"):
    if "BadWords" not in file:
        continue
    for word in pd.read_csv("src/" + file, header=None, names=["word"]).drop_duplicates()["word"]:
        badWords.append(word)
badWords = list(dict.fromkeys(badWords))

badWordJoin = '|'.join(badWords)
    
if not os.path.exists("output"):
    os.makedirs("output")
    
if not os.path.exists("BadWords"):
    os.makedirs("BadWords")
    
if not os.path.exists("Words"):
    os.makedirs("Words")

if not os.path.exists("input"):
    os.write(1, b'Input folder missing.\n')
    os.makedirs("input")
    sys.exit()

existingBadWords = os.listdir("BadWords")
existingWords = os.listdir("Words")

# Vosk and ffmpeg setup
SetLogLevel(-1)
sr=16000
model = Model("model_en-us_lgraph")

for file in os.listdir("input"):
   
    os.write(1, str.encode("Censoring file: " + file + "\n\n"))
    
    # List of words with Timestamps
    transcript = pd.DataFrame(columns = ["conf", "end", "start", "word"])
    idx = 0
    rec = KaldiRecognizer(model, sr)
    rec.SetWords(True)
    
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                "input/" + file,
                                '-ar', str(sr) , '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE)
    
    while True:
        data = process.stdout.read(4096)
        if len(data) == 0:
            process.wait()
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if len(res) != 1:
                for dataRow in res["result"]:
                    if dataRow["word"] != "":
                        transcript.loc[idx] = dataRow
                        idx += 1
    
    video = mp.VideoFileClip("input/" + file)
    audio = video.audio
    
    start = datetime.timedelta()
    rx = re.compile(badWordJoin)
    clips = []
    cnt = 0
    
    for idx, row in transcript.iterrows():
        #insert no word part
        end = datetime.timedelta(seconds=row["start"])
        
        clips.append(audio.subclip(str(start), str(end)))
        
        start = datetime.timedelta(seconds=row["end"])

        word = row["word"].lower()
        badWord = bool(rx.search(word))
        
        insecure = row["conf"] < 0.95
        
        if insecure:
            insecure = False
            wordlen = len(word)
            for aBadWord in badWords:
                if nltk.edit_distance(word, aBadWord) > max(wordlen, len(aBadWord))*(1-row["conf"]):
                    insecure = True
                    break;
                        
        if not (insecure or badWord):
            clips.append(audio.subclip(str(end), str(start)))
            continue
        
        duration = start.total_seconds() - end.total_seconds()
        
        # TTS-Replacement
        if (censorAll or censorType == 0):
            filename = word.replace(" ", "") + ".wav"
            
            # Word exists as a file
            if badWord:
                if filename not in existingBadWords:
                    outObj = gTTS(word.lower())
                    outObj.save("BadWords/"+ filename)
                    existingBadWords.append(filename)
                audioToCorrect, sr = librosa.load("BadWords/"+ filename, sr)
            elif censorAll or insecure:
                if filename not in existingWords:
                    outObj = gTTS(word.lower())
                    outObj.save("Words/"+ filename)
                    existingWords.append(filename)
                audioToCorrect, sr = librosa.load("Words/"+ filename, sr)        
        # Beep-Replacement
        elif (censorType == 1):
            audioToCorrect, sr = librosa.load("src/beep.mp3", sr)
        # Silence-Replacement
        elif (censorType == 2):
            audioToCorrect, sr = librosa.load("src/silence.mp3", sr)
    
        if censorAll or badWord or insecure:
            newSnippet = librosa.effects.time_stretch(audioToCorrect, librosa.get_duration(audioToCorrect, sr) / duration)
            soundfile.write("temp.wav", newSnippet, sr)
            
            clips.append(mp.AudioFileClip("temp.wav"))
            
            cnt += 1
    
    clips.append(audio.subclip(str(start)))
    
    newAudio = mp.concatenate_audioclips(clips)
    
    newVideo = video.set_audio(newAudio)
    
    newVideo.write_videofile("output/" + file)

    audio.close()
    video.close()
    newAudio.close()
    newVideo.close()
    
    print("Bad words:", cnt)
    print("Duration:", int(time.time()-start_ts), "sec")