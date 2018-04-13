# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Textrank
from AutoSummarization.controllers import session_scope
from zhon.hanzi import punctuation
import re
import jieba.posseg as pseg


# TODO punctuation add

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


def textrank_stemming(doc):
    sentences = re.sub(ur"[%s]+" % punctuation, "\n", doc)
    sentences_list = []
    append_sen = ""
    for sen in sentences:
        if sen == '\n':
            sentences_list.append(append_sen)
            append_sen = ""
            continue
        append_sen += sen
    return sentences_list


def textrank_participle(sentences_list):
    res = []
    for sentence in sentences_list:
        part = pseg.cut(sentence)
        part_res = []
        for word, property in part:
            if property == "a" or property == "an" or property == "n" or property == "v":
                part_res.append(word)

        res.append(part_res)
    return res


