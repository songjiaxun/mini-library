# 乡村图书馆管理系统开源开发指南

## 1. 软件目的
该软件希望满足乡村中小学图书室的日常管理需求，包括：书籍的录入和整理、书籍借阅管理功能、简单的统计功能。  
该软件希望能够尽量降低老师和同学们的使用难度，因此在数据管理方面使用最为直观的Excel文件直接存储文件；在日常管理方面使用小数字键盘配合扫码枪进行管理，让小学生能够快速熟练掌握。

## 2. 服务人群
- **老师**：前期整理图书馆信息，包括：电子化图书信息、添加读者信息、制定图书室规定等。
- **学生**：负责日后的日常管理，包括：为同学们借阅归还图书、图书上架整理等。

## 3. 合作开发平台：github，git

### git简易教程
> * http://rogerdudler.github.io/git-guide/index.zh.html
> * https://git-scm.com/book/zh/v2

### 合作开发示例

 - 开源开发者（不能直接push到该仓库）：

```terminal
    git init #安装git后初始化
    #进入https://github.com/jiaxunsongucb/mini-library，点击右上角的fork按钮，将仓库复制到自己的github账号下
    #进入到自己的账号下的mini-library，点击绿色的“Clone or download”按钮服制下载链接
    #回到本地：
    git clone https://github.com/<username>/mini-library.git #科隆仓库到本地
    git pull #更新本地仓库
    git add . #添加所有新文件到暂存区
    git commit -m "本次修改说明" #提交改动
    git push #向远端推送修改
    #回到github提交pull request
    #等待审核合并
```
 - 受信任的合作开发者（已成为Collaborators，可以直接push）：

```terminal
    git init #安装git后初始化
    git clone https://github.com/jiaxunsongucb/mini-library.git #科隆仓库到本地
    git checkout -b testing #新建名为testing的分支
    git pull #更新本地仓库
    git add . #添加所有新文件到暂存区
    git commit -m "本次修改说明" #提交改动
    git push --set-upstream origin testing #设置推送到远端的分支为testing
    git push upstream testing #向远端testing分支推送修改
    #回到github提交pull request
    #等待审核合并
```
## 4. 合作开发规范
- 代码文件用英文命名，采用小写加下划线方式，如library_system.py。
- 类class用驼峰命名方式，如CamelCase()。
- 函数function名用小写加下划线方式，如lower_case_with_underscores()。
- 变量名用小写加下划线方式，请尽量用英文命名而不是拼音。
- 请为所有新的类和函数添加注释，注释请用中文书写。
- 其它规范请参考http://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules/

## 5. 合作方式
**由于开源性质，该项目不设严密的组织结构以及时间线，请各位开发者依照自己的兴趣和需求进行开发。**
> 1. 自愿领取任务（详见“期待新增/优化的功能”)  
开发者通过邮件或微信方式向项目owner说明所领取的任务，owner在该说明文件中标明。
> 2. 自己设定deadline
> 3. 在自己的仓库中完成任务
> 4. 申请pull request
> 5. owner审核通过，进行合并

## 6. 软件架构
### 相关文件
- library_system.py （主程序）
- library_data_entry_excel.py （爬虫录入书籍）
- id_generater.py （生成借书号）
- meta_data.json （存储登录信息、密码等信息）
- 图书馆信息.xlsx （存储书籍信息）
- 读者信息.xlsx （存储读者信息）
- 图书馆信息.xlsx_backup.json （每一步操作后自动生成的备份文件）
- 读者信息.xlsx_backup.json （每一步操作后自动生成的备份文件）
- book.xml （爬虫生成的中间文件）

### class/function表
待续

## 7. 期待新增/优化的功能
- [x] 新增详细版说明书
- [ ] 新增图文版说明书
- [ ] 新增离线录入书籍
- [ ] 新增批量录入书籍
- [ ] 新增用户使用情况追踪
- [ ] 新增自动生成易打印的书籍信息和读者信息
- [ ] 解决python封装成exe文件后还需要用户自行安装编译环境的问题
- [ ] 解决python封装成exe文件后被杀毒软件误杀的问题
- [ ] 优化爬虫（使用xpath、scrapy、re，或者更成熟的API？）
- [ ] 优化数据存储方式（采用更成熟的数据库？）
- [ ] 优化数据备份方式（提高备份效率？）
- [ ] 优化书籍录入流程（从实际需求出发，帮助老师更快实现图书电子化）
- [ ] 图形化界面？（Python的GUI开发真的是痛！）
- [ ] 用其它语言和平台改写（目前沿用Python开发因为这个语言真的通俗易懂）
- [ ] 基于WEB的应用？

## 8. 软件下载地址（内附说明书）
**建议先下载软件进行实用，以此了解软件的逻辑和用户需求。**
> * 链接:https://pan.baidu.com/s/1c2isW5U
> * 密码:iuq3
