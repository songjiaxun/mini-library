#-*- coding: utf8 -*-
import urllib
import urllib.request
import xml.etree.ElementTree as ET

def get_text(data, start, end):
    if end - start<1 or start<100 or end<100 or data.find("数据库里没有这条请求记录.")>0 or data.find("<!-- filename: short-2-head  -->")>0 or data[start:end] == " ":
        text = "NA"
    else:
        text = data[start:end]
    return text

def htmldecoding(text):
    text = text.replace("&nbsp;"," ")
    text = text.replace("&quot;",'"')
    return text

def getinfo_douban(isbn, number, position):
    #豆瓣API
    data = [int(isbn), "《NA》", "NA", "NA", "NA", "NA", "NA", "NA", int(number), "NA", "NA", "豆瓣但无信息", None, None, position]
    #[isbn, "《"+ title + "》", author, publisher, pubdate, pages, price, subject, number, callnumber, summary, "来源"]
    try:
        r = urllib.request.urlopen("http://api.douban.com/book/subject/isbn/" + isbn)
        f = open('book.xml','wb')
        f.write(r.read())
        f.close()
    except Exception:
        return data
    try:
        tree = ET.parse('book.xml')
        root = tree.getroot()
    except Exception:
        return data
    attributes = root.findall('{http://www.douban.com/xmlns/}attribute')
    for attribute in attributes:
        if attribute.attrib["name"] == "pages":
            data[5] = attribute.text
        if attribute.attrib["name"] == "author":
            data[2] = attribute.text
        if attribute.attrib["name"] == "price":
            data[6] = attribute.text
        if attribute.attrib["name"] == "publisher":
            data[3] = attribute.text
        if attribute.attrib["name"] == "pubdate":
            data[4] = attribute.text    
    try:
        data[1] = u"《" + root.find('./{http://www.w3.org/2005/Atom}title').text + u"》"
        data[11] = "豆瓣"
        data[10] = root.find('./{http://www.w3.org/2005/Atom}summary').text
    except Exception:
        return data
    return data

