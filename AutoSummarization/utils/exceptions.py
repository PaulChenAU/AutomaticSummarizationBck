#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

except_dict = {
    'UserNotExist':{
        'code': 100001,
        'message': "User does not exist.",
        'zh_CN': "用户不存在"
    },
    'AuthFailed': {
        'code': 100001,
        'message': "authentication failed, because the password is not right.",
        'zh_CN': "验证失败,密码不正确"
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
