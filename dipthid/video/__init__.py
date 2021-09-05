import subprocess
from pathlib import Path


class Video:
    def __init__(self, file_path):
        self.file_path = file_path
        self.audio_codec = None
        self.video_codec = None
        self.get_codec()

    def get_codec(self):
        codec_command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            self.file_path,
        ]

        completed_process = subprocess.run(codec_command, capture_output=True)
        codecs = completed_process.stdout.decode("utf-8").splitlines()

        self.video_codec = codecs[0]
        if len(codecs) > 1:
            self.audio_codec = codecs[1]

    def convert(self, video_codec="libx264", audio_codec="aac"):
        convert_command = [
            "ffmpeg",
            "-i",
            self.file_path,
            "-vcodec",
            video_codec,
            "-acodec",
            audio_codec,
            "-pix_fmt",
            "yuv420p",  # Apple Quicktime support
            # "-profile:v",
            # "baseline",
            # "-level",
            # "3",  # Android in particular doesn't support higher profiles.
            "-threads",
            "0",
            "-crf",  # The range of the CRF scale is 0–51, where 0 is lossless
            "22",  # 23 is the default, and 51 is worst quality possible.
            "-movflags",  # Moves some data to the beginning of the file
            "+faststart",  # allowing the video to be played before it is completely downloaded.
            self.output_path(video_codec),
        ]

        # print(convert_command)
        print(" ".join(convert_command))

        # completed_process = subprocess.run(convert_command)  # , capture_output=True)

    def output_path(self, video_codec):
        exts = {
            "copy": Path(self.file_path).suffix,
            "libx264": ".mp4",
            "vp8": ".webm",
            "vp9": ".webm",
        }
        return f"output/{Path(self.file_path).stem}{exts[video_codec]}"
