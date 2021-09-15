import asyncio
import logging
import mimetypes
import shutil
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

    async def convert(self, audio_codec="aac", video_codec="libx264"):
        output_file_path = self.output_path(video_codec)
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
            output_file_path,
        ]

        logger.info(f"Converting - {self.file_path}")

        proc = await asyncio.create_subprocess_exec(
            *convert_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        # print(stdout)
        # print(stderr)

        logger.info(f"Convert for {self.file_path} exited with {proc.returncode}")

        # new_file_path = f"{Path(self.file_path).parent}/{Path(output_file_path).name}"
        # logger.info(f"Moving {output_file_path} to {new_file_path}")
        # shutil.move(output_file_path, new_file_path)

        mime_type, _ = mimetypes.guess_type(output_file_path)

        return (Path(output_file_path).name, mime_type)

    def output_path(self, video_codec):
        exts = {
            "copy": self.get_ext(Path(self.file_path).suffix, self.video_codec),
            "h264": ".mp4",
            "vp8": ".webm",
            "vp9": ".webm",
        }

        return f"output/{Path(self.file_path).stem}{exts[video_codec]}"

    def get_ext(self, ext: str, video_codec: str):
        codec_exts = {
            "libx264": ".mp4",
            "libx265": ".mp4",
            "h264": ".mp4",
            "h265": ".mp4",
            "vp8": ".webm",
            "vp9": ".webm",
            "av1": ".mp4",
        }
        valid_ext = [".webm", ".mp4"]

        if ext in valid_ext:
            return ext
        if video_codec in codec_exts:
            return codec_exts[video_codec]

        return None

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
