# -*- coding: utf-8 -*-
import json
from info import Info



def initiallize():
    ###初始化###
    with open('../data/meta_data.json','r') as file:
        json_data = json.load(file)
    if json_data['status'] == '0':
        print('【软件初始化】，请按提示输入！')
        json_data['status'] ='1'
        json_data['institution'] = input('【学校/机构名称】：')
        json_data['password'] = input('【登录密码】：')
        json_data['admin'] = input('【管理员密码】：')
        with open('../data/meta_data.json','w') as file2:
            json.dump(json_data,file2)
    return (json_data['institution'], json_data['password'],json_data['admin'])

instit, pw, pw_admin = initiallize()
info = Info()
info.book_Read()
info.reader_Read()