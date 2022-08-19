import os
import moviepy.editor as mp 

for file in os.listdir("input"):
    video = mp.VideoFileClip("input/" + file)
    video.audio.write_audiofile("input/" + file + ".mp3")