def getinfo_guotu1(isbn, number, position):
    #中国国家图书馆API-key
    apikey = urllib.request.urlopen("http://opac.nlc.cn/F/")
    url = str(apikey.read())
    apikey.close()
    key_start = url.find('<META HTTP-EQUIV="REFRESH" CONTENT="1200; URL=http://opac.nlc.cn:80/F/')+70
    key_end = key_start + 56
    key = url[key_start:key_end]
    #中国国家图书馆API
    website = urllib.request.urlopen("http://opac.nlc.cn/F/" + key + "?func=find-b&find_code=ISB&request=" + isbn)
    data = str(website.read(), encoding = "utf-8")
    website.close()
    #索书号
    callnumber_start = data.find('CALL-NO: ')+9
    callnumber_end = data[callnumber_start:].find('DOC-NUMBER')+callnumber_start-4
    callnumber = htmldecoding(get_text(data, callnumber_start, callnumber_end))
    #标题
    title_start1 = data.find("题名与责任")+62
    title_start2 = data[title_start1:].find(";'>")+title_start1+3
    title_end = data[title_start2:].find('[')+title_start2-6
    title = htmldecoding(get_text(data, title_start2, title_end))
    #内容简介
    summary_start = data.find("内容提要")+75
    summary_end = data[summary_start:].find('</td>')+summary_start-3
    summary = htmldecoding(get_text(data, summary_start, summary_end))
    #页数
    pages_start = data.find('载体形态项')+76
    pages_end = data[pages_start:].find('&nbsp')+pages_start
    pages = htmldecoding(get_text(data, pages_start, pages_end))
    #作者
    author_start1 = data.find("题名与责任")+62
    author_start2 = data[author_start1:].find("&nbsp;/&nbsp;")+author_start1+13
    author_end = data[author_start2:].find('</A>')+author_start2
    if data[author_start1:].find("&nbsp;/&nbsp;") == -1:
        author_start2 = data.find("AUTHOR: ")+8
        author_end = data[author_start2:].find(' IMPRINT')+author_start2-1
    author = htmldecoding(get_text(data, author_start2, author_end))
    #价格
    price_start1 = data.find('ISBN: ')+6
    price_start2 = data[price_start1:].find(' ')+price_start1+1
    price_end = data[price_start2:].find('TITLE:')+price_start2-3
    price = htmldecoding(get_text(data, price_start2, price_end))
    if price.find(" ")>0:
        price = price[price.find(" ")+1:]
    #出版社
    publisher_start1 = data.find('出版项')
    publisher_start2 = data[publisher_start1:].find("&nbsp;:&nbsp;")+13+publisher_start1
    publisher_end = data[publisher_start2:].find(',&nbsp;')+publisher_start2
    publisher = htmldecoding(get_text(data, publisher_start2, publisher_end))
    #出版日期
    pubdate_start1 = data.find('出版项')
    pubdate_start2 = data[pubdate_start1:].find(",&nbsp;")+7+pubdate_start1
    pubdate_end = data[pubdate_start2:].find('</A>')+pubdate_start2
    pubdate = htmldecoding(get_text(data, pubdate_start2, pubdate_end))
    if pubdate[-1] == ")":
       pubdate = pubdate[:-1]
    #主题
    subject_start1 = data.find("主题")
    subject_start2 = subject_start1 + data[subject_start1+6:].find("主题")
    subject_start3 = subject_start2 + data[subject_start2+16:].find("主题") 
    subject_start4 = data[subject_start3:].find(";'>") + subject_start3 + 3
    subject_end = data[subject_start4:].find("</A> ") + subject_start4
    subject = htmldecoding(get_text(data, subject_start4, subject_end))
    return [int(isbn), "《"+ title + "》", author, publisher, pubdate, pages, price, subject, int(number), callnumber, summary, "国家图书馆1", None, None, position]

