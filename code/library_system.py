from collections import deque
from datetime import datetime
import getpass # 输入密码
import numpy as np
import pandas as pd
from spider import *
import data_manager as dm
import sys
import traceback
from colorama import Fore, Back, Style

###############################
# 系统设置
###############################

logger = dm.logger

# 中文对齐
pd.set_option('display.unicode.east_asian_width',True)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.expand_frame_repr',False)
pd.set_option('display.width',100)
pd.set_option('display.max_colwidth',50)
pd.set_option('display.max_row',500)

border1 = "=" * 100
border2 = "-" * 100

readers_dic = {}
books_dic = {}

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
        readers_dic[reader_id] = dm.Reader(readers_df[readers_df["reader_id"]==reader_id].iloc[0])
    return readers_dic[reader_id]

def book_to_obj(isbn, force=False):
    """
    在内存中创建Book对象
    """
    if isbn not in books_df["isbn"].values:
        return None
    elif isbn not in books_dic or force:
        books_dic[isbn] = dm.Book(books_df[books_df["isbn"]==isbn].iloc[0])
    return books_dic[isbn]

def retrieve_reader_book(reader_option, book_option, limit=5):
    """
    打印读者/书籍信息，创建对象，并返回对象
    """
    reader = None
    book = None

    if reader_option:
        print (border2)
        reader_id = input_request("输入读者借书号，按0退出\n")
        logger.info(f"输入读者借书号 - {reader_id}")
        while not reader_to_obj(reader_id) and reader_id != "0":
            reader_id = input_request("读者借书号不存在。输入读者借书号，按0退出\n")
        if reader_id != "0":
            reader = reader_to_obj(reader_id)
            reader.print_info(limit)
        else:
            return reader, book

    if book_option:
        print (border2)
        isbn = input_request("输入isbn号，按0退出\n")
        logger.info(f"输入isbn号 - {isbn}")
        while not book_to_obj(isbn) and isbn != "0":
            isbn = input_request("isbn不存在。输入isbn，按0退出\n")
        if isbn != "0":
            book = book_to_obj(isbn)
            book.print_info(limit)
        else:
            return reader, book

    return reader, book

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
        logger.info(f"从{name}获取书籍信息 - {isbn}")
        status, book_info = spider(isbn, data, 5)
        if status:
            book_info["status"] = True
            book_info["source"] = name
            break
    if not status:
        book_info["status"] = False
        book_info["source"] = None

    return book_info

