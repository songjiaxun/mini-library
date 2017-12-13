# -*- coding: utf-8 -*-
import json
from info import Info
from validation import Validation

info = Info()
validation = Validation()
border1 = '=================================================================================='
border2 = '----------------------------------------------------------------------------------'

def initialize():
    ###初始化###
    try:
        with open('../data/meta_data.json','r') as file:
            json_data = json.load(file)
    except Exception:
        input("请确认“meta_data.json”文件保持关闭状态，并置于 data 文件夹下！") 
    if json_data['status'] == '0':
        print('【软件初始化】，请按提示输入！')
        json_data['status'] ='1'
        json_data['institution'] = input('【学校/机构名称】：')
        json_data['password'] = input('【登录密码】：')
        
        while (len(json_data['password']) < 6):
            print('弱密码，请使用至少6位数字作为密码')
            json_data['password'] = input('【登录密码】：')
        
        json_data['admin'] = input('【管理员密码】：')
        
        while (len(json_data['admin']) < 6):
            print('弱密码，请使用至少6位数字作为密码')
            json_data['admin'] = input('【管理员密码】：')
        
        with open('../data/meta_data.json','w') as file2:
            json.dump(json_data,file2)
    return (json_data['institution'], json_data['password'],json_data['admin'])

def main():
    ###主界面###
    instruction = '\n请按指示进行相关操作：\n借书请按【1】\n还书请按【2】\n查询书目信息请按【3】\n查询读者信息请按【4】\n管理各类信息请按【5】\n帮助请按【6】\n退出请按【0】\n'
    info.reader_Write2Json(info.readerFile)
    info.book_Write2Json(info.libFile)
    print(border1)
    print("欢迎进入" + instit + "图书馆管理系统！")
    print(border1)
    password = input('请输入密码！退出请按【0】\n密码：')
    while password != pw:
        if password == "0":
            return
        else:
            password = input("\n【密码错误！】\n请输入密码！退出请按0\n密码:")
    print(border1)
    print("【密码正确，欢迎使用！】")
    print(border2)
    info.summary()
    print('图书馆现存图书【'+ str(info.bookKinds) +'】种, 共计图书【'+ str(info.bookAmount) +'】册，注册读者【'+ str(info.readerAmount) +'】人。')
    print('学生借书期限【'+ info.supposed_return_days_students +'】天，教师借书期限【'+ info.supposed_return_days_teachers + '】天。')
    content = validation.inputs(border1+instruction)
    while content != '0':
        if content == '1':
            #备份数据
            info.reader_Write2Json(info.readerFile)
            info.book_Write2Json(info.libFile)
            info.borrow()



instit, pw, pw_admin = initialize()
info.book_Read()
info.reader_Read()
main()