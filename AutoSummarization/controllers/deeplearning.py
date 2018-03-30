# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Deeplearning
from AutoSummarization.controllers import session_scope


def deeplearning_history():
    with session_scope() as db_session:
        summary = db_session.query(Deeplearning).all()
        ans = []
        for sum in summary:
            ans.append(sum.to_dict())
        return ans
