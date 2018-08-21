# -*- coding: utf-8 -*-

class Format(object):
    """Format class"""
    def __init__(self):
        pass
    def breakLine(self,string='-',count=50):
        ##打印分隔线##
        ##string:分割线样式字符串##
        ##count:样式字符串重复次数##
        print(string*count)
