# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.models.entities import Deeplearning
from AutoSummarization.controllers import session_scope
import mxnet as mx
from mxnet import autograd, gluon, nd
from mxnet.gluon import nn, rnn, Block
from mxnet.contrib import text
import time
from io import open
import collections
import datetime
from sqlalchemy import func


def deeplearning_history(user):
    with session_scope() as db_session:
        summary = db_session.query(Deeplearning).filter(Deeplearning.user_id == user["id"]).all()
        ans = []
        for sum in summary:
            ans.append(sum.to_dict())
        return ans


def deeplearning_history_page(data, start, end):
    with session_scope() as db_session:
        res = {}
        sum = db_session.query(func.count(Deeplearning.id)).scalar()
        summary = db_session.query(Deeplearning).filter(Deeplearning.user_id == data["id"]).slice(start, end).all()
        ans = []
        for _summary in summary:
            ans.append(_summary.to_dict())
        res["sum"] = sum
        res["data"] = ans

        return res


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


PAD = '<pad>'
BOS = '<bos>'
EOS = '<eos>'
UNK = '<unk>'

max_doc_len = 152
max_summ_len = 35
max_seq_len = max(max_doc_len, max_summ_len)
ctx = mx.cpu(0)

base_path = "/Users/BoyLondon/Documents/LCSTS2.0/DATA/"
file_name = "PART_II(format).txt"


def read_data(max_doc_len, max_summ_len):
    doc_tokens = []
    summ_tokens = []
    document = []
    summary = []

    with open(base_path + file_name, encoding="utf8") as f:
        lines = f.readlines()
        for line in lines[1:101]:
            doc, summ = line.rstrip().split('<docgapsum>')
            cur_doc = get_word_list(doc)
            cur_summ = get_word_list(summ)

            if len(cur_doc) < max_doc_len and \
                            len(cur_summ) < max_summ_len:
                doc_tokens.extend(cur_doc)
                # 句末附上EOS符号。
                cur_doc.append(EOS)
                # 添加PAD符号使每个序列等长（长度为max_seq_len）。
                while len(cur_doc) < max_doc_len:
                    cur_doc.append(PAD)
                document.append(cur_doc)

                summ_tokens.extend(cur_summ)
                cur_summ.append(EOS)
                while len(cur_summ) < max_summ_len:
                    cur_summ.append(PAD)
                summary.append(cur_summ)

        doc_vocab = text.vocab.Vocabulary(collections.Counter(doc_tokens),
                                          reserved_tokens=[PAD, BOS, EOS])
        summ_vocab = text.vocab.Vocabulary(collections.Counter(summ_tokens),
                                           reserved_tokens=[PAD, BOS, EOS])

        doc_tokens.extend(summ_tokens)

        all_vocab = text.vocab.Vocabulary(collections.Counter(doc_tokens),
                                          reserved_tokens=[PAD, BOS, EOS])

    return doc_vocab, summ_vocab, all_vocab, document, summary


doc_vocab, summ_vocab, all_vocab, document, summary = read_data(max_seq_len, max_seq_len)
X = nd.zeros((len(document), max_seq_len), ctx=ctx)
Y = nd.zeros((len(summary), max_seq_len), ctx=ctx)

for i in range(len(document)):
    X[i] = nd.array(all_vocab.to_indices(document[i]), ctx=ctx)
    Y[i] = nd.array(all_vocab.to_indices(summary[i]), ctx=ctx)

dataset = gluon.data.ArrayDataset(X, Y)

encoder_num_layers = 1
decoder_num_layers = 2

encoder_drop_prob = 0.1
decoder_drop_prob = 0.1

encoder_hidden_dim = 256
decoder_hidden_dim = 256
alignment_dim = 25


class Encoder(Block):
    """编码器"""

    def __init__(self, input_dim, hidden_dim, num_layers, drop_prob):
        super(Encoder, self).__init__()
        with self.name_scope():
            self.embedding = nn.Embedding(input_dim, hidden_dim)
            self.dropout = nn.Dropout(drop_prob)
            self.rnn = rnn.GRU(hidden_dim, num_layers, dropout=drop_prob,
                               input_size=hidden_dim)

    def forward(self, inputs, state):
        # inputs尺寸: (batch_size, max_len)，emb尺寸: (max_len, batch_size, 256)
        emb = self.embedding(inputs).swapaxes(0, 1)

        emb = self.dropout(emb)
        output, state = self.rnn(emb, state)
        return output, state

    def begin_state(self, *args, **kwargs):
        return self.rnn.begin_state(*args, **kwargs)


