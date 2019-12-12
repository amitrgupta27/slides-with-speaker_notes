# My code
import os
import cv2
import time

from luigi import IntParameter, Parameter, Task
from luigi.contrib.external_program import ExternalProgramTask
from luigi.format import Nop
from pset_utils.luigi.target import LocalTarget


# did not use S3 target per Scott's instruction
# storing large files under data
#from luigi.contrib.s3 import S3Target

from skimage import measure
import speech_recognition as sr


# This task extracts the video stream from lecture.mp4, and takes a JPG snapshot every 20 seconds  (-r 0.05 flag in FFMPEG)
# Essentially downsampling 60fps video to 1 frame every 20 seconds
class TO_JPG (ExternalProgramTask):

    DATA_ROOT = "data"
    LECTURE_FILE = Parameter("lecture.mp4")
    lecture_duration = IntParameter(default=100)

    def output(self):
        # calculate last snapshot
        last_snapshot = (self.lecture_duration) // 20
        jpg_snapshot = "image-" + str(last_snapshot) + ".jpg"
        target =  LocalTarget(
        os.path.join(self.DATA_ROOT, "chunked_jpg_files", jpg_snapshot), format=Nop)
        # create a directory if one doesn't exist
        target.makedirs()
        return target

    def program_args(self):
        inputs = self.input()

        input_lecture_file = os.path.join(self.DATA_ROOT, "lecture", self.LECTURE_FILE)
        output_jpg_files = os.path.join(self.DATA_ROOT, "chunked_jpg_files", "image-%d.jpg")
        return [
            "ffmpeg",
            "-i",
            input_lecture_file,
            "-r",
            "0.05",
            "-t",
            str(self.lecture_duration),
            output_jpg_files,
        ]

    def run(self):
        super().run()


# This task extracts the audio stream from lecture.mp4, and writes the stream to lecture.mp3
class TO_MP3 (ExternalProgramTask):

    DATA_ROOT = "data"
    LECTURE_FILE = Parameter("lecture.mp4")
    LECTURE_MP3_FILE = Parameter("lecture.mp3")

    def output(self):
        target = LocalTarget(
            os.path.join(self.DATA_ROOT, "mp3_files", self.LECTURE_MP3_FILE), format=Nop)
        # create a directory if one doesn't exist
        target.makedirs()
        return target


    def program_args(self):
        inputs = self.input()

        input_lecture_file = os.path.join(self.DATA_ROOT, "lecture", self.LECTURE_FILE)
        output_mp3_file = os.path.join(self.DATA_ROOT, "mp3_files", self.LECTURE_MP3_FILE)
        return [
            "ffmpeg",
            "-i",
            input_lecture_file,
            "-vn",
            "-q:a",
            "0",
            output_mp3_file,
        ]

    def run(self):
        super().run()


# This task takes the lecture.mp3 audio stream and converts it to lecture.wav format
# .wav format is needed for python speech recognition libraries
class TO_WAV (ExternalProgramTask):

    DATA_ROOT = "data"
    LECTURE_MP3_FILE = Parameter("lecture.mp3")
    LECTURE_WAV_FILE = Parameter("lecture.wav")

    def requires(self):
        return self.clone(TO_MP3)

    def output(self):
        target =  LocalTarget(
            os.path.join(self.DATA_ROOT, "wav_files", self.LECTURE_WAV_FILE), format=Nop)
        # create a directory if one doesn't exist
        target.makedirs()
        return target


    def program_args(self):
        inputs = self.input()
        input_mp3_file = os.path.join(self.DATA_ROOT, "mp3_files", self.LECTURE_MP3_FILE)
        output_wav_file = os.path.join(self.DATA_ROOT, "wav_files", self.LECTURE_WAV_FILE)
        return [
            "ffmpeg",
            "-i",
            input_mp3_file,
            output_wav_file,
        ]

    def run(self):
        # You must set up an atomic write!
        #with self.output().temporary_path() as self.temp_output_path:
        super().run()


