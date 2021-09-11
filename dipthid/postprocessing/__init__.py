import os

import sqlalchemy as db


class PostProcess:
    def __init__(self, filename):
        __engine = db.create_engine(os.environ.get("DATABASE_URL"))
        self.__connection = __engine.connect()
        __metadata = db.MetaData()

        self._media = db.Table(
            "media", __metadata, autoload=True, autoload_with=__engine
        )

        self.filename = filename

    def getFile(self):
        query = db.select([self._media]).where(
            self._media.columns.filename == self.filename
        )

        ResultProxy = self.__connection.execute(query)
        ResultSet = ResultProxy.fetchall()

        print(ResultSet)

    def processed(self):
        query = (
            db.update(self._media)
            .values(processed=True)
            .where(self._media.columns.filename == self.filename)
        )
        self.__connection.execute(query)
