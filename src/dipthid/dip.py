import asyncio
import importlib
import logging
import mimetypes
import time
from pathlib import Path

from .asyncinotifyrecurse import InotifyRecurse, Mask
from .video import Video
from .video.codechelper import codecs, valid_container

logger = logging.getLogger(__name__)


class Dip:
    def __init__(self, opts):
        self.container = opts["--container"]
        self.pp_class = opts["--post-processer"]

    def postProcess(self, filename, mime_type=None, old_filename=None):
        namespace, obj_name = self.pp_class.split(":")
        p_mod = importlib.import_module(namespace, obj_name)
        process_class = getattr(p_mod, obj_name)
        process_obj = process_class(filename, mime_type, old_filename)
        process_obj.processed()

    async def convert(self, path):
        p = Path(path)
        if p.is_dir():
            for x in p.iterdir():
                await self.convert(str(x))
        elif p.is_file():
            if not self.valid_file(path):
                logger.info(f"<{path}> needs converting")
                self.postProcess(
                    *await self.vid.convert(*self.conv_codec), old_filename=p
                )
            else:
                logger.info(f"<{path}> doesn't needs converting")
                self.postProcess(p, old_filename=p.name)
        else:
            logger.info(f"<{path}> Not found")

    def valid_file(self, filepath):
        self.vid = Video(filepath)
        self.conv_codec = codecs(self.container, self.vid)
        self.mime_type, _ = mimetypes.guess_type(filepath)
        return valid_container(self.mime_type) and self.conv_codec == ("copy", "copy")

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
