# 小型图书馆管理系统 Mini library management system

## 1. 软件简介
该软件希望满足小型图书馆，特别是乡村中小学图书室的日常管理需求，包括：书籍的录入和整理、书籍借阅管理功能、简单的统计功能。  
该软件希望能够尽量降低老师和同学们的使用难度，因此在数据管理方面使用最为直观的Excel文件直接存储文件；在日常管理方面使用小数字键盘配合扫码枪进行管理，让小学生能够快速熟练掌握。

## 2. 服务人群
- **老师**：前期整理图书馆信息，包括：电子化图书信息、添加读者信息、制定图书室规定等。
- **学生**：负责日后的日常管理，包括：为同学们借阅归还图书、图书上架整理等。

## 3. 合作开发平台：Github

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
## 4. Python规范
- 代码文件用英文命名，采用小写加下划线方式，如library_system.py。
- 类class用驼峰命名方式，如CamelCase()。
- 函数function名用小写加下划线方式，如lower_case_with_underscores()。
- 变量名用小写加下划线方式，请尽量用英文命名而不是拼音。
- 请为所有新的类和函数添加注释，注释请用中文书写。
- 其它规范请参考[Google Python Style Guide](http://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules/)

## 5. 环境配置说明
**由于软件面向的是windows平台用户，所以开发者必须使用windows平台对软件进行调试和打包。软件使用Python3编写，可执行文件exe为32位软件。**
> 1. 安装虚拟机环境  
> a. **Mac系统**  
> 安装VirtualBox，并安装windows 7 (SP1)操作系统(64位或32位皆可)。详情可参考该[教程](http://juanha.coding.me/2017/02/09/mac-win7-virtualbox/)。  
> b. **Windows系统**  
> 无论是哪一个windows版本，无需进行额外的虚拟机配置。
> 2. 安装[Python 3.4.4 (86x)](https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi)。使用该Python版本的原因是：1）这是最后一版支持Windows XP 的Python版本； 2）该版本对exe可执行文件的打包效果最好。此仓库所有代码均依赖于这一版本的Python环境，请务必安装此版本；3）使用32位是因为64位系统依然能够运行32位的软件，如此就无需发布两套独立的软件。请将Python安装至默认路径下（C:\Python34）。
> 3. 下载[Git](https://git-scm.com/download/win)并安装。
> 4. 使用Git Bash克隆此仓库： git clone https://github.com/jiaxunsongucb/mini-library.git
> 5. 下载[.NET Framework 4](https://www.microsoft.com/en-US/Download/confirmation.aspx?id=17718)并安装。（Windows 8.1及更新系统无需安装。）
> 6. 下载[Microsoft Windows SDK](https://www.microsoft.com/en-us/download/confirmation.aspx?id=8279)并安装。（**不要**勾选安装Visual C++ Compilers！）
> 7. 下载[Visual C++ 10 Compiler](https://download.microsoft.com/download/7/5/0/75040801-126C-4591-BCE4-4CD1FD1499AA/VC-Compiler-KB2519277.exe)并安装。
> 8. 下载[pywin32](https://github.com/mhammond/pywin32/releases/download/b221/pywin32-221.win32-py3.4.exe)并安装。这是为了安装[Python package Pyinstaller](https://superuser.com/questions/1300163/how-to-install-pyinstaller-in-python-3-4-3)用以打包exe可执行文件而准备的。
> 9. 进入[code](https://github.com/jiaxunsongucb/mini-library/tree/master/code)文件夹双击“安装package_for_windows_python34_86x.bat”为Python安装必要的package。（此过程需要联网。此安装过程会较慢。）（注：CMD脚本中使用for loop安装requirements而不是标准的pip install -r requirements.txt是因为pandas需要依赖numpy，必须按顺序依次安装。）
> 10. 至此，全部环境配置已经完毕。测试：双击library_system.py即可运行软件；双击“生成exe文件_python34_86x.bat”可将.py打包为exe可执行文件。

## 6. 软件架构
### 相关文件
**粗体为用户得到的文件**
- library_system.py （主程序）
- spider.py （爬虫录入书籍）
- data_manager.py （数据读取、交换）
- requirements.txt （用于安装python package）
- 安装package_for_windows_python34_86x.bat （用于安装python package）
- library_system.spec （用于打包exe可执行文件）
- 生成exe文件_python34_86x.bat （用于打包exe可执行文件）
- **library.db （存储登录信息、密码等信息，并用于数据备份）**
- **图书馆信息.xlsx （存储读者、书籍信息）**
- **借阅记录.xlsx （存储借阅记录）**
- **/备份恢复 （存储恢复的Excel文件）**
- **library.log （软件运行产生的日志文件）**
- **图书馆管理系统.exe （软件主体）**

### 软件流程图
待续

## 7. 软件更新日志
**2018-09**
- 回滚到架构调整之前（为了解决一个已知的global数据交换不同步的问题）
- 增加读者丢书功能（管理员目录中）
- 增加当前操作提示
- 修复数个BUG，提高稳定性

**2018-08**
- 调整软件架构，使其更易读，便于后期维护
- 优化爬虫（使用xpath和re）
- 解决python封装成exe文件后还需要用户自行安装编译环境的问题
- 优化数据存储方式（借鉴关系型数据库）
- 优化数据备份方式（使用SQLite3）
- 优化书籍录入流程（从实际需求出发，帮助老师更快实现图书电子化）
- 新增用户使用情况日志功能
- 重编说明书
- 自动调整cmd窗口大小
- 优化信息打印格式（使用pandas打印表格）
- 添加彩色输出，绿色提示用户成功，红色失败
- 隐藏密码输入，用户输入的密码不在屏幕上打印出来

**2017-10**
- 软件开源

**2016-10**
- 软件上线

## 8. 期待新增/优化的功能
- 离线批量录入书籍
- 自动生成易打印的书籍信息和读者信息
- 图形化界面/基于WEB的应用

## 9. 软件下载方式
> 1. 填写[线上登记表](https://www.wjx.top/jq/27060445.aspx)
> 2. 关注公众号“宋老师的图书馆”
> 3. 至[百度网盘](https://pan.baidu.com/s/1c2isW5U)下载，密码:iuq3 **（目前还是第一版软件）**

## 10. 鸣谢
陈胜寒：重整软件架构、测试与调试  
Jacty：重整软件架构  
杨小朝：重写部分爬虫  
吕汶颖、王德超、章强、张潮、段晨瑞、侯添译、胡恩硕、魏林：提供宝贵意见和建议
