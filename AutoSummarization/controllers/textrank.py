# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Textrank
from AutoSummarization.controllers import session_scope


def textrank_history():
    with session_scope() as db_session:
        summary = db_session.query(Textrank).all()
        ans = []
        for sum in summary:
            ans.append(sum.to_dict())
        return ans


"""
{u'data': {u'id',
"""


def get_summary(data):
    return None
