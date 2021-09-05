import subprocess


class Video:
    def __init__(self, file_path):
        self.file_path = file_path
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
        ]

        codec_command.append(self.file_path)
        completed_process = subprocess.run(codec_command, capture_output=True)
        self.codec = "/".join(completed_process.stdout.decode("utf-8").splitlines())
