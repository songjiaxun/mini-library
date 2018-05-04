# -*- coding: utf-8 -*-
import json
from format import Format
from info import Info
from validation import Validation

info = Info()
validation = Validation()
format = Format()

def initialize():
    ####
    ##初始化：读取 meta_data.json 文件中的配置信息
    ####
    try:
        with open('../data/meta_data.json','r') as file:
            json_data = json.load(file)
    except Exception:
        input("请确认“meta_data.json”文件保持关闭状态，并置于 data 文件夹下！") 

    ####        
    ##初始化:设置机构信息及登录密码
    ####
    if json_data['status'] == '0':
        print('软件初始化：请按提示输入相关信息！')
        json_data['status'] ='1'
        json_data['institution'] = input('【学校/机构名称】：')
        
        ####
        ##登录密码验证
        ####

        json_data['password'] = input('【登录密码】：')
        while (len(json_data['password']) < 6):
            print('弱密码：请使用至少6位数字作为密码')
            json_data['password'] = input('【登录密码】：')
        
        ####
        ##管理员密码验证
        ####
        json_data['adminpass'] = input('【管理员密码】：')        
        while (len(json_data['adminpass']) < 6 or (json_data['password'] == json_data['adminpass'])):
            if (len(json_data['adminpass']) < 6):
                print('弱密码：请使用至少6位数字作为密码')
            elif (json_data['password'] == json_data['adminpass']):
                print('弱密码：请勿使用【登录密码】作为【管理员密码】')
            json_data['adminpass'] = input('【管理员密码】：')

        ####
        ##数据保存
        ####
        with open('../data/meta_data.json','w') as file2:
            json.dump(json_data,file2)

    return (json_data['institution'], json_data['password'],json_data['adminpass']) 

def main():
    ####
    ##主界面
    ####
        ####
        ##主菜单
        ####
    menu = '\n请按指示进行相关操作：\n借书请按【1】\n还书请按【2】\n查询书目信息请按【3】\n查询读者信息请按【4】\n管理各类信息请按【5】\n帮助请按【6】\n退出请按【0】\n'
    
    # 获取当前数据库中已有的读者信息及书籍信息
    # info.book_Read()
    # info.reader_Read()    
    # TODO:数据备份,考虑是否可以删除，与其他操作中自带的备份功能似乎有重叠
    # info.reader_Write2Json(info.readerFile)
    # info.book_Write2Json(info.libFile)
        
        ####
        ##欢迎词
        ####
    format.breakLine()
    print(f'欢迎进入【{institution}】图书馆管理系统！')
    format.breakLine()

        ####
        ##登录密码验证
        ####
    password = input('请输入密码！退出请按【0】\n密码：')    
    while password != pw:
        if password == '0':
            return
        else:
            password = input("\n【密码错误！】\n请重新输入密码！退出请按0\n密码:")
        ####
        ##数据汇总
        ####
    format.breakLine()
    info.summary()
    print(f'图书馆现存图书【{info.bookKinds}】种, 共计图书【{info.bookTotal}】册，注册读者【{info.readerTotal}】人。')
    print(f'学生借书期限【{info.supposedReturnDays_students}】天，教师借书期限【{info.supposedReturnDays_teachers}】天。')

    content = validation.inputs(menu)

    ## 获取用户输入的菜单命令
    ## 1为借书，2为还书
    while content != '0':
        if content == '1':
            info.bookBorrow()
            # content = validation.inputs(globalvar.border1 + instruction)
    #     elif content == '2':
    #         info.reader_Write2Json(info.readerFile)
    #         info.book_Write2Json(info.libFile)
        else:
            print('wrong command!')           



institution, pw, adminpw = initialize()
main()