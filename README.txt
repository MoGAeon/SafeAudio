Usage: python AudioSafety.py [-h | -a | -c=[beep | silence]]*
Censors all files in the "input"-folder with Text-To-Speech on the words 
in any .txt file in the "src"-folder with "BadWords" in its name.

Options:
-h 	 Help
-a 	 Censor all words (WARNING! Increases calculation time)
 	 overrides -c
-c 	 Allows selection for type of censor:
	 beep: Censors with a "beep" sound.
	 silence: Censors by removing the audio.


Use pip to install the following packages:

re
os
sys
subprocess

vosk

json
pandas

time
datetime
nltk
moviepy.editor as mp
gtts import gTTS
soundfile
librosa
