import logging
import os
from pathlib import Path

import sqlalchemy as db

from . import PostProcess

logger = logging.getLogger(__name__)


class UpdateDB(PostProcess):
    def __init__(self, filename, mime_type=None, old_filename=None):
        super().__init__(filename, mime_type, Path(old_filename).name)

        self.__connection = self._db_connect()

    def _db_connect(self):
        self.__engine = db.create_engine(os.environ.get("DATABASE_URL"))

        connection = self.__engine.connect()
        __metadata = db.MetaData()

        self._media = db.Table(
            "media", __metadata, autoload=True, autoload_with=self.__engine
        )

        return connection

    def getFile(self):
        query = db.select([self._media]).where(
            self._media.columns.filename == self.old_filename
        )
        ResultProxy = self.__connection.execute(query)
        return ResultProxy.fetchall()

    def processed(self):
        if self.new_filename:
            query = (
                db.update(self._media)
                .values(
                    processed=True, filename=self.filename, mime_type=self.mime_type
                )
                .where(self._media.columns.filename == self.old_filename)
            )
        else:
            query = (
                db.update(self._media)
                .values(processed=True)
                .where(self._media.columns.filename == self.filename)
            )

        self.__connection.execute(query)
        logger.info("Update media table with new filename")