# This task takes lecture.wav and converts in 20 second chunks of .wav files
class TO_ChunkedWAV (ExternalProgramTask):

    DATA_ROOT = "data"
    LECTURE_WAV_FILE = Parameter("lecture.wav")
    lecture_duration = IntParameter(default=100)

    def requires(self):
        return self.clone(TO_WAV)

    def output(self):
        # calculate last snapshot
        last_snapshot = ((self.lecture_duration) // 20) - 1
        wav_snapshot = "out-" + str(last_snapshot) + ".wav"
        target =  LocalTarget(
            os.path.join(self.DATA_ROOT, "chunked_wav_files", wav_snapshot), format=Nop)
        # create a directory if one doesn't exist
        target.makedirs()
        return target


    def program_args(self):

        inputs = self.input()

        input_wav_file = os.path.join(self.DATA_ROOT, "wav_files", self.LECTURE_WAV_FILE)
        output_chunked_wav_files = os.path.join(self.DATA_ROOT, "chunked_wav_files", "out-%d.wav")

        return [
            "ffmpeg",
            "-i",
            input_wav_file,
            "-f",
            "segment",
            "-segment_time",
            "20",
            "-t",
            str(self.lecture_duration),
            "-c",
            "copy",
            output_chunked_wav_files,

        ]

    def run(self):
        super().run()

# This task takes the JPG sna[shot, and extracts ROI (slide portion) from the image
class CropFrames (Task):

    lecture_duration = IntParameter(default=200)
    DATA_ROOT = "data"


    def requires(self):
        return self.clone(TO_JPG)

    def output(self):
        last_snapshot = (self.lecture_duration) // 20
        jpg_snapshot = "image-" + str(last_snapshot) + ".jpg"
        target =  LocalTarget(
        os.path.join(self.DATA_ROOT, "cropped_jpg_files", jpg_snapshot), format=Nop)
        # create a directory if one doesnt exist
        target.makedirs()
        return target


    def run(self):

        for name in os.listdir(os.path.join(self.DATA_ROOT, "chunked_jpg_files")):

            filepath = os.path.join(self.DATA_ROOT, "chunked_jpg_files", name)
            image = cv2.imread(filepath)
            # Select ROI (this is hardcoded, requires some experimentation with target monitor resolutions)
            r0 = 1871
            r1 = 278
            r2 = 850
            r3 = 478

            cropped_image = image[r1:r1 + r3, r0:r0 + r2]
            gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            cropped_filepath = os.path.join (self.DATA_ROOT, "cropped_jpg_files", name)
            cv2.imwrite(cropped_filepath, gray_image)


# This task finds the keyframes using structural similarity index
class FindKeyFrames (Task):

    lecture_duration = IntParameter(default=200)
    DATA_ROOT = "data"

    def requires(self):
        return self.clone(CropFrames)


    def output(self):
        # It was not clear to me what the correct final snapshot targets should be
        # Reason is we dont know beforehand what would be the key frames and non key frames in the video stream
        # I have assumed the first frame to be a key frame and second frame in 20s to be a non-key frame
        # key.txt has 2 columns (col1 records the key frame, col2 records the last non-key frame before the
        # next key frame)

        target =  {
            "key_frames": LocalTarget(
        os.path.join(self.DATA_ROOT, "key_frames", "image-1.jpg"), format=Nop),
            "nonkey_frames": LocalTarget(
        os.path.join(self.DATA_ROOT, "nonkey_frames", "image-2.jpg"), format=Nop),
            "key_frame_nos": LocalTarget(
        os.path.join(self.DATA_ROOT, "key_frame_nos", "key.txt"), format=Nop)
        }
        # create a directory if doesnt exist
        target["key_frames"].makedirs()
        target["nonkey_frames"].makedirs()
        target["key_frame_nos"].makedirs()

        return target


    def run(self):

        with self.output()["key_frame_nos"].temporary_path() as temp_output_path:

            fp = open(temp_output_path, "w")

            image_path = os.path.join(self.DATA_ROOT, "cropped_jpg_files")
            numfiles = len([name for name in os.listdir(image_path)])
            p_frame_thresh = 0.8  # You may need to adjust this threshold
            fnum = 1
            nonkey_counter = 0

            # Read the first frame, and designate it as a key frame

            prev_frame = cv2.imread(os.path.join(self.DATA_ROOT, "cropped_jpg_files", "image-1.jpg"), 0)
            out_keyframe_file = os.path.join(self.DATA_ROOT, "key_frames", "image-%d.jpg")
            cv2.imwrite(out_keyframe_file % fnum, prev_frame)
            fp.write(str(fnum))

            for count in range(numfiles - 1):

                cropped_file = os.path.join(image_path, "image-" + str(count + 2) + ".jpg")
                curr_frame = cv2.imread(cropped_file, 0)
                fnum += 1

                ssim = measure.compare_ssim(curr_frame, prev_frame)

                if ssim < p_frame_thresh:
                    out_keyframe_file = os.path.join(self.DATA_ROOT, "key_frames", "image-%d.jpg")
                    cv2.imwrite(out_keyframe_file % fnum, curr_frame)
                    fp.write(" " + str(nonkey_counter) + "\n")
                    fp.write(str(fnum))
                    nonkey_counter = 0
                else:
                    out_nonkeyframe_file = os.path.join(self.DATA_ROOT, "nonkey_frames", "image-%d.jpg")
                    cv2.imwrite(out_nonkeyframe_file % fnum, curr_frame)
                    nonkey_counter += 1

                prev_frame = curr_frame

            fp.write(" " + str(nonkey_counter) + "\n")


# This task converts the 20 second .wav files into text
class SpeechToText (Task):

    lecture_duration = IntParameter(default=200)
    DATA_ROOT = "data"
    TEXT_FILE = Parameter("lecture.txt")

    def requires(self):
        return self.clone(TO_ChunkedWAV)

    def output(self):
        target =  LocalTarget(
            os.path.join(self.DATA_ROOT, "speechtotext", self.TEXT_FILE))
        # create a directory if it doesnt exist
        target.makedirs()
        return target

    def run(self):

        with self.output().temporary_path() as temp_output_path:

            wavefile_path = os.path.join(self.DATA_ROOT, "chunked_wav_files")
            r = sr.Recognizer()

            numfiles = len([name for name in os.listdir(wavefile_path)])
            fp = open(temp_output_path, "w")

            for count in range(numfiles):

                wavfile = wavefile_path + "/" + "out-" + str(count) + ".wav"
                harvard = sr.AudioFile(wavfile)
                with harvard as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.record(source)

                response = {
                    "success": True,
                    "error": None,
                    "transcription": None
                }

                try:

                    response["transcription"] = r.recognize_google(audio)
                except sr.RequestError:
                    # API was unreachable or unresponsive
                    response["success"] = False
                    response["error"] = "API unavailable"
                except sr.UnknownValueError:
                    # speech was unintelligible
                    response["error"] = "Unable to recognize speech"


                timestr = time.strftime('%H:%M:%S', time.gmtime(count * 20))
                if (response["transcription"] != None):
                    fp.write(timestr + " " + response["transcription"] + "\n")
                else:
                    fp.write(timestr + " " + "ERROR converting audio to text\n")



# This task identifies the mapping of the slide number to the spoken text
class MapTextToSlides (Task):

    lecture_duration = IntParameter(default=200)
    DATA_ROOT = Parameter("data")
    MAP_FILE = "mapfile.txt"


    def requires(self):
        return {
            "text": self.clone(SpeechToText),
            "key_frames": self.clone(FindKeyFrames)
        }

    def output(self):
        target =  LocalTarget(
            os.path.join(self.DATA_ROOT, "mapping", self.MAP_FILE))
        # create dir if it doesnt exist
        target.makedirs()
        return target

    def run(self):

        # build the slide mapping
        input = self.input()["key_frames"]["key_frame_nos"].path
        key_fp = open(input, "r")

        input = self.input()["text"].path
        speech_fp = open(input, "r")
        slide_number = 0

        with self.output().temporary_path() as temp_output_path:

            fp = open(temp_output_path, "w")

            for line in key_fp.readlines():
                key, nonkey = line.split()
                total_lines_to_read = int(nonkey) + 1
                slide_number += 1
                fp.write("SLIDE" + str(slide_number) + "\n")
                # read these many lines from lecture.txt and attribute these lines to the particular slide
                for i in range(0, total_lines_to_read):
                    lines = speech_fp.readline()
                    fp.write(lines)