def getinfo_guotu2(isbn, number, position):
    #中国国家图书馆API-key
    apikey = urllib.request.urlopen("http://ucs.nlc.cn/F/")
    url = str(apikey.read())
    apikey.close()
    key_start = url.find('<META HTTP-EQUIV="REFRESH" CONTENT="1200; URL=http://ucs.nlc.cn:80/F/')+69
    key_end = key_start + 57
    key = url[key_start:key_end]
    #中国国家图书馆API
    website = urllib.request.urlopen("http://ucs.nlc.cn/F/" + key + "func=find-b&find_code=ISB&request=" + isbn + "&local_base=UCS01")
    data = str(website.read(), encoding = "utf-8")
    website.close()
    #索书号
    callnumber_start = data.find('CALL-NO: ')+9
    callnumber_end = data[callnumber_start:].find('DOC-NUMBER')+callnumber_start-4
    callnumber = htmldecoding(get_text(data, callnumber_start, callnumber_end))
    #标题
    title_start1 = data.find("题名与责任")+62
    title_start2 = data[title_start1:].find(";'>")+title_start1+3
    title_end = data[title_start2:].find('[')+title_start2-6
    title = htmldecoding(get_text(data, title_start2, title_end))
    #内容简介
    summary_start = data.find("内容提要")+66
    summary_end = data[summary_start:].find('</td>')+summary_start-3
    summary = htmldecoding(get_text(data, summary_start, summary_end))
    #页数
    pages_start = data.find('载体形态项')+67
    pages_end = data[pages_start:].find('&nbsp')+pages_start
    pages = htmldecoding(get_text(data, pages_start, pages_end))
    #作者
    author_start1 = data.find("题名与责任")+62
    author_start2 = data[author_start1:].find("&nbsp;/&nbsp;")+author_start1+13
    author_end = data[author_start2:].find('</A>')+author_start2
    if data[author_start1:].find("&nbsp;/&nbsp;") == -1:
        author_start2 = data.find("AUTHOR: ")+8
        author_end = data[author_start2:].find(' IMPRINT')+author_start2-1
    author = htmldecoding(get_text(data, author_start2, author_end))
    #价格
    price_start1 = data.find('ISBN: ')+6
    price_start2 = data[price_start1:].find(' ')+price_start1+1
    price_end = data[price_start2:].find('TITLE:')+price_start2-3
    price = htmldecoding(get_text(data, price_start2, price_end))
    if price.find(" ")>0:
        price = price[price.find(" ")+1:]
    #出版社
    publisher_start1 = data.find('出版项')
    publisher_start2 = data[publisher_start1:].find("&nbsp;:&nbsp;")+13+publisher_start1
    publisher_end = data[publisher_start2:].find(',&nbsp;')+publisher_start2
    publisher = htmldecoding(get_text(data, publisher_start2, publisher_end))
    #出版日期
    pubdate_start1 = data.find('出版项')
    pubdate_start2 = data[pubdate_start1:].find(",&nbsp;")+7+pubdate_start1
    pubdate_end = data[pubdate_start2:].find('</A>')+pubdate_start2
    pubdate = htmldecoding(get_text(data, pubdate_start2, pubdate_end))
    if pubdate[-1] == ")":
       pubdate = pubdate[:-1]
    #主题
    subject_start1 = data.find("主题")
    subject_start2 = subject_start1 + data[subject_start1+6:].find("主题")
    subject_start3 = subject_start2 + data[subject_start2+16:].find("主题") 
    subject_start4 = data[subject_start3:].find(";'>") + subject_start3 + 3
    subject_end = data[subject_start4:].find("</A> ") + subject_start4
    subject = htmldecoding(get_text(data, subject_start4, subject_end))
    return [int(isbn), "《"+ title + "》", author, publisher, pubdate, pages, price, subject, int(number), callnumber, summary, "国家图书馆2", None, None, position]

def writer(isbn, number, position):
    if len(isbn)<5 or isbn[:1] == "91" or (not isbn.isdigit()):
        return ("【"+isbn+"为错误的ISBN码，请检查输入设备。】")
    else:
        try:
            bookinfo = getinfo_guotu1(isbn, number, position)
            while len(bookinfo[1]) > 200:
                bookinfo = getinfo_guotu1(isbn, number, position)
            if bookinfo[1] == "《NA》" and isbn[1] != "1":
                try:
                    bookinfo = getinfo_guotu2(isbn, number, position)
                except Exception as e:
                    print (e)
            if bookinfo[1] == "《NA》" and isbn[1] != "1":
                try:
                    bookinfo = getinfo_douban(isbn, number, position)
                except Exception as e:
                    print (e)
            if bookinfo[1] != "《NA》":
                print ("ISBN:", bookinfo[0])
                print ("书籍名称:", bookinfo[1])
                print ("作者:", bookinfo[2])
                print ("出版社:", bookinfo[3])
                print ("出版日期:", bookinfo[4])
                print ("页数:", bookinfo[5])
                print ("价格:", bookinfo[6])
                print ("主题:", bookinfo[7])
                print ("馆藏本数:", bookinfo[8])
                print ("索书号:", bookinfo[9])
                print ("书籍位置:", bookinfo[14])
                print ("内容简介:", bookinfo[10])
                print ("信息来源:", bookinfo[11])
                print ("============================")
            else:
                return ("【无法在网络数据库中查询到此书目。】\n【请退出软件后在“图书馆信息.xlsx”中手动添加书籍信息。】")
        except Exception as e:
            print (e)
            return ("【网络连接错误，或数据库故障，请检查网络连接后再试。】\n【如果多次尝试失败，请退出软件后在“图书馆信息.xlsx”中手动添加书籍信息。】")
    return bookinfo
