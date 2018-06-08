# -*- coding:utf-8 -*-
# __author__=''
import jieba
import math


class VocabTokenizer(object):
    def __init__(self, sentence):
        cut_sentence = jieba.cut(sentence)
        self.token = [txt for txt in cut_sentence]
        self.length = len(self.token)

    def _get_similarity(wordlista, wordlistb):
        if len(wordlista) == 0 or len(wordlistb) == 0:
            return 0.0
        count = 0.0
        for worda in wordlista:
            if worda in wordlistb:
                count += 1
        base = math.log(len(wordlista), 2) + math.log(len(wordlistb), 2)
        return count / base if base != 0 else 0.0

    def cosine_similarity(self):
        pass
