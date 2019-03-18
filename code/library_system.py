# -*- coding: utf-8 -*-

from collections import deque
from datetime import datetime
import getpass # 输入密码
import numpy as np
import pandas as pd
import sqlite3 as sql
from spider import *
import logging
import sys
import traceback
import os
from shutil import rmtree, copyfile
import platform
from colorama import Fore, Back, Style, init
init(autoreset=True)

###############################
# 系统设置
###############################

# 调整窗口大小，buffer，标题
from ctypes import windll, byref, c_bool, c_wchar_p, wintypes
STDOUT = -12
hdl = windll.kernel32.GetStdHandle(STDOUT)

bufsize = wintypes._COORD(121, 300) # rows, columns
windll.kernel32.SetConsoleScreenBufferSize(hdl, bufsize)

rect = wintypes.SMALL_RECT(0, 0, 120, 40) # (left, top, right, bottom)
windll.kernel32.SetConsoleWindowInfo(hdl, c_bool(True), byref(rect))

windll.kernel32.SetConsoleTitleW(c_wchar_p("图书馆管理系统"))

# 中文对齐
pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.expand_frame_repr',False)
pd.set_option('display.width',120)
pd.set_option('display.max_colwidth',20)
pd.set_option('display.max_row',500)

border1 = "=" * 120
border2 = "-" * 120

readers_dic = {}
books_dic = {}

def _create_logger(logger_name):
    """
    创建日志
    """
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # create file handler
    log_path = "./{}.log".format(logger_name)
    fh = logging.FileHandler(log_path, mode='a', encoding='gbk')
    # when mode = 'w', a new file will be created each time.
    fh.setLevel(logging.INFO)
    
    # create formatter
    fmt = "%(asctime)s %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    # add handler and formatter to logger
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

