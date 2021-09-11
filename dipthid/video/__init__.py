import asyncio
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


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
        if completed_process.stdout.decode("utf-8") == "":
            return False
        codecs = completed_process.stdout.decode("utf-8").splitlines()
        self.video_codec = codecs[0]
        if len(codecs) > 1:
            self.audio_codec = codecs[1]

    async def convert(self, video_codec="libx264", audio_codec="aac"):
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
            "-y",  # Automatically overwrite file if already exists
            self.output_path(video_codec),
        ]

        logger.info(f"Converting - {self.file_path}")

        proc = await asyncio.create_subprocess_exec(
            *convert_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # stdout, stderr = await proc.communicate()
        logger.info(f"[Convert for {self.file_path} exited with {proc.returncode}]")

    def output_path(self, video_codec):
        exts = {
            "copy": self.get_ext(Path(self.file_path).suffix, video_codec),
            "libx264": ".mp4",
            "vp8": ".webm",
            "vp9": ".webm",
        }
        return f"output/{Path(self.file_path).stem}{exts[video_codec]}"

    def get_ext(self, ext, video_codec):
        codec_exts = {
            "libx264": ".mp4",
            "libx265": ".mp4",
            "vp8": ".webm",
            "vp9": ".webm",
            "av1": ".mp4",
        }
        valid_ext = [".webm", ".mp4"]

        if ext in valid_ext:
            return ext

        return codec_exts[video_codec]

    def create_thumbnail(self, thumbnail_type="scaled"):
        thumbnails = {
            "scaled": [
                "ffmpeg",
                "-ss",
                "00:00:01.00",
                "-i",
                self.file_path,
                "-vf",
                "'scale=640:640:force_original_aspect_ratio=decrease'",
                "-vframes",
                "1",
                "output.png",
            ],
            "full": [
                "ffmpeg",
                "-ss",
                "00:00:01.00",
                "-i",
                self.file_path,
                "-vframes",
                "1",
                "output.png",
            ],
            "range": [
                "ffmpeg",
                "-i",
                self.file_path,
                "-vf",
                "'scale=640:640:force_original_aspect_ratio=decrease,fps=1/5'",
                "img%03d.png",
            ],
        }

        subprocess.run(thumbnails[thumbnail_type], capture_output=True)
