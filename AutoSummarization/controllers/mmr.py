# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Mmr
from AutoSummarization.controllers import session_scope
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from AutoSummarization.classes.calculate_similarity import CalculateSimilarity
from AutoSummarization.classes.vocab_repository import VocabRepository
from AutoSummarization.classes.vocab_tokenizer import VocabTokenizer
from AutoSummarization.classes.calculate_similarity import CalculateSimilarity
from zhon.hanzi import punctuation
import re
import math
import time
import jieba.posseg as pseg
from sqlalchemy import func


def mmr_history(data):
    with session_scope() as db_session:
        res = {}
        sum = db_session.query(func.count(Mmr.id)).scalar()
        summary = db_session.query(Mmr).filter(Mmr.user_id == data["id"]).all()
        ans = []
        for _summary in summary:
            ans.append(_summary.to_dict())
        res["sum"] = sum
        res["data"] = ans

        return ans


def mmr_history_page(data, start, end):
    with session_scope() as db_session:
        res = {}
        sum = db_session.query(func.count(Mmr.id)).scalar()
        summary = db_session.query(Mmr).filter(Mmr.user_id == data["id"]).slice(start, end).all()
        ans = []
        for _summary in summary:
            ans.append(_summary.to_dict())
        res["sum"] = sum
        res["data"] = ans

        return res


def get_summary(data, compress_rate):
    compress_rate_val = float(compress_rate[:len(compress_rate) - 1]) / 100
    sentences_list = stemming(data.get("document"))
    summary_list = _get_summary(sentences_list, compress_rate_val)
    ans = []
    for sentence in sentences_list:
        if sentence in summary_list:
            ans.append(sentence)

    res = ",".join(ans)

    with session_scope() as db_session:
        mmr = Mmr()
        mmr.document = data.get("document")
        mmr.method = "mmr"
        mmr.summary = res
        mmr.create_time = int(time.time())
        mmr.user_id = data.get('id')
        mmr.compress_rate = compress_rate
        db_session.add(mmr)

    return res


def stemming(document):
    sentences = re.sub(r"[%s]+" % punctuation, "\n", document)
    sentences_list = []
    append_sen = ""
    for sen in sentences:
        if sen == '\n':
            sentences_list.append(append_sen)
            append_sen = ""
            continue
        append_sen += sen
    return sentences_list


def _get_summary(sentences_list, compress_rate_val):
    topn = int(len(sentences_list) * compress_rate_val)
    vocab_repo = VocabRepository(sentences_list)

    scores = get_similarity_score(sentences_list, vocab_repo)

    sentence_score = {}
    for sentence in scores.keys():
        sum = 0.0
        for sentence2 in scores[sentence].keys():
            sum += scores[sentence][sentence2]
        sentence_score[sentence] = sum

    summary_set = []

    alpha = 0.75
    while topn > 0:
        mmr = {}
        for sentence in sentences_list:
            if sentence not in summary_set:
                mmr[sentence] = alpha * sentence_score[sentence] - (1 - alpha) * set_similarity(scores, sentence,
                                                                                                summary_set)

        selected_sentence = max(mmr.items())[0]
        summary_set.append(selected_sentence)

        topn -= 1

    return summary_set


def set_similarity(scores, cmp_sentence, sentence_list):
    if sentence_list is None or len(sentence_list) == 0:
        return 0.0
    for sentence in scores.keys():
        if sentence == cmp_sentence:
            sum = 0.0
            for sentence2 in sentence_list:
                sum += scores[sentence][sentence2]
            break

    return sum


def get_similarity_score(sentences_list, vocab_repo):
    scores = {}
    for sentence in sentences_list:
        scores[sentence] = {}
        sentence_token = VocabTokenizer(sentence)
        sentence_vector = CalculateSimilarity.vectorize(sentence_token, vocab_repo)

        for sentence2 in sentences_list:
            if sentence != sentence2:
                sentence_token2 = VocabTokenizer(sentence2)
                scores[sentence][sentence2] = CalculateSimilarity.cosine_similarity(
                    CalculateSimilarity.vectorize(sentence_token, vocab_repo),
                    CalculateSimilarity.vectorize(sentence_token2, vocab_repo))

    return scores
