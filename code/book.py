# -*- coding: utf-8 -*-
from validation import Validation
from info import Info

validation = Validation()
info = Info()

class Book(object):
    """ Book operations class"""
    def borrow(self):
        #借书操作
        reader_id = validation.inputs('请输入读者【借书号】，退出借书请按【0】\n读者借书号：')
        while reader_id !='0':
            try:
                req_reader = info.data_reader[reader_id]