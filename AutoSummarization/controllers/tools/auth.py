# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.PC_tools import encrypt
from AutoSummarization.controllers import session_scope
from AutoSummarization.models.entities import User
from AutoSummarization.utils import exceptions
from AutoSummarization.PC_tools import encrypt
import time


def auth_password(username, password):
    with session_scope() as db_session:
        query_password = db_session.query(User).filter(User.username == username).first()
        if query_password is None:
            raise exceptions.UserNotExist
        if encrypt.auth_password(username, password):
            return True
    return False


def create_user(data):
    with session_scope() as db_session:
        username, password = data.get("username"), data.get("password")
        nickname = data.get("nickname")
        create_time = int(time.time())
        encrypted_password = encrypt.encrypt(password, create_time)
        user = User()
        user.username = username
        user.nickname = nickname
        user.password = encrypted_password
        user.create_time = create_time
        user.last_login_time = create_time
        db_session.add(user)
        db_session.commit()


def reset_password(username, old_password, new_password):
    if encrypt.auth_password(username, old_password):
        if encrypt.reset_password(username, new_password):
            return True
    return False
