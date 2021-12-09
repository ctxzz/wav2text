#!/bin/bash
#run in current DIR

for f in *.wav
do
   python3 wav2text.py -i ${f} -o output
done
