# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.controllers.extraction.mmr import document_cutting
from AutoSummarization.controllers.tools.hanzi_edit import stops
import jieba
import jieba.posseg as psg
import math


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

    def remove_node(self, node):
        if node is self.head:
            self.head = self.head.next
        else:
            pre = self.head
            cur = pre.next
            while cur != None:
                if cur is node:
                    pre.next = cur.next
                    break
                else:
                    pre = cur
                    cur = pre.next
        return self.head

    def get_node(self):
        cur = self.head
        while cur != None:
            if cur.prop == 'n':
                cur = self.remove_node(cur)
            else:
                cur = cur.next

    """ This methhod aims to simplify the sentence in order to get summary """

    def deduction(self):
        pass

    def calculate_whole_entropy(self):
        prob = {}
        res = {}
        for item in set(self.whole_property_list):
            res[item] = self.whole_property_list.count(item)

        sums = sum(res[item] for item in res.keys())
        for item in res.keys():
            prob[item] = res[item] / sums

        entropy = 0.0
        for item in prob.keys():
            entropy += - prob[item] * math.log(prob[item], 2)
        return entropy

    def calculate_entropy(self):
        prob = {}
        res = {}
        cur = self.head
        prop_list = []
        while cur != None:
            prop_list.append(cur.prop)
            cur = cur.next

        for item in set(prop_list):
            res[item] = prop_list.count(item)

        sums = sum(res[item] for item in res.keys())
        for item in res.keys():
            prob[item] = res[item] / sums

        entropy = 0.0
        for item in prob.keys():
            entropy += - prob[item] * math.log(prob[item], 2)
        return entropy


if __name__ == '__main__':
    sentence = "调查负责人、一妇婴妇幼保健部主任花静介绍,根据2010年国民体质监测数据显示,上海市3至6岁学龄前儿童超重、肥胖率分别为15.98%和11.15%,两个数值均有所下降,,这个数据的变化跟近年来的政策引导、保健科普和观念改变有关,‘大胖小子’不再是公众追求,上海家庭在育儿方式上更科学,对健康的关注度也更高,,但同时值得注意的是,在运动能力上,肥胖和超重儿童在运动控制（大运动能力）、精细运动/书写能力、一般协调性、总体运动能力上均低于正常组,"
    s = document_cutting(sentence)
    for sentence in s:
        wl = SentenceTree(sentence)
        print(wl.word_list)
        print(wl.property_list)
        print(wl.calculate_whole_entropy())
        print(wl.calculate_entropy())