def book_info_entry_batch():
    input ("若想批量录入图书请联系作者：chenshenghan.17@fellow.tfchina.org，谢谢！")

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
    统计馆藏本书、注册读者数等信息
    """
    book_number_unique = len(books_df)
    book_number = books_df["total_number"].sum()
    reader_number = len(readers_df)
    return book_number_unique, book_number, reader_number
  
###############################
# 管理员功能
###############################
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
            "九": "9", 
            "十": "10"            
            }
    groups = readers_df.groupby("unit")
    for unit, group in groups:
        if unit in ["教师", "老师"]:
            readers_df.iloc[group.index,0] = [f"{teacher_id:04d}" 
                                                for teacher_id in range(1, group.index.shape[0]+1)]
        else:
            grade_id = grade.get(unit[0], None)
            if grade_id:
                class_id = "0"
                for class_name in class_num:
                    if class_name in unit[1:]:
                        class_id = class_num[class_name]
                        break
                readers_df.iloc[group.index,0] = [f"{grade_id}{class_id}{student_id:02d}" 
                                                    for student_id in range(1, group.index.shape[0]+1)]
    dm.update_excel_library()

def info_summary():
    # 一般信息
    book_number_unique, book_number, reader_number = summary()
    supposed_return_days_students = meta_data["student_days"].item()
    supposed_return_days_teachers = meta_data["teacher_days"].item()
    print ("图书馆现存图书【{}】种，共计图书【{}】册，注册读者【{}】人。".format(book_number_unique, book_number, reader_number))
    print ("学生借书期限【{}】天，教师借书期限【{}】天。".format(supposed_return_days_students, supposed_return_days_teachers))
    print (border2)

    global history_df
    record = history_df.copy()
    record.index = np.arange(1, len(record)+1)
    # 今日借书记录
    today = record.loc[:, ["date_time", "reader_id", "unit", "reader_name", "action", "title"]]
    today = today[today["date_time"] >= pd.Timestamp(datetime.today().date())]
    today.columns = ["时间", "借书号", "单位", "读者", "动作", "书籍"]

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
    else:
        due_reader = pd.DataFrame()
    
    print ("最受欢迎的20本图书：")
    print (popular_book)
    print (border2)
    print ("最勤奋的20位读者：")
    print (good_reader)
    print (border2)
    print ("过期未还书的读者：")
    if not due_reader.empty:
        print (due_reader)
    else:
        print ("无过期未还书的读者")
    print (border2)
    print ("今日借阅记录（查看详细借阅记录请打开【借阅记录.xlsx】文件查询）：")
    if not today.empty:
        print (today)
    else:
        print ("无今日借阅记录")

###############################
# 管理员目录
###############################
def admin(password_admin):
    """
    管理员模块
    """
    global books_df
    print (border1)

    password = getpass.getpass(prompt="请输入【管理员密码】！退出请按【0】\n密码:") 
    while password != "0" and password != password_admin:
        print (Fore.RED + "【密码错误！】")
        password = getpass.getpass(prompt="请输入密码！退出请按【0】\n密码:")
    if password == "0":
        return
    instruction = ( "\n【管理员】请按指示进行相关操作："
                    "\n单本录入图书请按【1】"
                    "\n批量录入图书请按【2】"
                    "\n自动生成借书号请按【3】"
                    "\n修改读者权限请按【4】"
                    "\n设置还书期限请按【5】"
                    "\n重置密码及登录信息请按【6】"
                    "\n查看统计信息请按【7】"
                    "\n查询书目完整信息请按【8】"
                    "\n查询读者完整信息请按【9】"
                    "\n恢复备份文件请按【10】"
                    "\n退出请按【0】\n" )
    choice = input_request(border1 + instruction)

    while choice != "0":

        if choice == "1":
            logger.info("单本录入图书")
            print (border1)
            # 备份数据
            dm.update_sql()
            # 要求用户输入ISBN码，可以手动输入，也可以扫码枪输入
            isbn = input_request("输入ISBN，按0退出\n")
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
                        books_df = pd.concat([books_df, record], ignore_index=True, sort=False)
                    
                    # 更新excel
                    dm.update_excel_library()
                    
                    print (border2)
                    # 更新内存中的object
                    book_to_obj(isbn, force=True).print_info()
                    print (border2)
                isbn = input_request("输入ISBN，按0退出\n")

        elif choice == "2":
            # 逻辑比较难实现，暂时搁置
            logger.info("批量录入图书")
            print (border1)
            dm.update_sql()
            book_info_entry_batch()

        elif choice == "3":
            logger.info("自动生成借书号")
            print (border1)
            dm.update_sql()
            reader_id_generater()
            print (Fore.GREEN + "【读者借书号成功生成!】")
            return True
        
        elif choice == "4":
            logger.info("修改读者权限")
            dm.update_sql()
            reader, _ = retrieve_reader_book(True, False)
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
                    reader.print_info(5)
                    input (Fore.GREEN + "【读者权限修改成功！请按回车键返回。】")
                elif request == "2":
                    reader.reader_access_revise("暂停")
                    reader.print_info(5)
                    input (Fore.GREEN + "【读者权限修改成功！请按回车键返回。】")

        elif choice == "5":
            logger.info("设置还书期限")
            print (border1)
            student_days = input("【学生】借书期限（天）：")
            teacher_days = input("【教师】借书期限（天）：")
            confirm = "999"
            while confirm != "1" and confirm != "0":
                confirm = input_request(("该操作将设置读者借书期限，但【不会】影响书籍信息、读者信息和借阅记录。"
                                        "\n确认请按【1】，取消请按【0】"))
            if confirm == "1":
                meta_data["student_days"] = student_days # TODO 
                meta_data["teacher_days"] = teacher_days
                meta_data.to_sql("Meta", dm.get_connection(), if_exists="replace", index=False)
                print (Fore.GREEN + "【读者借书期限设置成功！】")
        
        elif choice == "6":
            logger.info("重置密码及登录信息")
            print (border1)
            confirm = "999"
            while confirm != "1" and confirm != "0":
                confirm = input_request(("该操作将重置软件登录信息及密码，但【不会】影响书籍信息、读者信息和借阅记录。"
                                        "\n确认请按【1】，取消请按【0】"))
            if confirm == "1":
                print (border2)
                meta_data["status"] = "0"
                meta_data.to_sql("Meta", dm.get_connection(), if_exists="replace", index=False)
                print (Fore.GREEN + "【密码及登录信息重置成功!】")
                return True
        
        elif choice == "7":
            logger.info("查看统计信息")
            print (border1)
            info_summary()

        elif choice == "8":
            logger.info("查询书目完整信息")
            retrieve_reader_book(False, True, None)
            input("请按回车键返回。")

        elif choice == "9":
            logger.info("查询读者完整信息")
            retrieve_reader_book(True, False, None)
            input("请按回车键返回。")

        elif choice == "10":
            logger.info("恢复备份文件")
            print (border1)
            print ("正在恢复文件中，请稍后...")
            dm.sql_to_excel()
            print (Fore.GREEN + "【文件恢复完成！】")
            print (Fore.GREEN + "【请返回到软件所在目录的“备份恢复”文件夹，用恢复所得文件覆盖原文件。】")
            return True

        else:
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
    print (f"欢迎进入{institution}图书馆管理系统！")
    print (border1)

    password = getpass.getpass(prompt="请输入密码！退出请按【0】\n密码:")
    while password != "0" and password != password_main:
        print (Fore.RED + "【密码错误！】")
        password = getpass.getpass(prompt="请输入密码！退出请按0\n密码:")
    if password == "0":
        return

    print (border1)
    print (Fore.GREEN + "【密码正确，欢迎使用！】")
    print (border2)
    
    book_number_unique, book_number, reader_number = summary()
    print (f"图书馆现存图书【{book_number_unique}】种，共计图书【{book_number}】册，注册读者【{reader_number}】人。")
    print (f"学生借书期限【{supposed_return_days_students}】天，教师借书期限【{supposed_return_days_teachers}】天。")
    
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
            reader, book = retrieve_reader_book(True, True)
            while reader and book:
                reader.check_in(book)
                reader, book = retrieve_reader_book(True, True)
        
        elif choice == "2":
            logger.info("还书")
            reader, book = retrieve_reader_book(True, True)
            while reader and book:
                reader.return_book(book)
                reader, book = retrieve_reader_book(True, True)
        
        elif choice == "3":
            logger.info("查询书目信息")
            _, book = retrieve_reader_book(False, True)
            while book:
                _, book = retrieve_reader_book(False, True)
        
        elif choice == "4":
            logger.info("查询读者信息")
            reader, _ = retrieve_reader_book(True, False)
            while reader:
                reader, _ = retrieve_reader_book(True, False)
        
        elif choice == "5":
            logger.info("管理各类信息")
            if admin(password_admin):
                input("【请点击回车键后重新打开软件！】")
                return
        
        elif choice == "6": 
            logger.info("帮助")
            print (border2)
            print (("感谢使用此套图书管理系统！"
                    "\n软件作者：陈胜寒、宋嘉勋"
                    "\n联系方式：E-mail: chenshenghan.17@fellow.tfchina.org | jiaxun.song@outlook.com"))
        
        else:
            logger.warn("代码错误")
            print (Fore.RED + "【错误代码，请重新输！】")
        
        choice = input_request(border1 + instruction)

if __name__ == '__main__':
    global meta_data, readers_df, books_df, history_df

    meta_data, readers_df, books_df, history_df = dm.start()

    if meta_data is not None and readers_df is not None and history_df is not None:
        try:
            logger.info("启动主程序")
            main(meta_data)
        except:
            logger.error("\n" + "".join(traceback.format_exception(*sys.exc_info())))
            input("软件运行出现错误，请联系作者：chenshenghan.17@fellow.tfchina.org，谢谢！")
