# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Deeplearning
from AutoSummarization.controllers import session_scope
import mxnet as mx
from mxnet import autograd, gluon, nd
from mxnet.gluon import nn, rnn, Block
from mxnet.contrib import text

from io import open
import collections
import datetime


def deeplearning_history(user):
    with session_scope() as db_session:
        summary = db_session.query(Deeplearning).filter(Deeplearning.user_id == user["id"]).all()
        ans = []
        for sum in summary:
            ans.append(sum.to_dict())
        return ans


PAD = '<pad>'
BOS = '<bos>'
EOS = '<eos>'
UNK = '<unk>'

max_doc_len = 152
max_summ_len = 35
max_seq_len = max(max_doc_len, max_summ_len)


def get_index_word_v3(line):
    number = 0
    word = ""
    begin = False
    for cha in line:
        if not ("\u4e00" <= cha <= "\u9fa5"):
            if cha == "<":
                word += cha
                begin = True
            elif cha == ">":
                begin = False
                word += cha
                yield number, word
                number += 1
                word = ""
            else:
                if begin:
                    word += cha
                else:
                    yield number, cha
                    number += 1
        else:
            if word != "":
                yield number, word
                word = ""
                number += 1
            else:
                yield number, cha


def get_word_list(line):
    res = []
    for number, cha in get_index_word_v3(line):
        res.append(cha)

    return res


def get_word_list_len(line):
    return len(get_word_list(line))


"""
{u'data': {u'id',
"""


def get_summary(data):
    return None
