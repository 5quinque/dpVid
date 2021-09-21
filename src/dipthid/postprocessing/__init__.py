import logging

logger = logging.getLogger(__name__)


class PostProcess:
    def __init__(self, filename, new_filename=None, mime_type=None):
        self.filename = filename
        self.new_filename = new_filename
        self.mime_type = mime_type

    def processed(self):
        logger.info(
            f"We have processed <{self.filename}> -> <{self.new_filename}> with the mime type <{self.mime_type}>"
        )
