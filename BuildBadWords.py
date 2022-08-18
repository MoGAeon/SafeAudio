import os
from gtts import gTTS
import pandas as pd
import time

for file in os.listdir("src"):
    if "BadWords" not in file:
        continue

    file = file.lower()

    # Forbidden words
    forbidden_words = pd.read_csv("src/" + file, header=None, names=["word"]).drop_duplicates()
    
    if not os.path.exists("BadWords"):
        os.makedirs("BadWords")
    
    for ids, row in forbidden_words.iterrows():
        word = row["word"]
        filename = "BadWords/" + word.replace(" ", "") + ".wav"
        
        if not os.path.exists(filename):
            outObj = gTTS(word)
            outObj.save(filename)