###############################
# 读者和书籍类
###############################
class Reader():
    def __init__(self, reader_info):
        self.reader_id = reader_info["reader_id"]
        self.name = reader_info["name"]
        self.gender = reader_info["gender"]
        self.unit = reader_info["unit"]
        self.access = reader_info["access"]
        self.quota = reader_info["quota"]
        self.update_data()

    def update_data(self):
        # 借阅记录
        self.reader_history = self.get_history()
        # 一共借阅过的本数
        self.checked_book_number = self.reader_history[self.reader_history["action"]=="借书"].shape[0]
        # 未还书籍列表
        self._unreturned_record = self._get_unreturned_record()
        # 借出未还的本数
        self.unreturned_book_number = self._unreturned_record.shape[0]
        # 过期未还记录
        self.due_record = self.cal_due_record()
        # 过期本数
        self.due_count = self.due_record.shape[0]

    def get_history(self):
        return history_df[history_df["reader_id"]==self.reader_id]

    def _get_unreturned_record(self):
        record = self.reader_history.copy()
        record = record.sort_values("date_time")
        index_list = []
        groups = record.groupby("isbn")
        for _, group in groups:
            queue = deque([])
            for i in group.index:
                if group.loc[i, "action"] == "借书":
                    queue.append(i)
                else:
                    queue.popleft()
            index_list += queue
        return record.loc[index_list]

    def cal_due_record(self):
        if self.unreturned_book_number > 0:
            record = self._unreturned_record.copy()
            record["return_day_obj"] = record["return_day"].apply(lambda day : pd.Timedelta(str(day) + " days"))
            record["return_date"] = record["date_time"] + record["return_day_obj"]
            return record[record["return_date"] < datetime.now()]
        return pd.DataFrame()

    def print_info(self, limit=None):
        print ("借书号：{}\n".format(self.reader_id)+
                "姓名：{}\n".format(self.name)+
                "性别：{}\n".format(self.gender)+
                "单位：{}\n".format(self.unit)+
                "借书权限：{}\n".format(self.access)+
                "借书额度：{}\n".format(self.quota)+
                "未还本数：{}\n".format(self.unreturned_book_number)+
                "过期本数：{}".format(self.due_count))
        record = self.reader_history.copy()
        record.index = np.arange(1, len(record)+1)
        record = record.loc[:limit, ["date_time", "action", "isbn", "title"]]
        record.columns = ["时间", "动作", "ISBN", "标题"]
        if not len(record):
            print (Fore.YELLOW + "【该读者暂无借阅记录。】")
        elif not limit:
            print (record)
        else:
            print (record.head(limit))
            if limit < len(self.reader_history):
                print ("借阅记录太长已被省略，请至“管理各类信息”中查询完整借阅记录。")

    def insert_hitory_record(self, reader, book, action):
        date_time = pd.Timestamp(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        unit = reader.unit
        reader_name = reader.name
        reader_id = reader.reader_id
        action = action
        isbn = book.isbn
        title = book.title
        location = book.location

        if reader.unit not in ["教师", "老师"]:
            return_day = int(meta_data["student_days"])
        else:
            return_day = int(meta_data["teacher_days"])
        record = (date_time, unit, reader_name, reader_id, action, isbn, title, location, return_day)
        record = pd.DataFrame([record], columns=["date_time", "unit", "reader_name", "reader_id", "action", 
                                                 "isbn", "title", "location", "return_day"])

        global history_df
        history_df = pd.concat([record, history_df], ignore_index=True)
        
    def check_out(self):
        if self.access != "开通":
            print (Fore.RED + "【借书失败：读者没有开通借书权限！】")
            return False
        if self.unreturned_book_number >= self.quota:
            print (Fore.RED + "【借书失败：读者借阅书目数量超过借书额度！】")
            return False
        if self.due_count > 0:
            border2 = "-" * 80
            print (border2)
            print (Fore.RED + "【借书失败：读者有过期书籍，请还书后再借！】")
            temp = self.due_record.copy()
            temp = temp[["date_time", "action", "isbn", "title", "return_date"]]
            temp.columns = ["借书时间", "动作", "ISBN", "书籍", "应还书时间"]
            print ("过期书籍信息如下：")
            print (temp)
            return False

        book = retrieve_reader_book("book")
        if not book:
            return False
        if book.avaliable_number <= 0:
            print (Fore.RED + "【借书失败：该书馆藏本数不足！】")
            return False

        self.insert_hitory_record(self, book, "借书")
        self.update_data()
        book.update_data()
        update_sql()
        update_excel_history()
        print (Fore.GREEN + "【借书成功！】")
        return True

    def return_book(self):
        if self._unreturned_record.shape[0] == 0:
            print (Fore.RED + "【读者没有借书记录！】")
            return False
        book = retrieve_reader_book("book")
        if not book:
            return False
        if book.isbn not in self._unreturned_record["isbn"].values:
            print (Fore.RED + "【读者未借阅该书籍！】")
            return False
        self.insert_hitory_record(self, book, "还书")
        self.update_data()
        book.update_data()
        update_sql()
        update_excel_history()
        print (Fore.GREEN + "【还书成功！】")
        return True

    def loose_book(self):
        if self._unreturned_record.shape[0] == 0:
            print (Fore.RED + "【读者没有借书记录！】")
            return False
        print (border2)
        print (Fore.YELLOW + "【读者所借书籍：】")
        unreturned_record = self._unreturned_record.copy()
        unreturned_record.index = np.arange(1, len(unreturned_record)+1)
        unreturned_record.index.name = "序号"
        unreturned_record = unreturned_record.loc[:, ["date_time", "action", "isbn", "title"]]
        unreturned_record.columns = ["时间", "动作", "ISBN", "标题"]
        print (unreturned_record)
        print (border2)
        index = input("请输入丢失条目序号（数字），退出请按【0】：")
        while not index.isdigit() or index != "0":
            if not index.isdigit():
                print (Fore.YELLOW + "【请确认输入数字！】")
                index = input("请输入丢失条目序号（数字），退出请按【0】：")
            elif int(index) > unreturned_record.shape[0] or int(index) < 0:
                print (Fore.YELLOW + "【请确认序号在列表格中！】")
                index = input("请输入丢失条目序号（数字），退出请按【0】：")
            else:
                break
        if index == "0":
            return False
        isbn = unreturned_record.loc[int(index), "ISBN"]
        book = book_to_obj(isbn)
        self.insert_hitory_record(self, book, "丢书")
        self.update_data()
        book.loose_book()
        book.update_data()
        self.reader_access_revise("丢书")
        update_sql()
        update_excel_history()
        print (border2)
        print (Fore.GREEN + "【设置丢失书籍成功！】")
        print (Fore.RED + "【丢失书籍，借书权限将被暂停！】")
        return True

    def reader_access_revise(self, access):
        self.access = access
        index = readers_df[readers_df["reader_id"]==self.reader_id].index
        readers_df.loc[index, "access"] = access
        update_sql()
        update_excel_library()

class Book():
    def __init__(self, book_info):
        self.isbn = book_info["isbn"]
        self.title = book_info["title"]
        self.author = book_info["author"]
        self.publisher = book_info["publisher"]
        self.publish_date = book_info["publish_date"]
        self.price = book_info["price"]
        self.total_number = book_info["total_number"]
        self.location = book_info["location"]
        self.update_data()

    def update_data(self):
        # 借阅记录
        self.book_history = self.get_history()
        # 一共借阅过的次数
        self.checked_book_number = self.book_history[self.book_history["action"]=="借书"].shape[0]
        # 剩余在架的本数
        self.avaliable_number = self.cal_avaliable_number()

    def get_history(self):
        return history_df[history_df["isbn"]==self.isbn]

    def cal_avaliable_number(self):
        record = self.book_history.copy()
        record = record.sort_values("date_time")
        action_dic = {"借书" : -1, "还书" : 1, "丢书" : 1}
        result = self.total_number
        actions = record["action"]
        for action in actions:
            result += action_dic[action]
        return result

    def loose_book(self):
        self.total_number -= 1
        index = books_df[books_df["isbn"]==self.isbn].index
        books_df.loc[index, "total_number"] = self.total_number
        update_sql()
        update_excel_library()

    def print_info(self, limit=None):
        print ("ISBN：{}\n".format(self.isbn)+
                "标题：{}\n".format(self.title)+
                "作者：{}\n".format(self.author)+
                "出版社：{}\n".format(self.publisher)+
                "位置：【{}】\n".format(self.location)+
                "馆藏本数：{}\n".format(self.total_number)+
                "剩余本数：{}".format(self.avaliable_number))
        record = self.book_history.copy()
        record.index = np.arange(1, len(record)+1)
        record = record.loc[:limit, ["date_time", "unit", "reader_name", "reader_id", "action"]]
        record.columns = ["时间", "单位", "读者ID", "读者", "动作"]
        if not len(record):
            print (Fore.YELLOW + "【本书暂无借阅记录。】")
        elif not limit:
            print (record)
        else:
            print (record.head(limit))
            if limit < len(self.book_history):
                print ("借阅记录太长已被省略，请至“管理各类信息”中查询完整借阅记录。")

###############################
# 载入数据
###############################
def load_data_libaray():
    readers_schema = ["reader_id", "name", "gender", "unit", "access", "quota"]
    books_schema = ["isbn", "title", "author", "publisher", "publish_date", "page_number", 
                    "price", "subject", "total_number", "call_no", "summary", "location"]
    readers = pd.read_excel("图书馆信息.xlsx", sheet_name=0, dtype={"借书号":str, "借书额度":int})
    books = pd.read_excel("图书馆信息.xlsx", sheet_name=1, dtype={"ISBN":str, "馆藏本数":int, "书籍位置":str})
    readers.columns = readers_schema
    books.columns = books_schema
    return readers, books

def load_data_history():
    history_schema = ["date_time", "unit", "reader_name", "reader_id", 
                      "action", "isbn", "title", "location", "return_day"]
    history_df = pd.read_excel("借阅记录.xlsx", sheet_name=0, dtype={"ISBN":str, "借书号":str, "还书期限":int})
    history_df.columns = history_schema
    history_df["date_time"] = history_df["date_time"].apply(lambda datetime : pd.Timestamp(datetime))
    return history_df

###############################
# 交换数据、备份数据
###############################
def delete_temp_files_and_backup_files(bundle_dir):
    print (bundle_dir)
    print ("\\".join(bundle_dir.split("\\")[:-1]))
    windows_version = platform.platform()
    bits = platform.architecture()[0]
    logger.info("系统版本：" + windows_version + ", " + bits)
    if windows_version.lower().startswith("windows-xp"):
        base_path = "{}\Local Settings\Temp".format(os.environ['USERPROFILE'])
    else:
        base_path = "{}\AppData\Local\Temp".format(os.environ['USERPROFILE'])
    print (base_path)
    logger.info("临时文件夹根目录：" + base_path)

    # 删除历史临时文件
    folders = list(filter(lambda folder : folder.startswith("_MEI"), os.listdir(base_path)))
    folders.sort(key=lambda folder: os.path.getmtime(os.path.join(base_path, folder)))
    for folder in folders[:-1]:
        if folder.startswith("_MEI"):
            logger.info("删除临时文件夹" + folder)
            rmtree(os.path.join(base_path, folder))
    
    # 如果软件所在目录没有所需的Excel文件，创建两个文件
    if False:
        pass
    # 如果软件所在目录存在所需的Excel文件，备份Excel文件
    else:
        for file in ["图书馆信息.xlsx", "借阅记录.xlsx"]:
            target_file = base_path + "\{}_{}.xlsx".format(file.split(".")[0], datetime.now().strftime('%Y-%m-%d-%H')) # 改变备份精度
            logger.info("备份文件：" + target_file)
            copyfile(file, target_file)

def get_connection(db_path='library.db'):
    return sql.connect(db_path, timeout=10)

def update_sql():
    conn = get_connection()
    readers_df.to_sql("Readers", conn, if_exists="replace", index=False)
    books_df.to_sql("Books", conn, if_exists="replace", index=False)
    history_df.to_sql("History", conn, if_exists="replace", index=False)

def update_excel_library():
    readers_copy = readers_df.copy(deep=True)
    books_copy = books_df.copy(deep=True)

    readers_schema = ["借书号", "姓名", "性别", "单位", "借书权限", "借书额度"]
    books_schema = ["ISBN", "书籍名称", "作者", "出版社", "出版日期", "页数", 
                    "价格", "主题", "馆藏本数", "索书号", "内容简介", "书籍位置"]

    readers_copy.columns = readers_schema
    books_copy.columns = books_schema

    with pd.ExcelWriter(os.path.join(os.getcwd(), "图书馆信息.xlsx")) as writer_library:
        readers_copy.to_excel(writer_library, sheet_name="读者", index=False)
        books_copy.to_excel(writer_library, sheet_name="书籍", index=False)

def update_excel_history():
    history_copy = history_df.copy(deep=True)
    history_schema = ["时间", "单位", "姓名", "借书号", "动作", "ISBN", "书名", "书籍位置", "还书期限"]
    history_copy.columns = history_schema

    with pd.ExcelWriter(os.path.join(os.getcwd(), "借阅记录.xlsx")) as writer_history:
        history_copy.to_excel(writer_history, sheet_name="借阅记录", index=False)

def sql_to_excel():
    conn = get_connection()
    readers_sql = "SELECT * FROM Readers"
    books_sql = "SELECT * FROM Books"
    history_sql = "SELECT * FROM History"

    readers_df = pd.read_sql(readers_sql, conn)
    books_df = pd.read_sql(books_sql, conn)
    history_df = pd.read_sql(history_sql, conn)

    readers_schema = ["借书号", "姓名", "性别", "单位", "借书权限", "借书额度"]
    books_schema = ["ISBN", "书籍名称", "作者", "出版社", "出版日期", "页数", 
                    "价格", "主题", "馆藏本数", "索书号", "内容简介", "书籍位置"]
    history_schema = ["时间", "单位", "姓名", "借书号", "动作", "ISBN", "书名", "书籍位置", "还书期限"]

    readers_df.columns = readers_schema
    books_df.columns = books_schema
    history_df.columns = history_schema

    backup_path = os.path.join(os.getcwd(), "备份恢复")
    if not os.path.isdir(backup_path):
        os.makedirs(backup_path)

    with pd.ExcelWriter(os.path.join(backup_path, "图书馆信息.xlsx")) as writer_library:
        readers_df.to_excel(writer_library, sheet_name="读者", index=False)
        books_df.to_excel(writer_library, sheet_name="书籍", index=False)

    with pd.ExcelWriter(os.path.join(backup_path, "借阅记录.xlsx")) as writer_history:
        history_df.to_excel(writer_history, sheet_name="借阅记录", index=False)

def initiallize():
    """
    初始化
    """
    conn = get_connection()
    data = pd.read_sql("SELECT * FROM Meta", conn)

    if data["status"].item() == 0:
        data["status"] = 1
        print ("【软件初始化】，请按提示输入相应内容！")
        data["institution"] = input("设置【学校/机构名称】：")
        data["password"] = input("设置【登陆密码】：")
        data["administrator"] = input("设置【管理员密码】：")
        # use default values first
        data["student_days"] = 15
        data["teacher_days"] = 30
        data.to_sql("Meta", conn, if_exists="replace", index=False)
    return data

###############################
# 初始化对象
###############################
def reader_to_obj(reader_id, force=False):
    """
    在内存中创建Reader对象
    """
    if reader_id not in readers_df["reader_id"].values:
        return None
    elif reader_id not in readers_dic or force:
        readers_dic[reader_id] = Reader(readers_df[readers_df["reader_id"]==reader_id].iloc[0])
    return readers_dic[reader_id]

def book_to_obj(isbn, force=False):
    """
    在内存中创建Book对象
    """
    if isbn not in books_df["isbn"].values:
        return None
    elif isbn not in books_dic or force:
        books_dic[isbn] = Book(books_df[books_df["isbn"]==isbn].iloc[0])
    return books_dic[isbn]

def retrieve_reader_book(option="reader", limit=5):
    """
    打印读者/书籍信息，创建对象，并返回对象
    """
    obj = None

    if option == "reader":
        print (border2)
        reader_id = input_request("输入读者借书号，按0退出：")
        logger.info("输入读者借书号 - {}".format(reader_id))
        while not reader_to_obj(reader_id) and reader_id != "0":
            reader_id = input_request("读者借书号不存在。\n输入读者借书号，按0退出：")
        if reader_id != "0":
            obj = reader_to_obj(reader_id)
            obj.print_info(limit)

    if option == "book":
        print (border2)
        isbn = input_request("输入ISBN号，按0退出：")
        logger.info("输入ISBN号 - {}".format(isbn))
        while not book_to_obj(isbn) and isbn != "0":
            isbn = input_request("ISBN不存在。\n输入ISBN号，按0退出：")
        if isbn != "0":
            obj = book_to_obj(isbn)
            obj.print_info(limit)

    return obj

###############################
# 爬虫相关
###############################
def book_info_entry_single(isbn):
    # 图书数据
    book_schema = ["isbn", "title", "author", "publisher", "publish_date", "page_number", 
               "price", "subject", "total_number", "call_no", "summary", "location"]
    data = {col : None for col in book_schema}

    # 检查isbn，本数和位置信息，如果不正确返回空值，不录入数据库
    # 检查isbn格式（由于豆瓣数据库不检查校验数位，且国内部分书籍校验数位不符，所以暂且只查基础格式是否正确）
    if (len(isbn) != 10 or not re.search(r'^(\d{9})(\d|X)$', isbn)) and (len(isbn) != 13 or not re.search(r'^(\d{12})(\d)$', isbn)):
        print (Fore.RED + "【{}为错误的ISBN码，应为[9位纯数字+'X'结尾]或[10位纯数字]或[13位纯数字]，请检查输入设备。】".format(isbn))
        return

    data["isbn"] = isbn
    # 输入书籍本数
    total_number = input("本数：")
    if total_number == "0":
        return
    if not total_number.isdigit():
        print (Fore.RED + "非数字！请重新输入！")
        return
    data["total_number"] = int(total_number)
    # 输入书籍位置
    location = input("位置：")
    if location == "0":
        return
    data["location"] = location

    # 如果书籍已经存在，询问是否合并
    if isbn in set(books_df["isbn"]):
        book_existed = book_to_obj(isbn)
        print (Fore.RED + "【书目已存在于数据库中】，信息如下：")
        print ("书籍名称:", book_existed.title)
        print ("馆藏本数:", book_existed.total_number)
        print ("书籍位置:", book_existed.location)
        print (border2)
        confirm = input_request(("【是否与现存书目信息合并？】"
                                 "\n现存书目将增加【{}】本，书籍位置依然为【{}】？"
                                 "\n确认请按【1】，取消请按【0】\n").format(data["total_number"], book_existed.location))
        while confirm != "1" and confirm != "0":
            confirm = input_request("确认请按【1】，取消请按【0】\n")
        if confirm == "1":
            data["total_number"] += book_existed.total_number
            return data
        else:
            # 如果不合并，返回空值
            return

    # 定义爬虫
    spider_functions = [getinfo_guotu1, getinfo_guotu2, getinfo_douban]
    spider_names = ["国图1", "国图2", "豆瓣"]
    # 从三个数据源依次获得数据
    for spider, name in zip(spider_functions, spider_names):
        logger.info("从{}获取书籍信息 - {}".format(name, isbn))
        status, book_info = spider(isbn, data, 5)
        if status:
            book_info["status"] = True
            book_info["source"] = name
            break
    if not status:
        book_info["status"] = False
        book_info["source"] = None

    return book_info

###############################
# 通用功能
###############################
def input_request(instruction):
    """
    信息输入
    """
    user_input = input(instruction)
    while user_input == "":
        user_input = input(instruction)
    return user_input

def summary():
    """
    统计馆藏本数、注册读者数等信息
    """
    book_number_unique = len(books_df)
    book_number = books_df["total_number"].sum()
    reader_number = len(readers_df)
    return book_number_unique, book_number, reader_number
  
###############################
# 管理员功能
###############################
def reset_history():
    global history_df
    history_df.drop(history_df.index, inplace=True)
    update_excel_history()

def reader_id_generater():
    """
    自动生成借书号
    """
    grade = {
            "一": "1",
            "二": "2",
            "三": "3",
            "四": "4",
            "五": "5",
            "六": "6",
            "七": "7",
            "八": "8",
            "九": "9"
            }    
    class_num = {
            "年级": "0",
            "甲": "1",
            "乙": "2",
            "丙": "3",
            "丁": "4",
            "一": "1",
            "二": "2",
            "三": "3",
            "四": "4",
            "五": "5",
            "六": "6",
            "七": "7",
            "八": "8",
            "九": "9"           
            }
    groups = readers_df.groupby("unit")
    for unit, group in groups:
        unit = unit.strip()
        if unit in set(["教师", "老师"]):
            readers_df.iloc[group.index,0] = ["{:04d}".format(teacher_id) 
                                                for teacher_id in range(1, group.index.shape[0]+1)]
        else:
            grade_id = grade.get(unit[0], None)
            if grade_id:
                class_id = "0"
                for class_name in class_num:
                    if class_name in unit[1:]:
                        class_id = class_num[class_name]
                        break
                readers_df.iloc[group.index,0] = ["{}{}{:02d}".format(grade_id, class_id, student_id) 
                                                    for student_id in range(1, group.index.shape[0]+1)]
    update_excel_library()

def info_summary():
    # 一般信息
    book_number_unique, book_number, reader_number = summary()
    supposed_return_days_students = meta_data["student_days"].item()
    supposed_return_days_teachers = meta_data["teacher_days"].item()
    print ("图书馆现存图书【{}】种，共计图书【{}】册，注册读者【{}】人。".format(book_number_unique, book_number, reader_number))
    print ("学生借书期限【{}】天，教师借书期限【{}】天。".format(supposed_return_days_students, supposed_return_days_teachers))
    print (border2)

    record = history_df.copy()
    record.index = np.arange(1, len(record)+1)
    # 今日借书记录
    today = record.loc[:, ["date_time", "reader_id", "unit", "reader_name", "action", "title"]]
    today = today[today["date_time"] >= pd.Timestamp(datetime.today().date())]
    today.columns = ["时间", "借书号", "单位", "读者", "动作", "书籍"]
    today = today.head(15)

    # 最受欢迎的20本图书
    popular_book = (record[record["action"]=="借书"].groupby(["isbn", "title", "location"])["reader_id"]
                                                    .count()
                                                    .sort_values(ascending=False)
                                                    .iloc[:20,])
    popular_book = pd.DataFrame(popular_book).reset_index()
    popular_book.columns = ["ISBN", "标题", "位置", "借阅次数"]
    popular_book.index = np.arange(1, min(20, len(popular_book))+1)

    # 最勤奋的20位读者
    good_reader = (record[record["action"]=="借书"].groupby(["reader_id", "reader_name", "unit"])["isbn"]
                                                    .count()
                                                    .sort_values(ascending=False)
                                                    .iloc[:20,])
    good_reader = pd.DataFrame(good_reader).reset_index()
    good_reader.columns = ["借书号", "姓名", "单位", "借阅次数"]
    good_reader.index = np.arange(1, min(20, len(good_reader))+1)

    # 过期未还书的读者
    due_reader = record
    due_reader = due_reader.sort_values("date_time")
    index_list = []
    groups = due_reader.groupby(["reader_id", "isbn"])
    for _, group in groups:
        queue = deque([])
        for i in group.index:
            if group.loc[i, "action"] == "借书":
                queue.append(i)
            else:
                try:
                    queue.popleft()
                except:
                    logger.error("借书记录错误！")
                    logger.error(group.loc[i, ["reader_name", "reader_id", "action"]])
        index_list += queue
    due_reader = due_reader.loc[index_list]

    if due_reader.shape[0] > 0:
        due_reader["return_day_obj"] = due_reader["return_day"].apply(lambda day : pd.Timedelta(str(day) + " days"))
        due_reader["return_date"] = due_reader["date_time"] + due_reader["return_day_obj"]
        due_reader = due_reader[due_reader["return_date"] < datetime.now()]
        due_reader = due_reader[["date_time", "reader_id", "unit", "reader_name", "title", "isbn", "return_date"]]
        due_reader.columns = ["借书时间", "借书号", "单位", "读者", "书籍", "ISBN", "应还书时间"]
        due_reader.index = np.arange(1, len(due_reader)+1)
    else:
        due_reader = pd.DataFrame()
    
    print (Fore.GREEN + "最受欢迎的20本图书：")
    if not popular_book.empty:
        print (popular_book)
    else:
        print ("暂无借阅记录。\n")
    print (border2)

    print (Fore.GREEN + "最勤奋的20位读者：")
    if not good_reader.empty:
        print (good_reader)
    else:
        print ("暂无借阅记录。\n")

    print (border2)
    print (Fore.RED + "过期未还书的读者：")
    if not due_reader.empty:
        print (due_reader)
    else:
        print ("无过期未还书的读者。\n")
    print (border2)

    print (Fore.YELLOW + "今日最近15条借阅记录（查看详细借阅记录请打开【借阅记录.xlsx】文件查询）：")
    if not today.empty:
        print (today)
    else:
        print ("无今日借阅记录。\n")

###############################
# 管理员目录
###############################
def admin(password_admin):
    """
    管理员模块
    """
    global books_df
    print (border1)

    password = getpass.getpass(prompt="请输入【管理员密码】！退出请按【0】\n密码（隐藏）:") 
    while password != "0" and password != password_admin:
        print (Fore.RED + "【密码错误！】")
        password = getpass.getpass(prompt="请输入密码！退出请按【0】\n密码（隐藏）:")
    if password == "0":
        return
    instruction = ( "\n【管理员】请按指示进行相关操作："
                    "\n单本录入图书请按【1】"
                    "\n新学年重置读者信息请按【2】"
                    "\n自动生成借书号请按【3】"
                    "\n修改读者权限请按【4】"
                    "\n读者丢失书籍请按【5】"
                    "\n设置借书期限请按【6】"
                    "\n重置密码及登录信息请按【7】"
                    "\n查看统计信息请按【8】"
                    "\n查询书目完整信息请按【9】"
                    "\n查询读者完整信息请按【10】"
                    "\n恢复备份文件请按【11】"
                    "\n退出管理员菜单请按【0】\n" )
    choice = input_request(border1 + instruction)

    while choice != "0":

        if choice == "1":
            logger.info("单本录入图书")
            print (border1)
            print (Fore.YELLOW + "【当前操作：单本录入图书】")
            print (border1)
            # 备份数据
            update_sql()
            # 要求用户输入ISBN码，可以手动输入，也可以扫码枪输入
            isbn = input_request("输入ISBN，按0退出\nISBN：")
            while isbn != "0":
                # 调用单本录入函数
                book_info = book_info_entry_single(isbn)
                # 如果有返回信息，说明用户输入信息格式正确
                if book_info:
                    book_schema = ["isbn", "title", "author", "publisher", "publish_date", "page_number", 
                                "price", "subject", "total_number", "call_no", "summary", "location"]
                    book_info_tuple = (book_info[col] for col in book_schema)
                    
                    # 如果ISBN已经存在，并且用户同意合并信息，则只更改已存在条目中书籍总数
                    if book_info["isbn"] in set(books_df["isbn"]):
                        books_df.loc[books_df[books_df["isbn"]==isbn].index, "total_number"] = book_info["total_number"]
                    else:
                        # 如果ISBN不存在，则插入新的信息
                        print (border2)
                        if book_info["status"]:
                            print (Fore.GREEN + "联网数据获得成功，数据源：{}".format(book_info["source"]))
                        else:
                            # 无论书籍信息是否获取成功，这一条信息都会被插入到excel中
                            print (Fore.RED + "联网数据获得失败，请打开“图书馆信息.xlsx”文件手动添加书籍信息。")
                        record = pd.DataFrame([book_info_tuple], columns=book_schema)
                        books_df = pd.concat([books_df, record], ignore_index=True)
                    
                    # 更新excel
                    update_excel_library()
                    
                    print (border2)
                    # 更新内存中的object
                    book_to_obj(isbn, force=True).print_info()
                    print (border2)
                isbn = input_request("输入ISBN，按0退出\nISBN：")

        elif choice == "2":
            logger.info("新学年重置读者信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：新学年重置读者信息】")
            print (border1)
            update_sql()
            print (Fore.RED + "！！请认真阅读以下说明！！")
            confirm = "999"
            while confirm != "1" and confirm != "0":
                confirm = input_request(("如果您在使用该软件默认的读者借书号命名规则，那么在每一学年初，由于班级年级变更，"
                                         "\n需要重置读者信息方能使用。如果您在使用其他借书号命名规则，则【无需】使用此功能。"
                                         "\n该操作将【删除】所有借阅记录，并且【自动生成借书号】，但【不会】影响书籍信息。"
                                         "\n请确认【已经完成】以下操作，否则请按【0】退出："
                                         "\n  （1）更新【图书馆信息.xlsx】中的读者信息，如添加新读者，更新班级信息等。"
                                         "\n  （2）如有需要，手动备份【借阅记录.xlsx】文件，即复制该文件至其它位置。"
                                         "\n  （3）完成以上两步之后，重新启动软件，再次进入该功能，按【1】完成操作。"
                                         "\n确认操作请按【1】，取消请按【0】"))
            if confirm == "1":
                reset_history()
                reader_id_generater()
                print (Fore.GREEN + "【新学年重置软件生成!】")
                return True

        elif choice == "3":
            logger.info("自动生成借书号")
            print (border1)
            print (Fore.YELLOW + "【当前操作：自动生成借书号】")
            print (border1)
            update_sql()
            reader_id_generater()
            print (Fore.GREEN + "【读者借书号成功生成!】")
            return True
        
        elif choice == "4":
            logger.info("修改读者权限")
            print (border1)
            print (Fore.YELLOW + "【当前操作：修改读者权限】")
            update_sql()
            reader = retrieve_reader_book("reader")
            if reader:
                request = input_request(("\n开通读者借书权限请按【1】"
                                        "\n暂停读者借书权限请按【2】"
                                        "\n退出请按【0】\n"))
                while request not in ["1", "2", "0"]:
                    request = input_request(("\n开通读者借书权限请按【1】"
                                            "\n暂停读者借书权限请按【2】"
                                            "\n退出请按【0】\n"))
                if request == "1":
                    reader.reader_access_revise("开通")
                    print (border2)
                    reader.print_info(5)
                    print (Fore.GREEN + "【读者权限修改成功！】")
                    input ("请按回车键返回。")
                elif request == "2":
                    reader.reader_access_revise("暂停")
                    print (border2)
                    reader.print_info(5)
                    print (Fore.GREEN + "【读者权限修改成功！】")
                    input ("请按回车键返回。")
        
        elif choice == "5":
            logger.info("读者丢失书籍")
            print (border1)
            print (Fore.YELLOW + "【当前操作：读者丢失书籍】")
            reader = retrieve_reader_book("reader")
            if reader:
                reader.loose_book()

        elif choice == "6":
            logger.info("设置借书期限")
            print (border1)
            print (Fore.YELLOW + "【当前操作：设置借书期限】")
            print (border1)
            student_days = input("【学生】借书期限（天）：")
            teacher_days = input("【教师】借书期限（天）：")
            confirm = "999"
            while confirm != "1" and confirm != "0":
                confirm = input_request(("该操作将设置读者借书期限，但【不会】影响书籍信息、读者信息和借阅记录。"
                                        "\n确认请按【1】，取消请按【0】"))
            if confirm == "1":
                meta_data["student_days"] = student_days
                meta_data["teacher_days"] = teacher_days
                meta_data.to_sql("Meta", get_connection(), if_exists="replace", index=False)
                print (Fore.GREEN + "【读者借书期限设置成功！】")
        
        elif choice == "7":
            logger.info("重置密码及登录信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：重置密码及登录信息】")
            print (border1)
            confirm = "999"
            while confirm != "1" and confirm != "0":
                confirm = input_request(("该操作将重置软件登录信息及密码，但【不会】影响书籍信息、读者信息和借阅记录。"
                                        "\n确认请按【1】，取消请按【0】"))
            if confirm == "1":
                print (border2)
                meta_data["status"] = 0
                meta_data.to_sql("Meta", get_connection(), if_exists="replace", index=False)
                print (Fore.GREEN + "【密码及登录信息重置成功!】")
                return True
        
        elif choice == "8":
            logger.info("查看统计信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：查看统计信息】")
            print (border1)
            info_summary()
            input("请按回车键返回。")

        elif choice == "9":
            logger.info("查询书目完整信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：查询书目完整信息】")
            retrieve_reader_book("book", None)
            input("请按回车键返回。")

        elif choice == "10":
            logger.info("查询读者完整信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：查询读者完整信息】")
            retrieve_reader_book("reader", None)
            input("请按回车键返回。")

        elif choice == "11":
            logger.info("恢复备份文件")
            print (border1)
            print (Fore.YELLOW + "【当前操作：恢复备份文件】")
            print (border1)
            print ("正在恢复文件中，请稍后...")
            sql_to_excel()
            print (Fore.GREEN + "【文件恢复完成！】")
            print (Fore.GREEN + "【请返回到软件所在目录的“备份恢复”文件夹，用恢复所得文件覆盖原文件。】")
            return True

        else:
            logger.warn("错误代码")
            print(Fore.RED + "【错误代码，请重新输！】")
        
        choice = input_request(border1 + instruction)

###############################
# 主目录
###############################
def main(meta_data):
    
    institution = meta_data["institution"].item()
    password_main = meta_data["password"].item()
    password_admin = meta_data["administrator"].item()
    supposed_return_days_students = meta_data["student_days"].item()
    supposed_return_days_teachers = meta_data["teacher_days"].item()

    print (border1)
    print ("欢迎进入{}图书馆管理系统！".format(institution))
    print (border1)

    password = getpass.getpass(prompt="请输入密码！退出请按【0】\n密码（隐藏）:")
    while password != "0" and password != password_main:
        print (Fore.RED + "【密码错误！】")
        password = getpass.getpass(prompt="请输入密码！退出请按【0】\n密码（隐藏）:")
    if password == "0":
        return

    print (border1)
    print (Fore.GREEN + "【密码正确，欢迎使用！】")
    print (border2)
    
    book_number_unique, book_number, reader_number = summary()
    print ("图书馆现存图书【{}】种，共计图书【{}】册，注册读者【{}】人。".format(book_number_unique, book_number, reader_number))
    print ("学生借书期限【{}】天，教师借书期限【{}】天。".format(supposed_return_days_students, supposed_return_days_teachers))
    
    instruction = ( "\n请按指示进行相关操作："
                    "\n借书请按【1】"
                    "\n还书请按【2】"
                    "\n查询书目信息请按【3】"
                    "\n查询读者信息请按【4】"
                    "\n管理各类信息请按【5】"
                    "\n帮助请按【6】"
                    "\n退出请按【0】\n" )
    choice = input_request(border1 + instruction)
    while choice != "0":
        
        if choice == "1":
            logger.info("借书")
            print (border1)
            print (Fore.YELLOW + "【当前操作：借书】")
            reader = retrieve_reader_book("reader")
            while reader:
                reader.check_out()
                print (border1)
                print (Fore.YELLOW + "【当前操作：借书】")
                reader = retrieve_reader_book("reader")
        
        elif choice == "2":
            logger.info("还书")
            print (border1)
            print (Fore.YELLOW + "【当前操作：还书】")
            reader = retrieve_reader_book("reader")
            while reader:
                reader.return_book()
                print (border1)
                print (Fore.YELLOW + "【当前操作：还书】")
                reader = retrieve_reader_book("reader")
        
        elif choice == "3":
            logger.info("查询书目信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：查询书目信息】")
            book = retrieve_reader_book("book")
            while book:
                print (border1)
                print (Fore.YELLOW + "【当前操作：查询书目信息】")
                book = retrieve_reader_book("book")
        
        elif choice == "4":
            logger.info("查询读者信息")
            print (border1)
            print (Fore.YELLOW + "【当前操作：查询读者信息】")
            reader = retrieve_reader_book("reader")
            while reader:
                print (border1)
                print (Fore.YELLOW + "【当前操作：查询读者信息】")
                reader = retrieve_reader_book("reader")
        
        elif choice == "5":
            logger.info("管理各类信息")
            if admin(password_admin):
                input("【请点击回车键后重新打开软件！】")
                return
        
        elif choice == "6": 
            logger.info("帮助")
            print (border2)
            print (("感谢使用此套图书管理系统！"
                    "\n软件作者：宋嘉勋、陈胜寒"
                    "\n联系方式：E-mail: jiaxun.song@outlook.com"
                    "\n如需寻求帮助，请在邮件标题中注明【图书馆软件问题】，在邮件正文中说明所遇到的问题，并将【library.log】、【借阅记录.xlsx】和【图书馆信息.xlsx】三个文件添加至附件一并发送，谢谢！"))
        
        else:
            logger.warn("代码错误")
            print (Fore.RED + "【错误代码，请重新输！】")
        
        choice = input_request(border1 + instruction)

###############################
# 载入数据
###############################
def load_data():
    meta_data, readers_df, books_df, history_df = (None, None, None, None)

    try:
        logger.info("载入元数据")
        meta_data = initiallize()
    except:
        logger.error("元数据载入错误\n" + "".join(traceback.format_exception(*sys.exc_info())))
        input ("请确认【library.db】与该软件置于同一目录下！")

    try:
        logger.info("载入读者、书籍数据")
        readers_df, books_df = load_data_libaray()
    except:
        logger.error("读者、书籍据载入错误\n" + "".join(traceback.format_exception(*sys.exc_info())))
        input ("请确认【图书馆信息.xlsx】文件保持关闭状态，并与该软件置于同一目录下！")

    try:
        logger.info("载入借阅数据")
        history_df = load_data_history()
    except:
        logger.error("借阅数据载入错误\n" + "".join(traceback.format_exception(*sys.exc_info())))
        input ("请确认【借阅记录.xlsx】文件保持关闭状态，并与该软件置于同一目录下！")

    return meta_data, readers_df, books_df, history_df

if __name__ == '__main__':
    # 获得版本信息
    if getattr( sys, 'frozen', False ) :
            bundle_dir=sys._MEIPASS
    else :
            bundle_dir=os.path.dirname(os.path.abspath(__file__))
    
    with open(os.path.join(bundle_dir, "VERSION"), "r") as file:
        VERSION = file.read()
    
    # 日志
    global logger    
    logger = _create_logger("library")
    logger.info("="*80)
    logger.info("软件版本：" + VERSION)

    # 删除临时文件
    try:
        delete_temp_files_and_backup_files(bundle_dir)
    except:
        logger.error("删除临时文件错误\n" + "".join(traceback.format_exception(*sys.exc_info())))        

    global meta_data, readers_df, books_df, history_df
    meta_data, readers_df, books_df, history_df = load_data()

    if meta_data is not None and readers_df is not None and books_df is not None and history_df is not None:
        try:
            logger.info("启动主程序")
            main(meta_data)
        except:
            logger.error("\n" + "".join(traceback.format_exception(*sys.exc_info())))
            input((border1 + "\n软件运行出现错误，请检查确认【借阅记录.xlsx】和【图书馆信息.xlsx】文件保持关闭状态。"
                   "\n如果问题持续无法解决，请联系作者：jiaxun.song@outlook.com，谢谢！"))
