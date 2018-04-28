#!/usr/bin/python3

import logging
import time


def take_break(sleep_time):
    logging.warning("休息一下~ " + str(sleep_time) + '秒')
    print("----------------------------------------------------------------")
    time.sleep(sleep_time)


def get_from_file(file_name):
    """read data from files"""
    logging.info("读取文件" + file_name + "中的内容")
    result = {}
    exec(open(file_name).read(), None, result)
    return result
