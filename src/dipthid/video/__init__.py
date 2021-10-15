import asyncio
import logging
import mimetypes
import os
import subprocess
from pathlib import Path

from .convertcommand import ConvertCommand

logger = logging.getLogger(__name__)


class Video:
    def __init__(self, file_path):
        self.file_path = file_path

        self.convert_command = ConvertCommand(
            self.file_path, self.output_path()
        ).convert_command

    async def convert(self):
        output_file_path = self.output_path()

        logger.info(f"Creating thumbnail for <{self.file_path}>")
        self.create_thumbnail()

        logger.info(f"Converting <{self.file_path}>")

        logger.debug("ffmpeg command: %s", " ".join(self.convert_command))

        proc = await asyncio.create_subprocess_exec(
            *self.convert_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        # print(stdout)
        # print(stderr)

        logger.info(f"Convert for {self.file_path} exited with {proc.returncode}")

        mime_type, _ = mimetypes.guess_type(output_file_path)

        return (output_file_path, mime_type)

    def output_path(self):
        if not os.path.isdir(f"output/{Path(self.file_path).stem}"):
            os.mkdir(f"output/{Path(self.file_path).stem}")
        return f"output/{Path(self.file_path).stem}/{Path(self.file_path).stem}.mpd"

    def create_thumbnail(self):
        thumbnail_command = [
            "ffmpeg",
            "-ss",
            self.timestamp(),
            "-i",
            self.file_path,
            "-vf",
            "scale=640:640:force_original_aspect_ratio=decrease",
            "-vframes",
            "1",
            f"output/{Path(self.file_path).stem}/thumbnail.png",
            "-y",
        ]

        subprocess.run(thumbnail_command, capture_output=True)

    def timestamp(self):
        duration = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            self.file_path,
        ]

        duration_proc = subprocess.run(duration, capture_output=True)
        return str(round(float(duration_proc.stdout.decode("utf-8")) / 2))
