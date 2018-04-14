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
    res = ",".join(_get_summary(data.get("document")))
    res += "."
    with session_scope() as db_session:
        textrank = Textrank()
        textrank.document = data.get("document")
        textrank.method = "textrank"
        textrank.summary = res
        textrank.user_id = data.get('id')
        db_session.add(textrank)

    return res


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


# TODO change base
def _get_similarity(wordlista, wordlistb):
    if len(wordlista) == 0 or len(wordlistb) == 0:
        return 0.0
    count = 0.0
    for worda in wordlista:
        if worda in wordlistb:
            count += 1
    base = math.log(len(wordlista), 2) + math.log(len(wordlistb), 2)
    return count / base if base != 0 else 0.0


def _get_sentence_similarity(word_lists):
    res = []
    for i in range(0, len(word_lists) - 1):
        res.append([])
        for j in range(i + 1, len(word_lists)):
            res[i].append(_get_similarity(word_lists[i], word_lists[j]))

    return res


def whole_similarity(word_lists):
    res = []
    triangle_sim = _get_sentence_similarity(word_lists)
    for i in range(len(triangle_sim)):
        res.append([])
        start, end = 0, i - 1
        for j in range(0, i):
            res[i].append(triangle_sim[start][end])
            start += 1
            end -= 1
        res[i].append(0.0)
        res[i].extend(triangle_sim[i])
    res.append(triangle_sim[0])

    return res


def textrank(sentences_similarity_lists, init_sentence_ws, d):
    # i represents the sentence number
    for i in range(len(sentences_similarity_lists)):
        sumwji = 0.0
        for j in range(len(sentences_similarity_lists[i])):
            if sentences_similarity_lists[i][j] != 0 and i != j:
                sumwjk = 0.0
                for k in range(len(sentences_similarity_lists[j])):
                    if sentences_similarity_lists[j][k] != 0 and k != i:
                        sumwjk += sentences_similarity_lists[j][k]
                sumwji += ((sentences_similarity_lists[i][j] / sumwjk) * init_sentence_ws[j]) if sumwjk != 0.0 else 0.0

        init_sentence_ws[i] = (1 - d) + d * (sumwji)

    return init_sentence_ws


def textrank_converge(sentences_similarity_lists, d):
    init_sentence_ws = [1 for i in range(len(sentences_similarity_lists))]
    for i in range(100):
        last_sum = sum(init_sentence_ws)
        new_ws = textrank(sentences_similarity_lists, init_sentence_ws, d)
        new_sum = sum(new_ws)
        init_sentence_ws = new_ws
    return init_sentence_ws


def get_topn(init_sentence_ws, topn):
    res = []
    for i in range(len(init_sentence_ws)):
        res.append((init_sentence_ws[i], i))
    sres = sorted(res, key=lambda x: x[0], reverse=True)
    return sres[:topn]


def _get_summary(data):
    sentences_list = textrank_stemming(data)
    word_lists = textrank_participle(sentences_list)
    similarity = whole_similarity(word_lists)
    sentece_ws = textrank_converge(similarity, d=0.85)
    topn = get_topn(sentece_ws, topn=int(len(sentences_list) / 2))
    stopn = sorted(topn, key=lambda x: x[1])
    sans = []
    for i in range(len(stopn)):
        sans.append(sentences_list[stopn[i][1]])
    return sans
