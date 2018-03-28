# -*- coding:utf-8 -*-
# __author__=''
import os
import re
from AutoSummarization import config


def get_avatar(username, avatar_size):
    abs_path = config["avatar"]["abs_path"]
    res = {}
    search_avatar = search(abs_path, username)
    res["file_path"] = search_avatar[0]
    res["mimetype"] = "image/" + search_avatar[1]
    return res


def search(abs_path, username):
    for file_name in os.listdir(abs_path):
        match = re.match(username + "_avatar.", file_name)
        if match:
            for i in range(0, len(file_name)):
                if file_name[i] == ".":
                    break
            return (file_name, file_name[i + 1:])
    return (abs_path + config["avatar"]["default_avatar"], config["avatar"]["default_type"])


# if __name__ == '__main__':
#     # print search(config["avatar"]["abs_path"], "admin")
