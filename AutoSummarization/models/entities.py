#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

import time

from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import VARCHAR
from sqlalchemy import DECIMAL
from sqlalchemy import TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixin:
    def to_dict(self, exclude_columns=None):
        """Convert to dict.

        convert the entity object to dict without relationships
        """
        if exclude_columns is None:
            exclude_columns = []
        d = {}
        for column in self.__table__.columns:
            if unicode(column.name) in exclude_columns:
                continue
            d[column.name] = getattr(self, column.name)

        return d


class BaseId:
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class BaseEntity:
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    create_time = Column(BigInteger, nullable=False)
    update_time = Column(BigInteger, nullable=False)

    def set_create_table_base(self):
        """Set base parameters for object.

        Set create / update time for object
        """
        now = int(time.time())
        self.create_time = now
        self.update_time = now

    def set_update_table_base(self):
        """Set base parameters for object update.

        Set update time for object
        """
        now = int(time.time())
        self.update_time = now


class Summary(Base, BaseMixin, BaseId):
    __tablename__ = "summary"

    document = Column(TEXT)
    summary = Column(TEXT)
    method = Column(VARCHAR(255))
    user_id = Column(BigInteger)


class User(Base, BaseMixin):
    __tablename__ = "user"

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    username = Column(VARCHAR(255))
    nickname = Column(VARCHAR(255))
    password = Column(VARCHAR(255))
    create_time = Column(BigInteger)
    last_login_time = Column(BigInteger)
