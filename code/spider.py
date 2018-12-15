# -*- coding: utf-8 -*-

import requests
from lxml import etree
import re

def connect_url(url, parser=etree.HTML, i=3, timeout=3):
    req = None
    for _ in range(i):
        try:
            req = requests.get(url=url, timeout=timeout)
            if req.status_code == 200:
                root = parser(req.content)
                return True, root
            else:
                return False, "bad connection"
        except:
            pass
    
    if not req:
        return False, "bad network"

def getinfo_douban(isbn, data, timeout=10):
    """
    豆瓣API
    没有主题和索书号信息
    """
    print ("从豆瓣图书数据库中获得数据...")
    data["isbn"] = isbn
    
    url = "http://api.douban.com/book/subject/isbn/" + isbn
    
    status, msg = connect_url(url, parser=etree.XML, timeout=timeout)
    
    if status:
        root = msg
    else:
        if msg == "bad connection":
            print ("豆瓣图书数据库中无该书目！")
            return False, data
        if msg == "bad network":
            print ("网络连接故障！")
            return False, data        

    attributes = root.findall('{http://www.douban.com/xmlns/}attribute')
    for attribute in attributes:
        if attribute.attrib["name"] == "pages":
            data["page_number"] = attribute.text
        if attribute.attrib["name"] == "author":
            data["author"] = attribute.text
        if attribute.attrib["name"] == "price":
            data["price"] = attribute.text
        if attribute.attrib["name"] == "publisher":
            data["publisher"] = attribute.text
        if attribute.attrib["name"] == "pubdate":
            data["publish_date"] = attribute.text    
    try:
        title = root.find('./{http://www.w3.org/2005/Atom}title').text
        data["title"] = "《{}》".format(title)
        data["summary"] = root.find('./{http://www.w3.org/2005/Atom}summary').text
        if data["summary"]:
            data["summary"] = re.sub(r"[\\n\s\n\t\r]+", "", data["summary"])
    except:
        pass
    
    return True, data

def getinfo_guotu1(isbn, data, timeout=10):
    """
    国家图书馆数据库1，首选
    """
    print ("从国家图书馆数据库1中获得数据...")
    data["isbn"] = isbn
    
    # 尝试获得key
    url_main = "http://opac.nlc.cn/F/"
    status, msg = connect_url(url_main, timeout=timeout)
    if status:
        root_key = msg
        try:
            key = re.findall(r"opac.nlc.cn:80\/F\/(.+)\-", root_key.xpath('//head/meta[@http-equiv="REFRESH"]/@content')[0])[0]
        except:
            print ("网络连接故障！")
            return False, data            
    else:
        print ("网络连接故障！")
        return False, data
    
    # 搜索url
    url = "http://opac.nlc.cn/F/" + key + "?func=find-b&find_code=ISB&request=" + isbn
    
    # 尝试连接搜索url
    status, msg = connect_url(url, timeout=timeout)
    if status:
        root_main = msg
    else:
        print ("网络连接故障！")
        return False, data
    
    # 如果返回的是一个图书列表，获得列表中第一本书的url
    if str(root_main.xpath('/comment()')[0]) == "<!-- filename: short-2-head  -->":
        print ("查找到多本图书，正在选取列表中的第一本！")
        try:
            url = root_main.xpath('//*[@id="brief"]/table/tr[1]/td[1]/div[2]/table/tr/td[3]/div/a[1]/@href')[0]
        except:
            print ("国家图书馆数据库1中无该书目！")
            return False, data            
        status, msg = connect_url(url, timeout=timeout)
        if status:
            root = msg
        else:
            print ("网络连接故障！")
            return False, data        
    else:
        root = root_main
    
    # 解析图书信息
    try:
        for e in root.xpath('/html/head/comment()'):
            if str(e).find("publish section")>0:
                comment = str(e)
                break

        info_comment = re.findall(r'(ISBN[\w\W\d\W\s\S]+)DOC', comment)[0].split("\n")
        data["publisher"] = info_comment[3].split(":")[1].strip()
        data["price"] = info_comment[0].split()[-1]
        data["call_no"] = info_comment[4].split(":")[1].strip()

        info_table = root.xpath('//*[@id="td"]/tr')
        for tr in info_table:
            name = tr.xpath('.//td[1]/text()')[0].strip()
            if name == "题名与责任":
                name_temp = tr.xpath('.//td[2]/a/text()')[0].replace("\xa0", "")
                try:
                    data["author"] = name_temp.split("/")[1]
                except:
                    data["author"] = None
                data["title"] = "《{}》".format(re.findall("(.+?)\[", name_temp)[0])
            elif name == "著者":
                author_alt = tr.xpath('.//td[2]/a/text()')[0].split("\xa0")[0]
            elif name == "主题":
                data["subject"] = tr.xpath('.//td[2]/a/text()')[0].replace("\xa0", "")
            elif name == "内容提要":
                data["summary"] = tr.xpath('.//td[2]/text()')[0].strip()
                if data["summary"]:
                    data["summary"] = re.sub(r"[\\n\s\n\t\r]+", "", data["summary"])
            elif name == "载体形态项":
                data["page_number"] = tr.xpath('.//td[2]/text()')[0].strip().replace("\xa0", "")
            elif name == "出版项":
                data["publish_date"] = re.findall(',(.+)', tr.xpath('.//td/a/text()')[0].replace("\xa0", ""))[0].strip(")")
        if not data["author"]:
            data["author"] = author_alt
    
    except:
        print ("国家图书馆数据库1中无该书目！")
        return False, data

    return True, data

