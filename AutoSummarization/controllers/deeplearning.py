# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Deeplearning
from AutoSummarization.controllers import session_scope


def deeplearning_history(user):
    with session_scope() as db_session:
        summary = db_session.query(Deeplearning).filter(Deeplearning.user_id == user["id"]).all()
        ans = []
        for sum in summary:
            ans.append(sum.to_dict())
        return ans


"""
{u'data': {u'id',
"""


def get_summary(data):
    return None
