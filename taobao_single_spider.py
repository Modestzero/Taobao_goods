import datetime
import json
import os
import random
import re
from time import sleep
from urllib.parse import urljoin
import easygui as g

import pymysql
from jsonpath import jsonpath
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TaoBao:
    def __init__(self, user, password, word):
        options = webdriver.ChromeOptions()
        # 添加防止被检测到使用selenium
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 设置不加载图片
        options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        # chromeOptions.add_argument('-headless')  # 设为无头模式
        options.add_argument('disable-infobars')  # 去掉提示：Chrome正收到自动测试软件的控制

        # 创建浏览器
        self.chrome = webdriver.Chrome(options=options)

        self.user = user
        self.password = password
        self.word = word

    def login(self):
        login_url = 'https://login.taobao.com/member/login.jhtml'
        self.chrome.get(login_url)
        while True:
            sleep(t)
            self.chrome.find_element_by_id('fm-login-id').send_keys(self.user)
            sleep(t)
            self.chrome.find_element_by_id('fm-login-password').send_keys(self.password)
            sleep(t)

            try:
                slider = self.chrome.find_element_by_id("nc_1_n1z")
                if slider.is_displayed():
                    ActionChains(self.chrome).click_and_hold(on_element=slider).perform()
                    ActionChains(self.chrome).move_by_offset(xoffset=259, yoffset=0).perform()
                    ActionChains(self.chrome).pause(1).release().perform()
            except:
                pass
            sleep(t)
            # 自动回到个人主页
            try:
                if self.chrome.find_element_by_xpath('//div/div/span/b').is_displayed():
                    self.chrome.find_element_by_class_name('fm-btn').click()
                    sleep(t)
                    print('开始进入首页搜索。。。')
                    self.chrome.get('https://www.taobao.com')
                    sleep(t)
                    break
            except:
                self.chrome.refresh()
                sleep(t)

    def get_page(self):
        self.chrome.find_element_by_id('q').send_keys(self.word)
        sleep(t)
        self.chrome.find_element_by_class_name('search-button').click()
        sleep(t)
        # 拖动滚动条到底端
        js = 'document.documentElement.scrollTop=10000'
        self.chrome.execute_script(js)
        sleep(t)
        try:
            WebDriverWait(taobao1.chrome, 10).until(
                EC.presence_of_element_located(By.CLASS_NAME, "J_Ajax num icon-tag"))
        except:
            pass
        finally:
            page_source = self.chrome.page_source
            return page_source

    def parse_page(self, response):
        # 提取页面商品数据字符串
        content = re.findall(r'g_page_config = (.*"shopcardOff":true}});', response, re.DOTALL)[0]
        # 转换为json
        content_json = json.loads(content)
        # 提取数据
        prices = jsonpath(content_json, '$..view_price')
        shops = jsonpath(content_json, '$..nick')
        names = jsonpath(content_json, '$..raw_title')
        urls = jsonpath(content_json, '$..detail_url')

        print('正在保存数据。。。')
        for price, shop, good, url in zip(prices, shops, names, urls):
            infos = price, shop, good, url
            yield infos


    def save_info(self, infos, way):
        # 完整域名样式, 用于urljoin补全链接
        url_a = "https://detail.tmall.com/item.htm?spm=a2310563"
        price = infos[0]
        shop = infos[1]
        name = infos[2]
        url_o = infos[3]
        url = urljoin(url_a, url_o)

        if way == 'TXT':
            # 保存数据
            data = "{}\t\t{}\t\t{}\t\t{}\t\n".format(price, shop, name, url)
            f.write(data)

        elif way == 'MySQL':
            # 打开数据库连接
            db = pymysql.connect(host, database_user, database_password, data_base)
            # 使用 cursor() 方法创建一个游标对象 cursor
            cursor = db.cursor()
            # SQL 插入语句
            sql = "INSERT INTO %s(price, shop, name, url)VALUES ('%s','%s','%s','%s')" %(table_name, price, shop, name, url)
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except Exception as e:
                # 如果发生错误则回滚
                db.rollback()
                print('插入数据失败。。。因为： {}'.format(e))
            cursor.close()
            # 关闭数据库连接
            db.close()



