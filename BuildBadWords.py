import os
from gtts import gTTS
import pandas as pd
import time

start_t = time.time()

# Forbidden words
forbidden_words = pd.read_csv("BadWords.txt", header=None, names=["word"]).drop_duplicates()

forbidden_words.to_csv("BadWords.txt",header=False,index=False)

if not os.path.exists("BadWords"):
    os.makedirs("BadWords")

for ids, row in forbidden_words.iterrows():
    word = row["word"]
    filename = "BadWords/" + word.replace(" ", "") + ".mp3"
    
    #if not os.path.exists(filename):
    outObj = gTTS(word)
    outObj.save(filename)
        
end_t = time.time()

print(end_t - start_t)