# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.controllers.extraction.mmr import document_cutting
from AutoSummarization.controllers.tools.hanzi_edit import stops
import jieba
import jieba.posseg as psg


class Tree():
    def __init__(self):
        pass

    def gen_sentence_tree(self, sentence):
        pass


class WordNode():
    def __init__(self, word_pair):
        self.word, self.prop = word_pair
        self.next = None

    def __str__(self):
        return "word:%s, property:%s " % (self.word, self.prop)

    __repr__ = __str__


class SentenceTree():
    def __init__(self, sentence):
        ps = psg.cut(sentence, HMM=False)
        self.words = [word_pair for word_pair in ps]
        self.head = WordNode(self.words[0])
        cur = self.head
        for i in range(1, len(self.words)):
            word_node = WordNode(self.words[i])
            cur.next = word_node
            cur = word_node

    def reset_word_node(self):
        self.head = WordNode(self.words[0])
        cur = self.head
        for i in range(1, len(self.words)):
            word_node = WordNode(self.words[i])
            cur.next = word_node
            cur = word_node

    def get_head(self):
        return self.head

    def __str__(self):
        cur = self.head
        while cur != None:
            print(cur, end='')
            cur = cur.next
        return ""

    @property
    def whole_property_list(self):
        res = []
        for word_pair in self.words:
            word, prop = word_pair
            res.append(prop)
        return res

    @property
    def property_list(self):
        cur = self.head
        res = []
        while cur != None:
            res.append(cur.prop)
            cur = cur.next
        return res

    @property
    def whole_word_list(self):
        res = []
        for word_pair in self.words:
            word, prop = word_pair
            res.append(word)
        return res

    @property
    def word_list(self):
        cur = self.head
        res = []
        while cur != None:
            res.append(cur.word)
            cur = cur.next
        return res





if __name__ == '__main__':
    sentence = "调查负责人、一妇婴妇幼保健部主任花静介绍,根据2010年国民体质监测数据显示,上海市3至6岁学龄前儿童超重、肥胖率分别为15.98%和11.15%,两个数值均有所下降,,这个数据的变化跟近年来的政策引导、保健科普和观念改变有关,‘大胖小子’不再是公众追求,上海家庭在育儿方式上更科学,对健康的关注度也更高,,但同时值得注意的是,在运动能力上,肥胖和超重儿童在运动控制（大运动能力）、精细运动/书写能力、一般协调性、总体运动能力上均低于正常组,"
    s = document_cutting(sentence)
    for sentence in s:
        wl = SentenceTree(sentence)
        print(wl)
        print(wl.property_list)
