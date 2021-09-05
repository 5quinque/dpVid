#!/usr/bin/env python


"""
dpVid / dipthid

Usage:
    dipthid watch <dir> [--interval=SECONDS]
    dipthid <path>
"""

from pathlib import Path

from docopt import docopt

from .video import Video


def get_conv_codecs(video):
    valid_video_codecs = {
        "av1": "av1",
        "h264": "libx264",
        "h265": "h265",
        "vp8": "vp8",
        "vp9": "vp8",
    }
    valid_audio_codecs = ("aac", "mp3", "vorbis", "opus")

    conv_aud_cod = "aac"
    conv_vid_cod = "libx264"

    if video.audio_codec is None:
        conv_aud_cod = "copy"
    elif video.audio_codec.lower() in valid_audio_codecs:
        conv_aud_cod = "copy"
    if video.video_codec is None:
        conv_vid_cod = "copy"
    elif video.video_codec.lower() in valid_video_codecs:
        conv_vid_cod = "copy"

    return (conv_vid_cod, conv_aud_cod)


def convert_file(filepath):
    vid = Video(filepath)

    print(filepath)

    if get_conv_codecs(vid) == ("copy", "copy"):
        print("Don't need to convert")
        return

    vid.convert(*get_conv_codecs(vid))


def convert(path):
    p = Path(path)
    if p.is_dir():
        for x in p.iterdir():
            convert(str(x))
    elif p.is_file():
        convert_file(path)
    else:
        print("Not found")


def main():
    opts = docopt(__doc__)

    if opts["watch"]:
        print("Watching directory")
    else:
        convert(opts["<path>"])


if __name__ == "__main__":
    main()
