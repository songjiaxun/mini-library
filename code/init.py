# -*- coding: utf-8 -*-
import json
from info import Info

info = Info()
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
    password = input('请输入密码！推出请按【0】\n密码：')

instit, pw, pw_admin = initialize()
info.book_Read()
info.reader_Read()
main()