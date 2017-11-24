# -*- coding: utf-8 -*-

class Validation(object):
    """输入验证模块"""
    def inputs(self,instruction):
        ##验证信息输入是否为空，若为空，重复提示内容。即原版的 input_request()###
        content = input(instruction)
        while content == '':
            content = input(instruction)
        return content

