# -*- coding: utf-8 -*-
from openpyxl import load_workbook
import json

class Info(object):
    """Info read/write class"""    
    def __init__(self,lib="../data/图书馆信息.xlsx",reader="../data/读者信息.xlsx"):
        ###
        ##数据初始化
        ###
        self.lib = lib
        self.reader = reader
        ###从两个excel文档和一个json文档中载入初始数据###
        try:
            lib_wk = load_workbook(lib)
            self.books = lib_wk.worksheets[0]#读取书籍信息
            self.books_lost = lib_wk.worksheets[1]#读取书籍遗失
        except Exception:
            input("请确认“图书馆信息.xlsx”文件保持关闭状态，并与置于data文件夹下！")                        
        try:
            reader_wk = load_workbook(reader)
            self.readers = reader_wk.worksheets[0]#读取读者信息
            self.log_borrow = reader_wk.worksheets[1]#读取借阅记录
        except Exception:
            input("请确认“读者信息.xlsx”文件保持关闭状态，并与置于data文件夹下！")
        ###从 meta_data.json 中读取配置信息###
        try:
            with open('../data/meta_data.json',"r") as file:
                meta_data = json.load(file)
                self.supposed_return_days_students = meta_data["student_days"]
                self.supposed_return_days_teachers = meta_data["teacher_days"]
        except Exception:
            input("请确认“meta_data.json”文件保持关闭状态，并与该软件置于同一目录下！") 
    def book_read(self):
        ###从excel文件读取图书信息###
        # rows = books.max_row
        print(self)               




