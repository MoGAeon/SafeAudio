########## Setup ##########
Download the git and create a folder named "input". This is where you will be putting all files you want to censor the "Bad Words" of.
In the folder "src" you will find a file named  "BadWords". Thise is a simple lists of words that are considered "nasty". 
You can use this, get your own list of words or add more to your liking. 
Note that all files containing "BadWords" in their names will be used for detection and censoring.

Now use "pip install %Name%" for all of the following packages by replacing %Name% in the command:

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


########## Running the Programm ##########
Usage: python AudioSafety.py [-h | -a | -c=[beep | silence]]*
Censors all files in the "input"-folder with Text-To-Speech on the words 
in any .txt file in the "src"-folder with "BadWords" in its name.
Running the "BuildBadWords.py" with good BadWords-files is strongly recommended.

Options:
-h 	 Help
-a 	 Censor all words (WARNING! Increases calculation time)
 	 overrides -c
-c 	 Allows selection for type of censor:
	 beep: Censors with a "beep" sound.
	 silence: Censors by removing the audio.

########## Some Notes ##########
This software is no were near perfection. It is a simple solution and a fun project, nothing more, nothing less.
I, personally, dont support censorship of opinion in any way or form, especially not for political reasons.
But I do note that censorship aimed to protect individuals like this is something the world needs.

########## Bugs ##########
I follow a simple rule with a simple script like this:
If you find a bug, you can keep it. Feel free to open an issue, but I dont promise to ever even look at it.
The basics of the script took me just shy over 4 hours to write and I never really used python in a way like this,
so just keep that in mind when you run into any major problem.
