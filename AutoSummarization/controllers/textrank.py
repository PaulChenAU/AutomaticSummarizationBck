# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Textrank
from AutoSummarization.controllers import session_scope
from zhon.hanzi import punctuation
import re
import math
import jieba.posseg as pseg

property_list = ["a", "an", "n", "v"]


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
            if property in property_list:
                part_res.append(word)

        res.append(part_res)
    return res


def _get_similarity(wordlista, wordlistb):
    count = 0.0
    for worda in wordlista:
        if worda in wordlistb:
            count += 1
    base = math.log(len(wordlista), 2) + math.log(len(wordlistb), 2)
    return count / base if base != 0 else 0.0


def get_sentence_similarity(word_lists):
    res = []
    for i in range(0, len(word_lists) - 1):
        for j in range(i + 1, len(word_lists)):
            res.append((_get_similarity(word_lists[i], word_lists[j]), i, j))

    return res


# TODO
def get_similarity_topn(similarity_lists, topn):
    pass



