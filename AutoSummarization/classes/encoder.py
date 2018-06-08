# -*- coding:utf-8 -*-
# __author__=''
import mxnet as mx
from mxnet import autograd, gluon, nd
from mxnet.gluon import nn, rnn, Block
from mxnet.contrib import text

class Encoder(Block):

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