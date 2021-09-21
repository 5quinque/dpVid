import os

import sqlalchemy as db

from . import PostProcess


class UpdateDB(PostProcess):
    def __init__(self, filename, new_filename=None, mime_type=None):
        super().__init__(filename, new_filename, mime_type)

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
            self._media.columns.filename == self.filename
        )

        ResultProxy = self.__connection.execute(query)
        ResultSet = ResultProxy.fetchall()

        print(ResultSet)

    def processed(self):
        if self.new_filename:
            query = (
                db.update(self._media)
                .values(
                    processed=True, filename=self.new_filename, mime_type=self.mime_type
                )
                .where(self._media.columns.filename == self.filename)
            )
        else:
            query = (
                db.update(self._media)
                .values(processed=True)
                .where(self._media.columns.filename == self.filename)
            )

        self.__connection.execute(query)