def getinfo_guotu2(isbn, data, timeout=10):
    """
    国家图书馆数据库2，书目不全，但信息准确
    没有价格信息
    """
    print ("从国家图书馆数据库2中获得数据...")
    data["isbn"] = isbn

    # 尝试获得key
    url_main = "http://ucs.nlc.cn/F/"
    status, msg = connect_url(url_main, timeout=timeout)
    if status:
        root_key = msg
        try:
            key = re.findall(r"ucs.nlc.cn:80\/F\/(.+)\-", root_key.xpath('//head/meta[@http-equiv="REFRESH"]/@content')[0])[0]
        except:
            print ("网络连接故障！")
            return False, data            
    else:
        print ("网络连接故障！")
        return False, data
    
    # 搜索url
    url = "http://ucs.nlc.cn/F/" + key + "?func=find-b&find_code=ISB&request=" + isbn + "&local_base=UCS01"
    
    # 尝试连接搜索url
    status, msg = connect_url(url, timeout=timeout)
    if status:
        root_main = msg
    else:
        print ("网络连接故障！")
        return False, data
    
    # 如果返回的是一个图书列表，获得列表中第一本书的url
    if str(root_main.xpath('/comment()')[0]) == "<!-- filename: short-2-head  -->":
        print ("查找到多本图书，正在选取列表中的第一本！")
        try:
            url = root_main.xpath('//*[@id="brief"]/table[1]/tr[1]/td[1]/table[1]/tr/td[3]/div/a/@href')[0]
        except:
            print ("国家图书馆数据库2中无该书目！")
            return False, data            
        status, msg = connect_url(url, timeout=timeout)
        if status:
            root = msg
        else:
            print ("网络连接故障！")
            return False, data        
    else:
        root = root_main
    
    # 解析图书信息
    try:
        for e in root.xpath('/html/head/comment()'):
            if str(e).find("publish section")>0:
                comment = str(e)
                break

        info_comment = re.findall(r'(ISBN[\w\W\d\W\s\S]+)DOC', comment)[0].split("\n")
        data["publisher"] = info_comment[3].split(":")[1].strip()
        data["call_no"] = info_comment[4].split(":")[1].strip()

        info_table = root.xpath('//*[@id="details2"]/table/tr')
        for tr in info_table:
            name = tr.xpath('.//td[1]/text()')[0].strip()
            if name == "题名与责任":
                name_temp = tr.xpath('.//td[2]/a/text()')[0].replace("\xa0", "")
                try:
                    data["author"] = name_temp.split("/")[1]
                except:
                    data["author"] = None
                data["title"] = "《{}》".format(re.findall("(.+?)\[", name_temp)[0])
            elif name == "著者":
                author_alt = tr.xpath('.//td[2]/a/text()')[0].split("\xa0")[0]
            elif name == "主题":
                data["subject"] = tr.xpath('.//td[2]/a/text()')[0].replace("\xa0", "")
            elif name == "内容提要":
                data["summary"] = tr.xpath('.//td[2]/text()')[0].strip()
                if data["summary"]:
                    data["summary"] = re.sub(r"[\\n\s\n\t\r]+", "", data["summary"])
            elif name == "载体形态项":
                data["page_number"] = tr.xpath('.//td[2]/text()')[0].strip().replace("\xa0", "")
            elif name == "出版项":
                data["publish_date"] = re.findall(',(.+)', tr.xpath('.//td/a/text()')[0].replace("\xa0", ""))[0]
            elif name == "电子馆藏:":
                break
        if not data["author"]:
            data["author"] = author_alt
    
    except:
        print ("国家图书馆数据库2中无该书目！")
        return False, data

    return True, data