class Decoder(Block):
    """含注意力机制的解码器"""

    def __init__(self, hidden_dim, output_dim, num_layers, max_seq_len,
                 drop_prob, alignment_dim, encoder_hidden_dim, batch_size):
        super(Decoder, self).__init__()
        self.max_seq_len = max_seq_len
        self.encoder_hidden_dim = encoder_hidden_dim
        self.hidden_size = hidden_dim
        self.num_layers = num_layers
        self.batch_size = batch_size

        with self.name_scope():
            self.embedding = nn.Embedding(output_dim, hidden_dim)
            self.dropout = nn.Dropout(drop_prob)
            # 注意力机制。
            self.attention = nn.Sequential()
            with self.attention.name_scope():
                self.attention.add(nn.Dense(
                    alignment_dim, in_units=hidden_dim + encoder_hidden_dim,
                    activation="tanh", flatten=False))
                self.attention.add(nn.Dense(1, in_units=alignment_dim,
                                            flatten=False))

            self.rnn = rnn.GRU(hidden_dim, num_layers, dropout=drop_prob,
                               input_size=hidden_dim)
            self.out = nn.Dense(output_dim, in_units=hidden_dim)
            self.rnn_concat_input = nn.Dense(
                hidden_dim, in_units=hidden_dim + encoder_hidden_dim,
                flatten=False)

    def forward(self, cur_input, state, encoder_outputs, is_train):

        # 当RNN为多层时，取最靠近输出层的单层隐含状态。
        single_layer_state = [state[0][-1].expand_dims(0)]

        # 用 is_train 来控制是训练还是测试，训练时每次读取batch_size个数据，测试时产生一个
        if is_train:
            encoder_outputs = encoder_outputs.reshape((self.max_seq_len, self.batch_size,
                                                       self.encoder_hidden_dim))
        else:
            encoder_outputs = encoder_outputs.reshape((self.max_seq_len, 1,
                                                       self.encoder_hidden_dim))

        # single_layer_state尺寸: [(1, batch_size, decoder_hidden_dim)], 1是num_layer大小
        # hidden_broadcast尺寸: (max_seq_len, batch_size, decoder_hidden_dim)
        hidden_broadcast = nd.broadcast_axis(single_layer_state[0], axis=0,
                                             size=self.max_seq_len)
        # print('hidden_broadcast',hidden_broadcast.shape)
        # encoder_outputs_and_hiddens尺寸:
        # (max_seq_len, batch_size, encoder_hidden_dim + decoder_hidden_dim)
        encoder_outputs_and_hiddens = nd.concat(encoder_outputs,
                                                hidden_broadcast, dim=2)

        # energy尺寸: (max_seq_len, batch_size, 1)，1是attention输出的一个标量e_t't
        energy = self.attention(encoder_outputs_and_hiddens)

        if is_train:
            batch_attention = nd.softmax(energy, axis=0).reshape(
                (self.batch_size, 1, self.max_seq_len))
        else:
            batch_attention = nd.softmax(energy, axis=0).reshape(
                (1, 1, self.max_seq_len))

        # 改变shape，让batch在dim==0上
        # batch_encoder_outputs尺寸: (batch_size, max_seq_len, encoder_hidden_dim)
        batch_encoder_outputs = encoder_outputs.swapaxes(0, 1)

        # decoder_context尺寸: (batch_size, 1, encoder_hidden_dim)
        decoder_context = nd.batch_dot(batch_attention, batch_encoder_outputs)

        # input_and_context尺寸: (batch_size, 1, encoder_hidden_dim + decoder_hidden_dim)
        # embedding size: (batch_size*1*256)
        if is_train:
            input_and_context = nd.concat(self.embedding(cur_input).reshape(
                (self.batch_size, 1, self.hidden_size)), decoder_context, dim=2)
        else:
            input_and_context = nd.concat(self.embedding(cur_input).reshape(
                (1, 1, self.hidden_size)), decoder_context, dim=2)

        # concat_input尺寸: (batch_size, 1, decoder_hidden_dim)
        concat_input = self.rnn_concat_input(input_and_context)
        concat_input = self.dropout(concat_input)

        # 当RNN为多层时，用单层隐含状态初始化各个层的隐含状态。
        state = [nd.broadcast_axis(single_layer_state[0], axis=0,
                                   size=self.num_layers)]

        # 这里做一个reshape，把 (batch_size, 1, decoder_hidden_dim) -> (1, batch_size, decoder_hidden_dim)
        # 因为 rnn.GRU 要求传入 shape=(sequence_length, batch_size, input_size)，（when layout is “TNC”）
        concat_input_exchange = concat_input.swapaxes(0, 1)
        output, state = self.rnn(concat_input_exchange, state)
        output = self.dropout(output)

        # 这里做一个reshape，因为self.out使用了Dense，所以需要把 batch_size 放入 dim0
        output = output.swapaxes(0, 1)
        output = self.out(output)
        # output尺寸: (batch_size, output_size)，hidden尺寸: [(1, 1, decoder_hidden_dim)]

        return output, state

    def begin_state(self, *args, **kwargs):
        return self.rnn.begin_state(*args, **kwargs)


