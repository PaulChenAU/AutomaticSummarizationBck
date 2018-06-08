# -*- coding:utf-8 -*-
# __author__=''

import mxnet as mx
from mxnet import autograd, gluon, nd
from mxnet.gluon import nn, rnn, Block
from mxnet.contrib import text


class Decoder(Block):
    """解码器"""

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
            self.rnn_concat_input = nn.Dense(
                hidden_dim, in_units=hidden_dim,
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
        #         energy = self.attention(encoder_outputs_and_hiddens)

        #         if is_train:
        #             batch_attention = nd.softmax(energy, axis=0).reshape(
        #                 (self.batch_size, 1, self.max_seq_len))
        #         else:
        #             batch_attention = nd.softmax(energy, axis=0).reshape(
        #                 (1, 1, self.max_seq_len))

        # 改变shape，让batch在dim==0上
        # batch_encoder_outputs尺寸: (batch_size, max_seq_len, encoder_hidden_dim)
        batch_encoder_outputs = encoder_outputs.swapaxes(0, 1)

        # decoder_context尺寸: (batch_size, 1, encoder_hidden_dim)
        #         decoder_context = nd.batch_dot(batch_attention, batch_encoder_outputs)

        # input_and_context尺寸: (batch_size, 1, encoder_hidden_dim + decoder_hidden_dim)
        # embedding size: (batch_size*1*256)
        #         if is_train:
        #             input_and_context = nd.concat(self.embedding(cur_input).reshape(
        #                 (self.batch_size, 1, self.hidden_size)), decoder_context, dim=2)
        #         else:
        #             input_and_context = nd.concat(self.embedding(cur_input).reshape(
        #                 (1, 1, self.hidden_size)), decoder_context, dim=2)

        if is_train:
            input_and_context = self.embedding(cur_input).reshape(
                (self.batch_size, 1, self.hidden_size))
        else:
            input_and_context = self.embedding(cur_input).reshape(
                (1, 1, self.hidden_size))

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
