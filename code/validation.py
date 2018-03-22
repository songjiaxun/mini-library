# -*- coding: utf-8 -*-

class Validation(object):
    """输入验证模块"""
    def inputs(self,str):
        ##验证信息输入是否为空，若为空，重复提示内容。即原版的 input_request()###
        content = input(str)
        while content == '':
            content = input(str)
        return content

