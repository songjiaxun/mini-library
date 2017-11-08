# -*- coding: utf-8 -*-
from openpyxl import load_workbook
import json

class Info(object):
    """Info read/write class"""    
    def __init__(self,lib="图书馆信息.xlsx",reader="读者信息.xlsx"):
        ###
        ##数据初始化
        ##Todo:增加自定义xlsx文件名供读取数据的功能
        ###
        self.lib = lib
        self.reader = reader
        ###从两个excel文档和一个json文档中载入初始数据###
        try:
            lib_wk = load_workbook(lib)
            reader_wk = load_workbook(reader)
            books = lib_wk.worksheets[0]#读取书籍信息
            readers = reader_wk.worksheets[0]#读取读者信息
            books_lost = lib_wk.worksheets[1]#读取书籍遗失
            log_borrow = reader_wk.worksheets[1]#读取借阅记录
        except Exception:
            input("请确认“图书馆信息.xlsx”和“读者信息.xlsx”文件保持关闭状态，并与该软件置于同一目录下！")
        ###从 meta_data.json 中读取配置信息###
        try:
            with open('meta_data.json',"r") as file:
                meta_data = json.load(file)
                supposed_return_days_students = json_data["student_days"]
                supposed_return_days_teachers = json_data["teacher_days"]
        except Exception:
            input("请确认“meta_data.json”文件保持关闭状态，并与该软件置于同一目录下！")                




