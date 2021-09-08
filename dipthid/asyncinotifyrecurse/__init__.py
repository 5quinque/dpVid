import os

from asyncinotify import InitFlags, Inotify, Mask


class InotifyRecurse(Inotify):
    def __init__(
        self,
        path,
        mask,
        flags: InitFlags = InitFlags.CLOEXEC | InitFlags.NONBLOCK,
        cache_size: int = 10,
    ) -> None:
        super(InotifyRecurse, self).__init__(flags=flags, cache_size=cache_size)

        self._mask = mask

        self.__load_tree(path)

    def __load_tree(self, path):
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
