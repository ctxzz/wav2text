#!/bin/bash
#run in current DIR

for f in *.mp4
do
   ffmpeg -i ${f} -ar 16000 -ac 1 -map 0:2 "${f}.wav"
done