class DecoderInitState(Block):
    # 解码器隐含状态的初始化

    def __init__(self, encoder_hidden_dim, decoder_hidden_dim):
        super(DecoderInitState, self).__init__()
        with self.name_scope():
            self.dense = nn.Dense(decoder_hidden_dim,
                                  in_units=encoder_hidden_dim,
                                  activation="tanh", flatten=False)

    def forward(self, encoder_state):
        return [self.dense(encoder_state)]


def translate(encoder, decoder, decoder_init_state, fr_ens, ctx, max_seq_len):
    rjson = {}
    num = 0
    rjson[str(num)] = {}
    for fr_en in fr_ens:
        #         print('Input :', fr_en[0])
        #         input_tokens = fr_en[0].split(' ') + [EOS]
        input_tokens = get_word_list(fr_en[0]) + [EOS]
        # 添加PAD符号使每个序列等长（长度为max_seq_len）。
        while len(input_tokens) < max_seq_len:
            input_tokens.append(PAD)
        inputs = nd.array(all_vocab.to_indices(input_tokens), ctx=ctx)
        encoder_state = encoder.begin_state(func=mx.nd.zeros, batch_size=1,
                                            ctx=ctx)
        encoder_outputs, encoder_state = encoder(inputs.expand_dims(0),
                                                 encoder_state)
        encoder_outputs = encoder_outputs.flatten()
        # 解码器的第一个输入为BOS字符。
        decoder_input = nd.array([all_vocab.token_to_idx[BOS]], ctx=ctx)
        decoder_state = decoder_init_state(encoder_state[0])
        output_tokens = []

        for i in range(max_seq_len):
            decoder_output, decoder_state = decoder(
                decoder_input, decoder_state, encoder_outputs, False)
            pred_i = int(decoder_output.argmax(axis=1).asnumpy())
            # 当任一时刻的输出为EOS字符时，输出序列即完成。
            if pred_i == all_vocab.token_to_idx[EOS]:
                break
            else:
                output_tokens.append(all_vocab.idx_to_token[pred_i])
            decoder_input = nd.array([pred_i], ctx=ctx)
        rjson[str(num)]["input"] = fr_en[0]
        rjson[str(num)]["output"] = ''.join(output_tokens)
        #         print('Output:', ' '.join(output_tokens))
        #         print('Expect:', fr_en[1], '\n')
        num += 1
        rjson[str(num)] = {}

    return rjson


batch_size = 4
encoder = Encoder(len(all_vocab), encoder_hidden_dim, encoder_num_layers,
                  encoder_drop_prob)

decoder = Decoder(decoder_hidden_dim, len(all_vocab),
                  decoder_num_layers, max_seq_len, decoder_drop_prob,
                  alignment_dim, encoder_hidden_dim, batch_size=batch_size)
decoder_init_state = DecoderInitState(encoder_hidden_dim, decoder_hidden_dim)

encoder.load_params("/Users/BoyLondon/Downloads/graduatedesign/AutomaticSummarization/AutomaticSummarizationBck/AutoSummarization/controllers/params/100_atten_encoder_b2_e100.params", ctx=ctx)
decoder.load_params("/Users/BoyLondon/Downloads/graduatedesign/AutomaticSummarization/AutomaticSummarizationBck/AutoSummarization/controllers/params/100_atten_decoder_b2_e100.params", ctx=ctx)
decoder_init_state.load_params("/Users/BoyLondon/Downloads/graduatedesign/AutomaticSummarization/AutomaticSummarizationBck/AutoSummarization/controllers/params/100_atten_decoder_init_state_b2_e100.params", ctx=ctx)

"""
{u'data': {u'id',
"""


def get_summary(data):
    document = data.get("document")
    input_sentence = [[document]]
    rjson = translate(encoder, decoder, decoder_init_state, input_sentence, ctx, max_seq_len)
    document = rjson["0"]["input"]
    ori_summary = rjson["0"]["output"]
    res = ""

    for word in ori_summary:
        if word != "<" and word != ">" and word not in ["p", "a", "d", "<pad>", " "]:
            res += word

    with session_scope() as db_session:
        deeplearning = Deeplearning()
        deeplearning.document = data.get("document")
        deeplearning.method = "deeplearning"
        deeplearning.summary = res
        deeplearning.create_time = int(time.time())
        deeplearning.user_id = data.get('id')
        db_session.add(deeplearning)

    return res
