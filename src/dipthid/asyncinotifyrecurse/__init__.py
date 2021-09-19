import os

from asyncinotify import InitFlags, Inotify, Mask

_MASK_ALL = (
    Mask.ACCESS
    | Mask.MODIFY
    | Mask.OPEN
    | Mask.CREATE
    | Mask.DELETE
    | Mask.ATTRIB
    | Mask.CLOSE
    | Mask.MOVE
    | Mask.ONLYDIR
)


class InotifyRecurse(Inotify):
    def __init__(
        self,
        path,
        mask: Mask = _MASK_ALL,
        flags: InitFlags = InitFlags.CLOEXEC | InitFlags.NONBLOCK,
        cache_size: int = 10,
    ) -> None:
        super().__init__(flags=flags, cache_size=cache_size)

        self._mask = mask

        self.load_tree(path)

    def load_tree(self, path):
        paths = []

        q = [path]
        while q:
            current_path = q[0]
            del q[0]

            paths.append(current_path)

            for filename in os.listdir(current_path):
                entry_filepath = os.path.join(current_path, filename)
                if os.path.isdir(entry_filepath) is False:
                    continue

                q.append(entry_filepath)

        for path in paths:
            self.add_watch(path, self._mask)
