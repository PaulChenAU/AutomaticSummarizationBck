#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

except_dict = {
    'LoginFailed': {
        'code': 1,
        'message': "LoginFailed",
        "zh_CN": "登录失败"
    }
}


def __str__(self):
    return self.message


def __repr__(self):
    return self.message


class HttpException(Exception):
    pass


exceptions_list = []
bases = (HttpException,)
attrs = {
    '__str__': __str__,
    '__repr__': __repr__
}

# generate error classes,
# add them to exception_list
# and then convert to exceptions tuple

for (eklass_name, attr) in except_dict.items():
    attrs.update(attr)
    eklass = type(str(eklass_name), bases, attrs)
    exceptions_list.append(eklass)
    globals().update({eklass_name: eklass})
