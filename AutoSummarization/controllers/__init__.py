#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

from AutoSummarization import config
from AutoSummarization.utils import getLogger
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

logger = getLogger(__name__)
engine = create_engine(
    config['database']['connection'].replace("mysql://", "mysql+pymysql://"),
    pool_size=config['database']['pool_size'],
    max_overflow=config['database']['max_overflow'],
    pool_recycle=3600,
    poolclass=QueuePool)
Session = sessionmaker(bind=engine)




@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations.

    provide a tran
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.exception(e)
        session.rollback()
        raise
    finally:
        session.close()
