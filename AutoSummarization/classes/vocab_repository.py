# -*- coding:utf-8 -*-
# __author__=''
import jieba
from AutoSummarization.classes.vocab_tokenizer import VocabTokenizer


class VocabRepository(object):
    def __init__(self, sentences):
        self.vocab = set()
        for sentence in sentences:
            cut_sentence = jieba.cut(sentence)
            sentence_tokens = [txt for txt in cut_sentence]
            for token in sentence_tokens:
                self.vocab.add(token)
        self.listvocab = list(self.vocab)
        self.length = len(self.listvocab)
