# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.classes.vocab_tokenizer import VocabTokenizer
from AutoSummarization.classes.vocab_repository import VocabRepository
import math


class CalculateSimilarity(object):
    def __init__(self):
        pass

    # def cosine_similarity(self, VocabTokenizer, VocabRepository):
    #     cosine_count = 0
    #     for token in VocabTokenizer.token:
    #         if token in VocabRepository.vocab:
    #             cosine_count += 1
    #
    #     base = math.log(len(VocabTokenizer.token), 2) + math.log(len(VocabRepository.vocab), 2)
    #     return cosine_count / base if base != 0 else 0.0

    def _get_similarity(wordlista, wordlistb):
        if len(wordlista) == 0 or len(wordlistb) == 0:
            return 0.0
        count = 0.0
        for worda in wordlista:
            if worda in wordlistb:
                count += 1
        base = math.log(len(wordlista), 2) + math.log(len(wordlistb), 2)
        return count / base if base != 0 else 0.0

    @staticmethod
    def vectorize(VocabTokenizer, VocabRepository):
        ans = [0 for i in range(VocabRepository.length)]
        for i in range(VocabRepository.length):
            for j in range(VocabTokenizer.length):
                if VocabTokenizer.token[j] == VocabRepository.listvocab[i]:
                    ans[i] = 1

        return ans

    @staticmethod
    def cosine_similarity_repository(vector, VocabRepository):
        pass

    @staticmethod
    def cosine_similarity(vectora, vectorb):
        sums = 0.0
        for i in range(len(vectora)):
            sums += vectora[i] * vectorb[i]

        div = math.sqrt(len(vectora)) * math.sqrt(len(vectorb))

        return sums / div

