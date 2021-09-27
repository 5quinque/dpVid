import logging
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class PostProcess(metaclass=ABCMeta):
    def __init__(self, filename, mime_type=None, old_filename=None):
        self.filename = filename
        self.mime_type = mime_type
        self.old_filename = old_filename

    @abstractmethod
    def processed(self):
        pass


class PostProcessLog(PostProcess):
    def processed(self):
        logger.info(
            f"Processing complete, <{self.filename=}> with the <{self.mime_type=}>"
        )
