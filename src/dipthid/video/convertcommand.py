class ConvertCommand:
    def __init__(
        self,
        video_in,
        video_out,
        fps="25",
        gop_size="100",
        preset_p="veryslow",
        v_size_1="768x432",
        v_size_2="1920x1080",
    ):
        self.video_in = video_in
        self.video_out = video_out
        self.fps = fps
        self.gop_size = gop_size
        self.preset_p = preset_p
        self.v_size_1 = v_size_1
        self.v_size_2 = v_size_2

    @property
    def convert_command(self):
        # To break a shell command into a sequence of arguments
        # import shlex
        # shlex.split(command)
        return [
            "ffmpeg",
            "-i",
            self.video_in,
            "-preset",
            self.preset_p,
            "-keyint_min",
            self.gop_size,
            "-g",
            self.gop_size,
            "-sc_threshold",
            "0",
            "-r",
            self.fps,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ac",
            "1",
            "-ar",
            "44100",
            "-map",
            "v:0",
            "-s:0",
            self.v_size_1,
            "-b:v:0",
            "500k",
            "-maxrate:0",
            "500k",
            "-bufsize:0",
            "250k",
            "-map",
            "v:0",
            "-s:1",
            self.v_size_2,
            "-b:v:1",
            "2M",
            "-maxrate:1",
            "2M",
            "-bufsize:1",
            "1M",
            "-map",
            "0:a",
            "-use_template",
            "1",
            "-use_timeline",
            "1",
            "-seg_duration",
            "6",
            "-adaptation_sets",
            "id=0,streams=v id=1,streams=a",
            "-f",
            "dash",
            self.video_out,
            "-y",
        ]
