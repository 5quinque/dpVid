#!/usr/bin/env python


"""
dpVid / dipthid

Usage:
    dipthid watch <dir> [--interval=SECONDS]
    dipthid <path>
"""

import asyncio
import mimetypes
import time
from pathlib import Path

from docopt import docopt

from .asyncinotifyrecurse import InotifyRecurse, Mask
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


async def convert_file(filepath):
    vid = Video(filepath)

    if get_conv_codecs(vid) == ("copy", "copy"):
        # [TODO]: Although codecs may be web friendly,
        #          The container may not. E.g. Matroska
        mime_type, _ = mimetypes.guess_type(filepath)

        if mime_type != "video/x-matroska":
            print("Don't need to convert")
            return

    await vid.convert(*get_conv_codecs(vid))


async def convert(path):
    p = Path(path)
    if p.is_dir():
        for x in p.iterdir():
            await convert(str(x))
    elif p.is_file():
        await convert_file(path)
    else:
        print("Not found")


async def consume(name: int, q: asyncio.Queue) -> None:
    while True:
        i, t = await q.get()
        now = time.perf_counter()
        print(f"Consumer {name} got element <{i}>" f" in {now-t:0.5f} seconds.")
        await convert(i)
        q.task_done()


async def inotify_producer(q: asyncio.Queue, path: str) -> None:
    with InotifyRecurse(path, Mask.CLOSE_WRITE) as inotify:
        async for event in inotify:
            i = str(event.path)
            t = time.perf_counter()

            await q.put((i, t))


async def watch(opts):
    path = opts["<dir>"]
    q = asyncio.Queue()

    producer = asyncio.create_task(inotify_producer(q, path))

    consumers = [asyncio.create_task(consume(n, q)) for n in range(2)]

    await asyncio.gather(producer)
    await q.join()  # Implicitly awaits consumers, too
    for c in consumers:
        c.cancel()


def main():
    opts = docopt(__doc__)

    if opts["watch"]:
        asyncio.run(watch(opts))
    else:
        convert(opts["<path>"])


if __name__ == "__main__":
    main()
