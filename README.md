# wav2text
A program that detects speech segments in audio files with inaSpeechSegmenter, recognizes speech with Cloud Speech-to-Text for each segment detected, and saves the speech description for each segment in csv format.

## Setup

### inaSpeechSegmenter
inaSpeechSegmenter is a CNN-based audio segmentation toolkit.

#### installation


```bash
$ virtualenv -p python3 inaSpeechSegEnv
$ source inaSpeechSegEnv/bin/activate
$ pip install tensorflow-gpu # for a GPU implementation
$ pip install tensorflow # for a CPU implementation
$ pip install inaSpeechSegmenter
```

### Cloud Speech-to-Text

In advance, you need to create a service account in Cloud Console, set environment variables, and configure authentication.

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/my-key.json"
```

## CREDITS

- [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter/)
- [pyton-speech](https://github.com/googleapis/python-speech/)

