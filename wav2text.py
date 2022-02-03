from inaSpeechSegmenter import Segmenter, seg2csv
from pydub import AudioSegment
from google.cloud import speech
import os
import io
import csv
import argparse
import glob
import distutils.util

description = """Do Speech/Music(/Noise) and Male/Female segmentation and store segmentations into CSV files. Segments labelled 'noEnergy' are discarded from music, noise, speech and gender analysis. 'speech', 'male' and 'female' labels include speech over music and speech over noise. 'music' and 'noise' labels are pure segments that are not supposed to contain speech.
"""


def wav2seg(args, input_files):
    segmentations = []
    detect_gender = bool(distutils.util.strtobool(args.detect_gender))
    seg = Segmenter(vad_engine=args.vad_engine,
                    detect_gender=detect_gender, ffmpeg=args.ffmpeg_binary)
    for input_file in input_files:
        segmentations += seg(input_file)

    print(segmentations)
    return segmentations


def seg2text(segmentations, input_files, output_files):
    for input_file, output_file in zip(input_files, output_files):
        with open(output_file + '.csv', 'w', encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            writer.writerow(['start', 'end', 'label', 'transcript'])

        idx = 0
        for segment in segmentations:
            segment_label = segment[0]
            if (segment_label == 'male' or segment_label == 'female' or segment_label == 'speech'):
                start_time = segment[1] * 1000
                end_time = segment[2] * 1000
                transcript = ""

                newAudio = AudioSegment.from_file(input_file)
                newAudio = newAudio[start_time:end_time]
                newAudio.export(output_file + '-' +
                                str(idx) + '.wav', format="wav")

                client = speech.SpeechClient()
                with io.open(output_file + '-' + str(idx) + '.wav', 'rb') as audio_file:
                    content = audio_file.read()

                # APIが60以上を対応していないため
                if (segment[2] - segment[1]) < 60:
                    audio = speech.RecognitionAudio(content=content)
                    config = speech.RecognitionConfig(
                        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=16000,
                        language_code='ja_JP'
                    )

                    response = client.recognize(config=config, audio=audio)
                    for result in response.results:
                        transcript += result.alternatives[0].transcript

                with open(output_file + '.csv', 'a', encoding="utf_8_sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [segment[1], segment[2], segment_label, transcript])

                print(idx, ": ", transcript)
                idx += 1
                del newAudio

        with open(output_file + ".csv") as f:
            print(f.read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--input', nargs='+', help='Input media to analyse. May be a full path to a media (/home/david/test.mp3), a list of full paths (/home/david/test.mp3 /tmp/mymedia.avi), a regex input pattern ("/home/david/myaudiobooks/*.mp3"), an url with http protocol (http://url_of_the_file)', required=True)
    parser.add_argument('-o', '--output_directory', help='Directory used to store segmentations. Resulting segmentations have same base name as the corresponding input media, with csv extension. Ex: mymedia.MPG will result in mymedia.csv', required=True)
    parser.add_argument('-d', '--vad_engine', choices=['sm', 'smn'], default='smn',
                        help="Voice activity detection (VAD) engine to be used (default: 'smn'). 'smn' split signal into 'speech', 'music' and 'noise' (better). 'sm' split signal into 'speech' and 'music' and do not take noise into account, which is either classified as music or speech. Results presented in ICASSP were obtained using 'sm' option")
    parser.add_argument('-g', '--detect_gender', choices=['true', 'false'], default='True',
                        help="(default: 'true'). If set to 'true', segments detected as speech will be splitted into 'male' and 'female' segments. If set to 'false', segments corresponding to speech will be labelled as 'speech' (faster)")
    parser.add_argument('-b', '--ffmpeg_binary', default='ffmpeg',
                        help='Your custom binary of ffmpeg', required=False)
    args = parser.parse_args()

    input_files = []

    for e in args.input:
        if e.startswith("http"):
            input_files += [e]
        else:
            input_files += glob.glob(e)
    assert len(
        input_files) > 0, 'No existing media selected for analysis! Bad values provided to -i (%s)' % args.input

    odir = args.output_directory.strip(" \t\n\r").rstrip('/')
    assert os.access(odir, os.W_OK), 'Directory %s is not writable!' % odir
    base = [os.path.splitext(os.path.basename(e))[0] for e in input_files]
    output_files = [os.path.join(odir, e) for e in base]

    segmentations = wav2seg(args, input_files)
    seg2text(segmentations, input_files, output_files)
