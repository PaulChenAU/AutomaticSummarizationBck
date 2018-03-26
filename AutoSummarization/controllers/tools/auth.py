# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.PC_tools import encrypt
from AutoSummarization.controllers import session_scope
from AutoSummarization.models.entities import User
from AutoSummarization.utils import exceptions
from AutoSummarization.PC_tools import encrypt


def auth_password(username, password):
    with session_scope() as db_session:
        query_password = db_session.query(User).filter(User.username == username).first()
        if query_password is None:
            raise exceptions.UserNotExist
        if encrypt.auth_password(username,password):
            return True
    return False




