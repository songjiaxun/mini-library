from collections import deque
from datetime import datetime
import numpy as np
import pandas as pd
import sqlite3 as sql

import logging
import sys
import os
import traceback

from colorama import init, Fore
init(autoreset=True)

def _create_logger(logger_name):
    """
    创建日志
    """
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # create file handler
    log_path = f"./{logger_name}.log"
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

logger = _create_logger("mini-library")

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
        # 一共借阅过的本书
        self.checked_book_number = self.reader_history[self.reader_history["action"]=="借书"].shape[0]
        # 未还书籍列表
        self._unreturned_record = self._get_unreturned_record()
        # 借出未还的本书
        self.unreturned_book_number = self._unreturned_record.shape[0]
        # 过期未还记录
        self.due_record = self.cal_due_record()
        # 过期本数
        self.due_count = self.due_record.shape[0]

    def get_history(self):
        # global history_df
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
        print ((f"借书号：{self.reader_id}\n"
                f"姓名：{self.name}\n"
                f"性别：{self.gender}\n"
                f"单位：{self.unit}\n"
                f"借书权限：{self.access}\n"
                f"借书额度：{self.quota}\n"
                f"未还本书：{self.unreturned_book_number}\n"
                f"过期本书：{self.due_count}"))
        record = self.reader_history.copy()
        record.index = np.arange(1, len(record)+1)
        record = record.loc[:limit, ["date_time", "action", "isbn", "title"]]
        record.columns = ["时间", "动作", "ISBN", "标题"]
        if not len(record):
            print (Fore.RED + "【该读者暂无借阅记录。】")
        elif not limit:
            print (record)
        else:
            print (record.head(limit))
            if limit < len(self.reader_history):
                print ("记录太长已被省略，请至“管理各类信息”中查询完整记录。")

    def insert_hitory_record(self, reader, book, action):
        date_time = pd.Timestamp(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        unit = reader.unit
        reader_name = reader.name
        reader_id = reader.reader_id
        action = action
        isbn = book.isbn
        title = book.title
        location = book.location

        if reader.unit == "教师":
            return_day = int(meta_data["student_days"])
        else:
            return_day = int(meta_data["teacher_days"])
        record = (date_time, unit, reader_name, reader_id, action, isbn, title, location, return_day)
        record = pd.DataFrame([record], columns=["date_time", "unit", "reader_name", "reader_id", "action", 
                                                 "isbn", "title", "location", "return_day"])

        global history_df
        history_df = pd.concat([record, history_df], ignore_index=True)
        
    def check_in(self, book):
        if self.access != "开通":
            print (Fore.RED + "【借书失败：读者没有开通借书权限！】")
            return False
        if self.unreturned_book_number >= self.quota:
            print (Fore.RED + "【借书失败：读者超过借书额度！】")
            return False
        if self.due_count > 0:
            border2 = "-" * 80 # ...
            print (border2)
            print (Fore.RED + "【借书失败：读者有过期书籍，请还书后再借！】")
            temp = self.due_record.copy()
            temp = temp[["date_time", "action", "isbn", "title", "return_date"]]
            temp.columns = ["借书时间", "动作", "ISBN", "书籍", "应还书时间"]
            print ("过期书籍信息如下：")
            print (temp)
            return False
        if book.avaliable_number <= 0:
            print (Fore.RED + "【借书失败：馆藏本书不足！】")
            return False

        self.insert_hitory_record(self, book, "借书")
        self.update_data()
        book.update_data()
        update_sql()
        update_excel_history()
        print (Fore.GREEN + "【借书成功！】")
        return True

    def return_book(self, book):
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

    def loose_book(self, book):
        if book.isbn not in self._unreturned_record["isbn"].values:
            print (Fore.RED + "【读者未借阅该书籍！】")
            return False
        self.insert_hitory_record(self, book, "丢书")
        self.update_data()
        book.update_data()
        self.reader_access_revise("丢书")
        update_sql()
        update_excel_history()
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
        # 剩余在架的本书
        self.avaliable_number = self.cal_avaliable_number()

    def get_history(self):
        return history_df[history_df["isbn"]==self.isbn]

    def cal_avaliable_number(self):
        record = self.book_history.copy()
        record = record.sort_values("date_time")
        action_dic = {"借书" : -1, "还书" : 1, "丢书" : 0}
        result = self.total_number
        actions = record["action"]
        for action in actions:
            result += action_dic[action]
        return result

    def print_info(self, limit=None):
        print ((f"ISBN：{self.isbn}\n"
                f"标题：{self.title}\n"
                f"作者：{self.author}\n"
                f"出版社：{self.publisher}\n"
                f"位置：【{self.location}】\n"
                f"馆藏本书：{self.total_number}\n"
                f"剩余本书：{self.avaliable_number}"))
        record = self.book_history.copy()
        record.index = np.arange(1, len(record)+1)
        record = record.loc[:limit, ["date_time", "unit", "reader_name", "reader_id", "action"]]
        record.columns = ["时间", "单位", "读者ID", "读者", "动作"]
        if not len(record):
            print (Fore.RED + "【本书暂无借阅记录。】")
        elif not limit:
            print (record)
        else:
            print (record.head(limit))
            if limit < len(self.book_history):
                print ("记录太长已被省略，请至“管理各类信息”中查询完整记录。")

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

    writer_library = pd.ExcelWriter(os.path.join(os.getcwd(), "图书馆信息.xlsx"))
    readers_copy.to_excel(writer_library, sheet_name="读者", index=False)
    books_copy.to_excel(writer_library, sheet_name="书籍", index=False)
    writer_library.save()

def update_excel_history():
    history_copy = history_df.copy(deep=True)
    history_schema = ["时间", "单位", "姓名", "借书号", "动作", "ISBN", "书名", "书籍位置", "还书期限"]
    history_copy.columns = history_schema

    writer_history = pd.ExcelWriter(os.path.join(os.getcwd(), "借阅记录.xlsx"))
    history_copy.to_excel(writer_history, sheet_name="借阅记录", index=False)
    writer_history.save()

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

    writer_library = pd.ExcelWriter(os.path.join(backup_path, "图书馆信息.xlsx"))
    readers_df.to_excel(writer_library, sheet_name="读者", index=False)
    books_df.to_excel(writer_library, sheet_name="书籍", index=False)

    writer_history = pd.ExcelWriter(os.path.join(backup_path, "借阅记录.xlsx"))
    history_df.to_excel(writer_history, sheet_name="借阅记录", index=False)

    writer_library.save()
    writer_history.save()


def initiallize():
    """
    初始化
    """
    conn = get_connection()
    pd.DataFrame({}).to_sql('Meta', conn, if_exists='append') # making sure there's the table - will be revised later

    data = pd.DataFrame(pd.read_sql("SELECT * FROM Meta", conn))
    logger.info(data)

    # sanity check -- remove later: "status" not in data (when there's "status" but no item???)
    if "status" not in data:
        data["status"] = ["1"]
    elif data["status"].item() is None:
        print ("data['status'].item() is None")

    if data["status"].item() == "0":
        data["status"] = "1"
        print ("【软件初始化】，请按提示输入相应内容！")
        data["institution"] = input("【学校/机构名称】：")
        data["password"] = input("【登陆密码】：")
        data["administrator"] = input("【管理员密码】：")
        # use default values first
        data["student_days"] = 15
        data["teacher_days"] = 30
        data.to_sql("Meta", conn, if_exists="replace", index=False) # why False?
    return data


def start():
    logger.info("=" * 80)

    global meta_data, readers_df, books_df, history_df
    meta_data, readers_df, books_df, history_df = (None, None, None, None)
    
    try:
        logger.info("载入元数据")
        meta_data = initiallize()
    except:
        logger.error("元数据载入错误\n" + "".join(traceback.format_exception(*sys.exc_info())))
        print ("Bugs here. Contact the collaborator") # delete this later
    
    try:
        logger.info("载入读者、书籍数据")
        readers_df, books_df = load_data_libaray()
    except:
        logger.error("读者、书籍据载入错误\n" + "".join(traceback.format_exception(*sys.exc_info())))
        print ("请确认【图书馆信息.xlsx】文件保持关闭状态，并与该软件置于同一目录下！")
    
    try:
        logger.info("载入借阅数据")
        history_df = load_data_history()
    except:
        logger.error("借阅数据载入错误\n" + "".join(traceback.format_exception(*sys.exc_info())))
        print ("请确认【借阅记录.xlsx】文件保持关闭状态，并与该软件置于同一目录下！")

    return meta_data, readers_df, books_df, history_df