if __name__ == '__main__':
    # 随机时间
    t = random.randrange(1, 3)
    g.msgbox("""-·- -·- -·- -·- 欢迎使用 Lucky定制 某宝商品搜索器 V 1.0 -·- -·- -·- -·- 
    
    
    
                本软件调用浏览器工作以确保用户信息安全，请放心使用。""")
    way = g.buttonbox("""请选择数据保存方式： 
    
    目前数据库方式只支持mysql/mariadb，后续再增加其他数据库和方式。""", choices=['TXT', 'MySQL'], default_choice='TXT')

    if way == None:
        os._exit(0)


    # TXT方式保存数据:
    elif way == 'TXT':
        msg = '请输入用户信息：'
        title = "666"
        field_name = ['商品名', '用户账号', '用户密码']
        person_info = g.multpasswordbox(msg, fields=field_name)
        while 1:
            if person_info == None:
                os._exit(0)
            errmsg = ""
            for i in range(len(field_name)):
                option = field_name[i].strip()
                if person_info[i].strip() == "" and option[0] == "*":
                    errmsg += ('【%s】为必填项。\n\n' % field_name[i])
            if errmsg == "":
                break
            person_info = g.multpasswordbox(errmsg, title, field_name, values=person_info)
        user = person_info[1]
        password = person_info[2]
        word = person_info[0]

        # 获取本地时间
        ISOTIMEFORMAT = '%Y-%m-%d-%H-%M'
        thetime = datetime.datetime.now().strftime(ISOTIMEFORMAT)
        # 获取当前目录
        file_path = os.getcwd() + word + thetime + '.txt'

        f = open(file_path, 'w+', encoding='utf-8')

        taobao1 = TaoBao(user, password, word)
        print('正在登陆.....')
        taobao1.login()
        print('正在打开首页.....')
        response = taobao1.get_page()
        print('正在解析.....')
        while True:
            information = taobao1.parse_page(response)

            for each in information:
                taobao1.save_info(each, way)
            sleep(t)

            try:

                # 方案一 ，模拟点击无法完成点击下一页，技术不够未找到原因
                # element = taobao1.chrome.find_element_by_css_selector('ul.items > li.item next > a').click()
                # # 执行js来点击
                # taobao1.chrome.execute_script("arguments[0].click();", element)

                # 方案二：移动鼠标点击, 可完成点击下一页， 需要添加个等待
                # 鼠标移动到 ac 位置
                # 等待加载结束再查找下一页位置
                # element = WebDriverWait.until(taobao1.chrome, 10).until(
                #     EC.presence_of_element_located(By.XPATH, "//ul/li[@class='item next']/a/span[1]")
                # )
                ac = taobao1.chrome.find_element_by_xpath("//ul/li[@class='item next']/a/span[1]")
                ActionChains(taobao1.chrome).move_to_element(ac).perform()
                # 在 ac 位置单击
                ActionChains(taobao1.chrome).move_to_element(ac).click(ac).perform()
                sleep(t)
                # 拖动滚动条到底端
                js = 'document.documentElement.scrollTop=10000'
                taobao1.chrome.execute_script(js)
                sleep(t * 2)
                print('正在解析下一页.....')
                response = taobao1.chrome.page_source

            except Exception as e:
                print('爬取结束。。。因为：{}，没有下一页了。或其他原因 '.format(e))
                f.close()
                taobao1.chrome.quit()
                break


    # 数据库MySQL方式保存数据:
    elif way == 'MySQL':
        msg = """     请输入用户信息: 
        
        请注意: 如果数据库或者表已存在, 则会清空里面的内容."""
        title = "666"
        fieldNames = ['*数据库IP', '*数据库用户名', '*数据库密码', '*数据库名', '*表名', '*商品名', '*用户名', '*用户密码']
        person_info = g.multpasswordbox(msg,title,fieldNames)
        while 1:
            if person_info == None:
                os._exit(0)
            errmsg = ""
            for i in range(len(fieldNames)):
                option = fieldNames[i].strip()
                if person_info[i].strip() == "" and option[0] == "*":
                    errmsg += ('【%s】为必填项。\n\n' % fieldNames[i])
            if errmsg == "":
                break
            person_info = g.multpasswordbox(errmsg, title, fieldNames, values=person_info)

        # 数据库地址
        host = person_info[0]
        # 数据库用户名
        database_user = person_info[1]
        # 数据库密码
        database_password = person_info[2]
        # 数据库名
        data_base = person_info[3]
        # 数据库的表名
        table_name = person_info[4]
        # 待搜索商品名
        word = person_info[5]
        # 某宝账号(手机号)
        user = person_info[6]
        # 某宝密码
        password = person_info[7]

        # 打开数据库连接
        db = pymysql.connect(host, database_user, database_password, data_base)
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        try:
            # 使用 execute() 方法执行 SQL，如果表存在则删除
            cursor.execute("DROP TABLE IF EXISTS %s " % table_name)

            # 使用预处理语句创建表
            sql = """CREATE TABLE %s (
                         price  INT(20),
                         shop  CHAR(255),
                         name  CHAR(255),
                         url  varchar (1024))""" % table_name
            cursor.execute(sql)
        except Exception as e:
            print('创建表失败。因为：{}'.format(e))


        taobao1 = TaoBao(user, password, word)
        print('正在登陆.....')
        taobao1.login()
        print('正在打开首页.....')
        response = taobao1.get_page()
        print('正在解析.....')

        while True:
            information = taobao1.parse_page(response)
            for each in information:
                taobao1.save_info(each, way)
            sleep(t)

            try:
                # 方案一 ，模拟点击无法完成点击下一页，技术不够未找到原因
                # element = taobao1.chrome.find_element_by_css_selector('ul.items > li.item next > a').click()
                # # 执行js来点击
                # taobao1.chrome.execute_script("arguments[0].click();", element)

                # 方案二：移动鼠标点击, 可完成点击下一页， 需要添加个等待
                # 鼠标移动到 ac 位置
                # 等待加载结束再查找下一页位置
                # element = WebDriverWait.until(taobao1.chrome, 10).until(
                #     EC.presence_of_element_located(By.XPATH, "//ul/li[@class='item next']/a/span[1]")
                # )
                ac = taobao1.chrome.find_element_by_xpath("//ul/li[@class='item next']/a/span[1]")
                ActionChains(taobao1.chrome).move_to_element(ac).perform()
                # 在 ac 位置单击
                ActionChains(taobao1.chrome).move_to_element(ac).click(ac).perform()
                sleep(t)
                # 拖动滚动条到底端
                js = 'document.documentElement.scrollTop=10000'
                taobao1.chrome.execute_script(js)
                sleep(t * 2)
                print('正在解析下一页.....')
                response = taobao1.chrome.page_source

            except Exception as e:
                print('爬取结束。。。因为：{}，没有下一页了。或其他原因. '.format(e))
                db.close()
                taobao1.chrome.quit()
                break


