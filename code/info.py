# -*- coding: utf-8 -*-
from openpyxl import load_workbook
import json

class Info(object):
    """Info read/write class"""    
    def __init__(self,libFile="../data/图书馆信息.xlsx",readerFile="../data/读者信息.xlsx"):
        ###
        ##数据初始化
        ###
        self.libFile = libFile
        self.readerFile = readerFile
        self.data_book = {}
        self.data_reader = {}
        ###从两个excel文档和一个json文档中载入初始数据###
        try:
            libWorkbook = load_workbook(libFile)
            self.books = libWorkbook.worksheets[0]#读取书籍信息
            self.books_lost = libWorkbook.worksheets[1]#读取书籍遗失
        except Exception:
            input("请确认“图书馆信息.xlsx”文件保持关闭状态，并与置于data文件夹下！")                        
        try:
            readerWorkbook = load_workbook(readerFile)
            self.readers = readerWorkbook.worksheets[0]#读取读者信息
            self.log_borrow = readerWorkbook.worksheets[1]#读取借阅记录
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
    def book_Read(self):
        ###从excel文件读取图书信息###
        books = self.books 
        rows = books.max_row
        for book in range(2, rows+1):
            if books.cell(row=book,column=13).value == None:
                borrowed_times = 0
            else:
                borrowed_times = books.cell(row=book,column=13).value
            if not str(books.cell(row=book,column=1).value).isdigit():
                isbn = "0"
            else:
                isbn = str(books.cell(row=book,column=1).value)
            if not str(books.cell(row=book,column=9).value).isdigit():
                amount = 0
            else:
                amount = int(books.cell(row=book,column=9).value)
            info_book = {
                "row": book,
                "ISBN": isbn,
                "书籍名称": books.cell(row=book,column=2).value,
                "作者": books.cell(row=book,column=3).value,
                "出版社": books.cell(row=book,column=4).value,
                "出版日期": books.cell(row=book,column=5).value,
                "页数": books.cell(row=book,column=6).value,
                "价格": books.cell(row=book,column=7).value,
                "主题": books.cell(row=book,column=8).value,
                "馆藏本数": amount,
                "索书号": books.cell(row=book,column=10).value,
                "书籍位置": books.cell(row=book,column=15).value,
                "借阅次数": borrowed_times,
                "借阅记录": books.cell(row=book,column=14).value,
                "内容简介": books.cell(row=book,column=11).value,
                "信息来源": books.cell(row=book,column=12).value
            }                         
            self.data_book[isbn] = info_book
    def reader_Read(self):
        ###从excel文件读取读者信息###
        readers = self.readers 
        rows = readers.max_row
        for reader in range(2, rows+1):
            if readers.cell(row=reader,column=11).value == None:
                count = 0
            else:
                count = readers.cell(row=reader,column=11).value
            if readers.cell(row=reader,column=12).value == None:
                borrowed_times = 0
            else:
                borrowed_times = readers.cell(row=reader,column=12).value
            if not str(readers.cell(row=reader, column=1).value).isdigit():
                reader_id= 0
            else:
                reader_id = str(readers.cell(row=reader,column=1).value)
            info_reader = {
                "row": reader,
                "借书号": reader_id,
                "姓名": readers.cell(row=reader,column=2).value,
                "性别": readers.cell(row=reader,column=3).value,
                "单位": readers.cell(row=reader,column=4).value,
                "所借书目": readers.cell(row=reader,column=5).value,
                "借书日期": readers.cell(row=reader,column=6).value,
                "应还日期": readers.cell(row=reader,column=7).value,
                "还书日期": readers.cell(row=reader,column=8).value,
                "借书记录": readers.cell(row=reader,column=9).value,
                "借书权限": readers.cell(row=reader,column=10).value,
                "过期次数": count,
                "借阅次数": borrowed_times
            }                         
            self.data_reader[reader_id] = info_reader  
        print(self.data_reader)                


