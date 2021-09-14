import asyncio
import logging
import mimetypes
import time
from pathlib import Path

from .asyncinotifyrecurse import InotifyRecurse, Mask
from .postprocessing import PostProcess
from .video import Video
from .video.codechelper import codecs, valid_container

logger = logging.getLogger(__name__)


class Dip:
    def __init__(self, opts):
        self.container = opts["--container"]

    async def convert(self, path):
        p = Path(path)
        if p.is_dir():
            for x in p.iterdir():
                await self.convert(str(x))
        elif p.is_file():
            filename, mime_type = await self.convert_file(path)

            pp = PostProcess(p.name, new_filename=filename, mime_type=mime_type)
            pp.processed()
        else:
            logger.info(f"<{path}> Not found")

    async def convert_file(self, filepath):
        vid = Video(filepath)

        conv_codec = codecs(self.container, vid)

        mime_type, _ = mimetypes.guess_type(filepath)

        # print(mime_type, valid_container(mime_type), conv_codec)

        if valid_container(mime_type) and conv_codec == ("copy", "copy"):
            logger.info(f"<{filepath}> doesn't need converting")
            return

        return await vid.convert(*conv_codec)

    async def watch(self, opts):
        path = opts["<dir>"]
        q = asyncio.Queue()
        producer = asyncio.create_task(self.inotify_producer(q, path))
        consumers = [
            asyncio.create_task(self.consume(n, q))
            for n in range(int(opts["--consumers"]))
        ]
        await asyncio.gather(producer)
        await q.join()  # Implicitly awaits consumers, too
        for c in consumers:
            c.cancel()

    async def consume(self, name: int, q: asyncio.Queue) -> None:
        logger.debug(f"Warming up consumer <{name}>")
        while True:
            i, t = await q.get()
            now = time.perf_counter()
            logger.debug(
                f"Consumer {name} got element <{i}>" f" in {now-t:0.5f} seconds."
            )
            await self.convert(i)
            q.task_done()

    async def inotify_producer(self, q: asyncio.Queue, path: str) -> None:
        with InotifyRecurse(
            path, mask=Mask.MOVED_TO | Mask.CLOSE_WRITE | Mask.CREATE
        ) as inotify:
            async for event in inotify:
                i = str(event.path)
                t = time.perf_counter()

                # Watch newly created dirs
                if (
                    Mask.CREATE in event.mask
                    and event.path is not None
                    and event.path.is_dir()
                ):
                    inotify.load_tree(event.path)

                if (
                    (Mask.MOVED_TO | Mask.CLOSE_WRITE) & event.mask
                    and event.path is not None
                    and event.path.is_file()
                ):
                    await q.put((i, t))
