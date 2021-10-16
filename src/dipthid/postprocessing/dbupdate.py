import datetime
import logging
import os
from pathlib import Path

import requests
import sqlalchemy as db

from . import PostProcess

logger = logging.getLogger(__name__)


class UpdateDB(PostProcess):
    def __init__(self, filename, mime_type=None, old_filename=None):
        super().__init__(filename, mime_type, Path(old_filename).name)

        self.object_base_url = (
            os.environ.get("OBJECT_BASE_URL") + Path(self.filename).parent.name
        )

        self.__connection = self._db_connect()

    def _db_connect(self):
        self.__engine = db.create_engine(os.environ.get("DATABASE_URL"))

        connection = self.__engine.connect()
        __metadata = db.MetaData()

        self._media = db.Table(
            "media", __metadata, autoload=True, autoload_with=self.__engine
        )
        self._thumbnail = db.Table(
            "thumbnail", __metadata, autoload=True, autoload_with=self.__engine
        )

        return connection

    def get_file_id(self):
        query = db.select([self._media.c.post_id]).where(
            self._media.columns.filename == self.old_filename
        )
        ResultProxy = self.__connection.execute(query)
        (post_id,) = ResultProxy.first()

        return post_id

    def processed(self):
        file_id = self.get_file_id()

        self.update_media_record()
        self.create_thumbnail_record(file_id)

    def create_thumbnail_record(self, file_id):
        thumbnail_url = f"{self.object_base_url}/thumbnail.png"
        thumbnail_resp = requests.head(thumbnail_url)

        query = db.insert(self._thumbnail).values(
            post_id=file_id,
            filename="thumbnail.png",
            size=thumbnail_resp.headers.get("Content-Length"),
            mime_type=thumbnail_resp.headers.get("Content-Type"),
            created=datetime.datetime.now(),
            object_url=thumbnail_url,
        )

        self.__connection.execute(query)
        logger.info("Added thumbnail record")

    def update_media_record(self):
        query = (
            db.update(self._media)
            .values(
                processed=True,
                object_url=f"{self.object_base_url}/{Path(self.filename).name}",
                mime_type=self.mime_type,
                filesystem="media",
            )
            .where(self._media.columns.filename == self.old_filename)
        )

        self.__connection.execute(query)
        logger.info("Update media table with new filename")
