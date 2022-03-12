# -*- coding: utf-8 -*-
# @Time    : 2022/2/19 16:27
# @Author  : liangwenjie
import json
import os
import socket
import subprocess
import traceback
from selenium.webdriver.common.by import By
import time
import urllib
from telnetlib import EC
import pandas as pd
import pymysql
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#cmd chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenium_ui_auto\chrome_temp"
from selenium.webdriver.support import ui
from bs4 import BeautifulSoup as bf
import json
from selenium.webdriver.common.keys import Keys   #引用keys包
from selenium.webdriver.chrome.service import Service

# 判断端口是否被占用
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    s.connect(('127.0.0.1', 9222))
    s.shutdown(2)
    print('端口：9222正在使用')
except:
    print('端口：9222未被使用，准备打开Chrome窗口')
    subprocess.Popen('chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\selenium_ui_auto\chrome_temp"', shell=False)
# os.system('chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\selenium_ui_auto\chrome_temp"') # 放弃
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_driver = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
# driver = webdriver.Chrome(chrome_driver, options=chrome_options)
# 尝试传参
service = Service(chrome_driver)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.lagou.com/')
driver.implicitly_wait(10)  #隐式等待：浏览器加载页面需要时间10s，智能化等待，渲染时间
# driver.maximize_window()    #最大化浏览器


'''
配置连接MySQL参数
'''
def getConn():
    # 打开数据库连接
    conn = pymysql.connect(host="localhost", user="root", passwd="root123", port=3307, db="lwj_bysj", charset='utf8')
    conn.autocommit(True)#设置自动连接
    return conn

'''
#操作完成关闭数据库
'''
def close(conn):
    if conn:
        conn.close()

'''
判断是否登录
'''
def login_lg(classify,classfy_index):
    try:
        #判断是否登录错误，若是就执行登录
        islogin=driver.find_element(By.CSS_SELECTOR,'#lg_tbar > div.inner > div.lg_tbar_r > ul > li:nth-child(1) > a').text
        print('请'+islogin)
        print('系统休息100s,手动登录')
        time.sleep(100) #等待100秒手动执行登录
        '''
        确认已经登录：开始爬取数据
        '''
        try:
            user = driver.find_element(By.CSS_SELECTOR,
                '#lg_tbar > div.inner > div.lg_tbar_r > ul > li.user_dropdown > span').text
            print('已经登录，当前用户:' + user)
            '''
            确认已经登录：开始爬取数据
            '''
            print('点击h3:JAVA，再点击首页')
            # 点击首页的Java(默认为首页)
            click=driver.find_element(By.CSS_SELECTOR,
                '#sidebar > div > div:nth-child(1) > div.menu_main.job_hopping > div > a:nth-child(2) > h3')
            driver.execute_script("arguments[0].click();", click)
            crawl_data(classify,classfy_index)  # 开始从第classfy_index个分类开始
            driver.minimize_window()  # 自动最小化浏览器
        except Exception as e:
            print('登录报错，继续登录:'+repr(e))
            # traceback.print_exc()
            login_lg(classify,classfy_index)
    except Exception as e:
        print('无法登录:' + repr(e))
        # print('无法登录')
        # traceback.print_exc()

'''
爬取数据
'''
def crawl_data(classify,index):
    try:
        print('当前keyword为：'+str(classify[index]))
        while len(classify) > index:
            try:
                # 寻找按钮多节点
                wait = ui.WebDriverWait(driver, 20)
                # driver.refresh()
                driver.implicitly_wait(5)  # 隐式等待：浏览器加载页面需要时间3s，智能化等待，渲染时间
                print('准备点击首页')
                # 再次点击首页
                wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR,'#lg_tbar > div.lg_tbar_l > ul > li:nth-child(2) > a'))
                try:
                    click=driver.find_element(By.CSS_SELECTOR,'#lg_tbar > div.lg_tbar_l > ul > li:nth-child(2) > a') # 点击首页
                    driver.execute_script("arguments[0].click();",click)
                except:
                    print('再次尝试XPATH点击')
                    try:
                        sy=driver.find_element(By.XPATH,
                                        '//*[@id="lg_tbar"]/div[1]/ul/li[1]/a')  # 点击首页
                        driver.execute_script("arguments[0].click();", sy)
                    except:
                        print('再再次尝试模糊点击')
                        element=driver.find_element(By.CSS_SELECTOR,
                                            'li:nth-child(2)')  # 点击首页
                        driver.execute_script("arguments[0].click();", element)
                driver.implicitly_wait(5)  # 隐式等待：浏览器加载页面需要时间3s，智能化等待，渲染时间
                try:
                    time.sleep(3)
                    try:
                        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR,
                                                                      '#search_input'))
                        print('正在点击搜索框')
                        keyword = driver.find_element(By.CSS_SELECTOR,'#search_input')  # 搜索框
                        driver.execute_script("arguments[0].click();", keyword) #点击搜索框
                    except:
                        print('再次XPATH正在点击搜索框')
                        try:
                            keyword = driver.find_element(By.XPATH, '//*[@id="search_input"]')  # 搜索框
                            driver.execute_script("arguments[0].click();", keyword)  # 点击搜索框
                        except:
                            keyword = driver.find_element(By.CLASS_NAME, 'search_input')  # 搜索框
                            driver.execute_script("arguments[0].click();", keyword)  # 点击搜索框
                    keyword.clear()
                    keyword.send_keys(str(classify[index]))  # 输入关键词
                    # driver.execute_script("arguments[0].send_keys({str(classify[index])});", keyword)
                    print('现在搜索'+str(classify[index]))

                    wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR,
                        '#search_input'))
                    # 输入完成后，敲击键盘上的回车键
                    time.sleep(2)
                    print('发送enter指令')
                    driver.find_element(By.CSS_SELECTOR,'#search_input').send_keys(Keys.ENTER)
                except Exception as e:
                    print('点击搜索框失败:' + repr(e))
                    # traceback.print_exc()
                    '''
                    如果找不到这个input key，先尝试一下再次输入，不行再重新开始
                    '''
                    try:
                        time.sleep(5)
                        print('正在尝试再次点击搜索框')
                        keyword = driver.find_element(By.CSS_SELECTOR,'#search_input')  # 搜索框
                        driver.execute_script("arguments[0].click();", keyword)  # 点击搜索框

                        keyword.clear()
                        keyword.send_keys(str(classify[index]))  # 输入关键词
                        time.sleep(2)
                        print('发送enter指令')
                        driver.find_element(By.CSS_SELECTOR,'#search_input').send_keys(Keys.ENTER)
                    except Exception as e:
                        try:
                            print('尝试直接在顶部输入keyword搜索')
                            try:
                                find=driver.find_element(By.CSS_SELECTOR,'# keyword')
                                print('点击')
                                find.click()
                                find.clear()
                                find.send_keys(str(classify[index]))
                                print('发送enter指令')
                                find.send_keys(Keys.ENTER)
                            except:
                                print('尝试Xpth搜索')
                                find = driver.find_element(By.XPATH, '//*[@id="keyword"]')
                                print('点击')
                                find.click()
                                find.clear()
                                find.send_keys(str(classify[index]))
                                print('发送enter指令')
                                find.send_keys(Keys.ENTER)
                        except:
                            print(str(e))
                            print('输入keyword搜索发生错误，准备跳转重新搜索')
                            driver.refresh()
                            time.sleep(2)
                            print('点击首页')
                            #点击首页
                            wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR,
                                '# lg_tbar > div.inner > div.lg_tbar_l > ul > li.tab-active > a'))
                            sy=driver.find_element(By.CSS_SELECTOR,'# lg_tbar > div.inner > div.lg_tbar_l > ul > li.tab-active > a')
                            driver.execute_script("arguments[0].click();", sy)
                            print('点击h3:JAVA，再点击首页')
                            # 点击首页的Java(默认为首页)
                            wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR,
                                '#sidebar > div > div:nth-child(1) > div.menu_main.job_hopping > div > a:nth-child(2) > h3'))
                            click=driver.find_element(By.CSS_SELECTOR,
                                '#sidebar > div > div:nth-child(1) > div.menu_main.job_hopping > div > a:nth-child(2) > h3')
                            driver.execute_script("arguments[0].click();",click)
                            print('输入下一个分类进行搜索')
                            crawl_data(classify,index)  # 开始返回第classfy_index个分类重新开始
                driver.implicitly_wait(5)  # 隐式等待：浏览器加载页面需要时间5s，智能化等待，渲染时间
                while True:
                    driver.implicitly_wait(5)  # 隐式等待：浏览器加载页面需要时间5s，智能化等待，渲染时间
                    time.sleep(3)
                    print('正在传递page_source')
                    page_source = driver.page_source.encode('utf-8')
                    classif = str(classify[index])
                    analysis_data(page_source,classif)  # 传递html
                    # 寻找按钮多节点
                    wait = ui.WebDriverWait(driver, 10)
                    time.sleep(2)
                    try:
                        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR,
                            'li.lg-pagination-next'))
                        print('准备点击下一页')
                        element=driver.find_element(By.CSS_SELECTOR,'li.lg-pagination-next')  # 模糊匹配下一页标签,点击下一页
                        driver.execute_script("arguments[0].click();", element)
                        driver.implicitly_wait(10)  # 隐式等待：浏览器加载页面需要时间3s，智能化等待，渲染时间
                        # wait.until(lambda driver: driver.find_element_by_css_selector(
                        #     '#jobList > div.pagination__1L2PP > ul > li.lg-pagination-next > a'))
                        print('等待系统刷新')
                        time.sleep(5)
                        driver.refresh()
                        time.sleep(5)
                        try:
                            end = driver.find_element(By.CSS_SELECTOR,
                                'li.lg-pagination-next.lg-pagination-disabled').text
                            if (str(end) == '下一页'):
                                print('已经是最后一页了')
                                time.sleep(3)
                                print('正在传递最后一页page_source')
                                page_source=driver.page_source.encode('utf-8')
                                classif=str(classify[index])
                                analysis_data(page_source,classif)  # 传递最后一页html
                                index = index + 1
                                print('最后的打印位置:' + str(index))
                                break
                        except Exception as e:
                            print('等待进入下一页：' + repr(e))
                    except  Exception as e:
                        print('这是该分类已经是最后一页了：' + repr(e))
                        index = index + 1
                        print('最后的打印位置:' + str(index))
                        break
                time.sleep(400)
            except Exception as e:
                time.sleep(20)
                print('当前分类发生错误：'+classify[index],'报错:' + repr(e))
                print('跳过当前分类，搜索下一个分类：'+classify[index+1])
                cw = index+1
                driver.get('https://www.lagou.com/')
                print('点击h3:JAVA，再点击首页')
                # 点击首页的Java(默认为首页)
                ui.WebDriverWait(driver, 20).until(lambda driver: driver.find_element(By.CSS_SELECTOR,
                                                              '#sidebar > div > div:nth-child(1) > div.menu_main.job_hopping > div > a:nth-child(2) > h3'))
                click=driver.find_element(By.CSS_SELECTOR,
                                    '#sidebar > div > div:nth-child(1) > div.menu_main.job_hopping > div > a:nth-child(2) > h3')
                driver.execute_script("arguments[0].click();", click)
                crawl_data(classify,cw)
    except Exception as e:
        print('搜索结束'+repr(e))

def analysis_data(html,clasi):
    classify = clasi
    try:
        # 用BeautifulSoup解析html
        obj = bf(html,'html.parser')
        '''
        # 从标签script里提取标题<script id="__NEXT_DATA__" type="application/json">
        # all_jobs = obj.find_all('script')
        '''
        #转换成json格式
        json_format=str(obj.find('script', {'id': '__NEXT_DATA__'})).replace(r'<script id="__NEXT_DATA__" type="application/json">','').replace('</script>','')
        job_list=json.loads(json_format.strip())
        '''
        strip() 去除前后空格，包括换行,replace(old,new)字符串替换
        '''

        #根据json定位，获取返回的结果条数
        count=job_list.get("props").get("pageProps").get("initData").get("content").get("positionResult").get("resultSize")
        print(count)

        #返回职位结果
        all_jobs =job_list.get("props").get("pageProps").get("initData").get("content").get("positionResult").get("result")
        print(all_jobs)
        #json格式转换成DataFrame
        df = pd.DataFrame(all_jobs)
        print(df.to_string())
        save_mysql(count,df,classify)
    except Exception as e:
        print('BeautifulSoup解析失败:'+repr(e))
        try:
            print('尝试xpath解析')
            html=etree.HTML(html)
            # 1.岗位名称
            job_list = html.xpath(
                '//*[@id="jobList"]/div[1]/div/div/div[1]/div/a/text()[1]')  # .split(r'\n')[0].strip().replace(r'\n','').replace(r'[','')
            print(job_list)
            # 2.公司名称(不变)
            company_list = html.xpath('//*[@id="jobList"]/div/div/div/div[2]/div/a/text()[1]')
            # 3.城市
            city_list = html.xpath('//*[@id="jobList"]/div/div/div/div/div/a/text()[2]')
            # 4.发布时间（不变）
            time_list = html.xpath('//*[@id="jobList"]/div/div/div/div/div[1]/span/text()')
            # 5.工资水平（不变）
            salary_list = html.xpath('//*[@id="jobList"]/div/div/div/div/div[2]/span/text()')
            # 6.经验及学历
            educat_info_list = html.xpath('//*[@id="jobList"]/div/div/div[1]/div[1]/div/text()')
            # 7.方向、融资情况、规模
            all_scale_list = html.xpath('//*[@id="jobList"]/div/div/div/div[2]/div/text()')
            # 8.公司福利
            welfare_list = html.xpath('//*[@id="jobList"]/div/div/div[2]/div[2]/text()')
            # 9.职责技能分类
            skill_list = {}
            for jn in range(len(job_list)):
                jn = jn + 1
                xpath = '//*[@id="jobList"]/div/div[' + str(jn) + ']/div/div/span/text()'
                skill_info = html.xpath(xpath)
                skill_list[jn - 1] = skill_info
            count=len(job_list)
            result = []  # 定义空列表
            for i in range(len(company_list)):
                result.append(
                    ([job_list[i], company_list[i], city_list[i], time_list[i], salary_list[i], educat_info_list[i],
                      all_scale_list[i], welfare_list[i], skill_list[i]]))
                print(result)
            df = pd.DataFrame(result)
            # save_mysql(count,df)
            # 获取当前页面url并断言
            currentpageurl = driver.current_url
            print("当前页面的url是：", currentpageurl)
            # 保存数据
            cur = getConn().cursor()
            print('使用xpath保存mysql,正在插入表2:src_lgzp_current_day_data')
            for bc in range(count):
                positionname=df[0][bc]
                companyshortname=df[1][bc]
                city_area=df[2][bc]
                createtime=df[3][bc]
                salary=df[4][bc]
                exper_educat=df[5][bc]
                direct_finance_scale=df[6][bc]
                companylabellist=df[7][bc]
                positionlables=df[8][bc]
                insert_time=time.strftime("%Y-%m-%d")
                print(classify, positionname, companyshortname, city_area, createtime, salary, exper_educat,
                    direct_finance_scale, companylabellist, positionlables, insert_time, currentpageurl)
                inssql = "insert into src_lgzp_current_day_data(classify,position,company,city_area,pub_time,salary,exper_educat,direct_finance_scale,welfare,skill_classify,insert_time,lgzp_url) " \
                         "value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(inssql, (
                    classify, positionname, companyshortname, city_area, createtime, salary, exper_educat,
                    direct_finance_scale, companylabellist, positionlables, insert_time, currentpageurl))
                getConn().commit()
                print('插入成功')
                time.sleep(2)
        except Exception as e:
            print('xpath解析失败:'+repr(e))
            print(html)
    #获取保存条数，和数据列表

def get_gongsi():
    # driver.Navigation #navigate = driver.navigate();
    #点击公司元素
    print('准备点击公司首页')
    time.sleep(2)
    click = driver.find_element(By.CSS_SELECTOR,'#lg_tbar > div.inner > div.lg_tbar_l > ul > li:nth-child(4) > a')
    driver.execute_script("arguments[0].click();", click)
    time.sleep(3)
    print('点击按职位数量排序')
    try:
        click2 = driver.find_element(By.CSS_SELECTOR,'#order > li > div.item.order > a:nth-child(3)')
        driver.execute_script("arguments[0].click();", click2)
    except:
        click2 = driver.find_element(By.XPATH, '//*[@id="order"]/li/div[1]/a[2]')
        driver.execute_script("arguments[0].click();", click2)
    page=0
    result = []  # 定义空列表
    count=1
    while page<20:
        ispage = driver.find_element(By.CLASS_NAME,
                                     'pager_is_current').text
        print('ispage:' + str(ispage))
        for i in range(15):
            # 公司id
            list_company_id_element = f'#company_list > ul > li:nth-child({i + 1}) > div.top > h3 > a'
            list_company_id = driver.find_element(By.CSS_SELECTOR,
                                                  list_company_id_element).get_attribute('data-lg-tj-cid')
            # 公司名称
            short_name = driver.find_element(By.CSS_SELECTOR,
                                             list_company_id_element).text
            # 公司的# 方向、融资情况、规模
            direct_finance_scale_element = f'#company_list > ul > li:nth-child({i + 1}) > div.top > h4.indus-stage.wordCut'
            direct_finance_scale = driver.find_element(By.CSS_SELECTOR,
                                                       direct_finance_scale_element).text
            # 公司宣传语
            advantage_element = f'#company_list > ul > li:nth-child({i + 1}) > div.top > h4.advantage.wordCut'
            advantage = driver.find_element(By.CSS_SELECTOR,
                                            advantage_element).text

            # # 面试评价数量
            assess_element = f'#company_list > ul > li:nth-child({i + 1}) > div.bottom.clearfix > a.bottom-item.bottom-1.fl > p.green'
            assess = driver.find_element(By.CSS_SELECTOR,
                                         assess_element).text
            # # 在招职位数量
            position_num_element = f'#company_list > ul > li:nth-child({i + 1}) > div.bottom.clearfix > a.bottom-item.bottom-2.fl > p.green'
            position_num = driver.find_element(By.CSS_SELECTOR,
                                               position_num_element).text
            # # 简历处理率
            deal_cv_element = f'#company_list > ul > li:nth-child({i + 1}) > div.bottom.clearfix > a.bottom-item.bottom-3.fl > p.green'
            deal_cv = driver.find_element(By.CSS_SELECTOR,
                                          deal_cv_element).text
            # # 公司排名
            # pm_element = f'#company_list > ul > li:nth-child({i + 1}) > div.top > p > a'
            pm = (i+1)+(int(ispage)-1)*15
            # # 公司的url
            # 公司的url
            url_element = f'#company_list > ul > li:nth-child({i + 1}) > div.top > p > a'
            url = driver.find_element(By.CSS_SELECTOR,
                                      url_element).get_attribute('href')
            count=count+i  # 统计个数
            print(list_company_id, short_name, direct_finance_scale, advantage, assess,
                            position_num, deal_cv, pm, url)
            result.append(([list_company_id, short_name, direct_finance_scale, advantage, assess,
                            position_num, deal_cv, pm, url]))
        click3 = driver.find_element(By.CSS_SELECTOR, '#company_list > div > div > span.pager_next')
        driver.execute_script("arguments[0].click();", click3)
        print('点击下一页')
        time.sleep(5)
        page = page + 1
    df = pd.DataFrame(result)
    print(df.to_string())
    save_gongsi(count, df)
    print('返回搜索主页')
    click4= driver.find_element(By.CSS_SELECTOR, '#lg_tbar > div.inner > div.lg_tbar_l > ul > li:nth-child(1) > a')
    driver.execute_script("arguments[0].click();", click4)


# def explain_gongsi_date(page_source):
#     obj = bf(page_source, 'html.parser')
#     # 返回公司条数
#     count = len(obj.find_all('li', {'class': 'company-item'}))
#     print(count)
#     # print(obj.find_all('li', {'class': 'company-item'}))
#     result = []  # 定义空列表
#     for bc in range(count):
#         # 公司id
#         list_company_id = obj.find_all('li', {'class': 'company-item'})[bc].attrs['data-companyid']
#         # 公司名称
#         short_name = obj.find_all('li', {'class': 'company-item'})[bc].div.h3.a.attrs['title']
#         # 公司的# 方向、融资情况、规模
#         direct_finance_scale = obj.find_all('li', {'class': 'company-item'})[bc].div.h4.text
#         # 公司宣传语
#         advantage = obj.find_all('li', {'class': 'company-item'})[bc].div.find('h4',
#                                                                                {'class': 'advantage wordCut'}).text
#         # 面试评价数量
#         assess = obj.find_all('li', {'class': 'company-item'})[bc].find('div', {'class': 'bottom clearfix'}).find('p', {
#             'class': 'green'}).text
#         # 在招职位数量
#         position_num = \
#             obj.find_all('li', {'class': 'company-item'})[bc].find('div', {'class': 'bottom clearfix'}).find_all('p', {
#                 'class': 'green'})[1].text
#         # 简历处理率
#         deal_cv = \
#             obj.find_all('li', {'class': 'company-item'})[bc].find('div', {'class': 'bottom clearfix'}).find_all('p', {
#                 'class': 'green'})[2].text
#         # 公司排名
#         pm = json.loads(
#             obj.find_all('li', {'class': 'company-item'})[bc].div.p.a.attrs['data-lg-webtj-added_props']).get('seq')
#         # 公司的url
#         url = json.loads(
#             obj.find_all('li', {'class': 'company-item'})[bc].div.p.a.attrs['data-lg-webtj-added_props']).get('URL')
#
#         result.append(([list_company_id, short_name, direct_finance_scale, advantage, assess,
#                         position_num, deal_cv, pm, url]))
#     df = pd.DataFrame(result)
#     print(df.to_string())
#     print('准备保存公司信息')
#     save_gongsi(count, df)
'''
保存数据到数据库
'''
def save_gongsi(count,df):
    # 保存数据
    cur = getConn().cursor()
    try:
        for bc in range(count):
            # 职位id
            list_company_id = str(df[0][bc])
            short_name = str(df[1][bc])
            direct_finance_scale = str(df[2][bc])
            advantage = str(df[3][bc])
            assess = str(df[4][bc])
            position_num = str(df[5][bc])
            deal_cv = str(df[6][bc])
            pm = str(df[7][bc])
            url = str(df[8][bc])
            insert_time = time.strftime("%Y-%m-%d")
            print(list_company_id, short_name, direct_finance_scale, advantage, assess,
                    position_num, deal_cv, pm, url,insert_time)
            try:
                print('正在插入公司情况表:src_bysj_crawl_company_data')
                len = ' ' + 'value(%s' + ',%s' * 9 + ')'
                sql = 'insert into src_bysj_crawl_company_data(list_company_id,short_name, direct_finance_scale, advantage, assess,position_num, deal_cv, pm, url,insert_time) ' \
                      + len
                cur.execute(sql, (
                    list_company_id, short_name, direct_finance_scale, advantage, assess,
                    position_num, deal_cv, pm, url,insert_time))
                getConn().commit()
                print('插入成功')
                time.sleep(2)
            except Exception as e:
                try:
                    sql = 'update src_bysj_crawl_company_data set list_company_id=list_company_id,short_name=short_name,direct_finance_scale=direct_finance_scale,advantage=advantage,assess=assess,position_num=position_num,deal_cv=deal_cv,pm=pm,url=url,insert_time=insert_time where list_company_id=list_company_id and insert_time=insert_time'
                    time.sleep(2)
                    cur.execute(sql)
                    getConn().commit()
                    print('更新成功')
                except Exception as e:
                    print("插入失败:" + repr(e))
    except Exception as e:
        print('连接数据保存失败:' + repr(e))

def save_mysql(count,df,classify):
    # 获取当前页面url并断言
    currentpageurl = driver.current_url
    print("当前页面的url是：", currentpageurl)
    # 保存数据
    cur = getConn().cursor()
    try:
        for bc in range(count):
            # 职位id
            positionid = str(df['positionId'][bc])
            positionname = str(df['positionName'][bc])
            companyid = str(df['companyId'][bc])
            companyfullname = str(df['companyFullName'][bc])
            companyshortname = str(df['companyShortName'][bc])
            companysize = str(df['companySize'][bc])
            industryfield = str(df['industryField'][bc])
            financestage = str(df['financeStage'][bc])
            companylabellist = str(df['companyLabelList'][bc])
            firsttype = str(df['firstType'][bc])
            secondtype = str(df['secondType'][bc])
            thirdtype = str(df['thirdType'][bc])
            positionlables = str(df['positionLables'][bc])
            industrylables = str(df['industryLables'][bc])
            createtime = str(df['createTime'][bc])
            city = str(df['city'][bc])
            district = str(df['district'][bc])
            businesszones = str(df['businessZones'][bc])
            salary = str(df['salary'][bc])
            salarymonth = str(df['salaryMonth'][bc])
            workyear = str(df['workYear'][bc])
            jobnature = str(df['jobNature'][bc])
            education = str(df['education'][bc])
            positionadvantage = str(df['positionAdvantage'][bc])
            lastlogin = str(df['lastLogin'][bc])
            subwayline = str(df['subwayline'][bc])
            stationname = str(df['stationname'][bc])
            linestaion = str(df['linestaion'][bc])
            latitude = str(df['latitude'][bc])
            longitude = str(df['longitude'][bc])
            resumeprocessrate = str(df['resumeProcessRate'][bc])
            resumeprocessday = str(df['resumeProcessDay'][bc])
            score = str(df['score'][bc])
            isschooljob = str(df['isSchoolJob'][bc])
            positiondetail = str(df['positionDetail'][bc])
            positionaddress = str(df['positionAddress'][bc])
            insert_time = time.strftime("%Y-%m-%d")
            print(positionid, positionname, companyid, companyfullname, companyshortname, companysize, industryfield,
                    financestage, companylabellist, firsttype, secondtype, thirdtype, positionlables, industrylables,
                    createtime, city, district, businesszones, salary, salarymonth, workyear, jobnature, education,
                    positionadvantage, lastlogin, subwayline, stationname, linestaion, latitude, longitude,
                    resumeprocessrate, resumeprocessday, score, isschooljob, positiondetail, positionaddress,
                    insert_time)
            try:
                print('正在插入表1:src_bysj_crawl_lagou_data')
                len = ' ' + 'value(%s' + ',%s' * 36 + ')'
                sql = 'insert into src_bysj_crawl_lagou_data(positionid,positionname,companyid,companyfullname,companyshortname,companysize,industryfield,financestage,companylabellist,firsttype,secondtype,thirdtype,positionlables,industrylables,createtime,city,district,businesszones,salary,salarymonth,workyear,jobnature,education,positionadvantage,lastlogin,subwayline,stationname,linestaion,latitude,longitude,resumeprocessrate,resumeprocessday,score,isschooljob,positiondetail,positionaddress,insert_time) ' \
                      + len
                cur.execute(sql, (
                    positionid, positionname, companyid, companyfullname, companyshortname, companysize, industryfield,
                    financestage, companylabellist, firsttype, secondtype, thirdtype, positionlables, industrylables,
                    createtime, city, district, businesszones, salary, salarymonth, workyear, jobnature, education,
                    positionadvantage, lastlogin, subwayline, stationname, linestaion, latitude, longitude,
                    resumeprocessrate, resumeprocessday, score, isschooljob, positiondetail, positionaddress,
                    insert_time))
                getConn().commit()
                print('插入成功')
                time.sleep(2)
                print('正在插入表2:src_lgzp_current_day_data')
                inssql = "insert into src_lgzp_current_day_data(classify,position,company,city_area,pub_time,salary,exper_educat,direct_finance_scale,welfare,skill_classify,insert_time,lgzp_url) " \
                         "value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                city_area = '[' + city + '·' + district + ']'
                exper_educat = workyear + '/' + education
                # 移动互联网 / 未融资 / 15-50人
                direct_finance_scale = industryfield + '/' + financestage + '/' + companysize
                cur.execute(inssql, (
                classify, positionname, companyshortname, city_area, createtime, salary, exper_educat,
                direct_finance_scale, companylabellist, positionlables, insert_time, currentpageurl))
                getConn().commit()
                print('插入成功')
                time.sleep(2)
            except Exception as e:
                try:
                    sql = 'update src_bysj_crawl_lagou_data set positionid=positionid,positionname=positionname,companyid=companyid,companyfullname=companyfullname,companyshortname=companyshortname,companysize=companysize,industryfield=industryfield,financestage=financestage,companylabellist=companylabellist,firsttype=firsttype,secondtype=secondtype,thirdtype=thirdtype,positionlables=positionlables,industrylables=industrylables,createtime=createtime,city=city,district=district,businesszones=businesszones,salary=salary,salarymonth=salarymonth,workyear=workyear,jobnature=jobnature,education=education,positionadvantage=positionadvantage,lastlogin=lastlogin,subwayline=subwayline,stationname=stationname,linestaion=linestaion,latitude=latitude,longitude=longitude,resumeprocessrate=resumeprocessrate,resumeprocessday=resumeprocessday,score=score,isschooljob=isschooljob,positiondetail=positiondetail,positionaddress=positionaddress,insert_time=insert_time where positionid=positionid and companyid=companyid'
                    time.sleep(2)
                    cur.execute(sql)
                    getConn().commit()
                    print('更新成功')
                except Exception as e:
                    # traceback.print_exc()
                    print("插入失败:" + repr(e))
    except Exception as e:
        print('连接数据保存失败:'+repr(e))

'''
main（）主函数
'''
if __name__ == '__main__':
    classfy_index = int(input('请输入你要爬取分类的index：'))
    cur = getConn().cursor()
    sql = 'select * from src_bysj_position_classify_all'
    # 执行SQL语句
    cur.execute(sql)
    # 获取所有记录列表
    classify = []
    results = cur.fetchall()
    for row in results:
        classify.append(row[2])  # 将数据保存在列表中,keywords
    print('keywords:'+str(classify))
    try:
        user = driver.find_element(By.CSS_SELECTOR,
            '#lg_tbar > div.inner > div.lg_tbar_r > ul > li.user_dropdown > span').text
        print('当前用户:' + user)
        '''
        确认已经登录：开始爬取数据
        '''
        try:
            print('先爬取公司情况数据')
            get_gongsi()
        except Exception as e:
            print(e)
        print('正在点击h3:JAVA,再点击首页')
        # 点击首页的Java(默认为首页)
        try:
            dj=driver.find_element(By.CSS_SELECTOR,'#sidebar > div > div:nth-child(1) > div.menu_main.job_hopping > div > a:nth-child(2) > h3')
            driver.execute_script("arguments[0].click();", dj)
        except:
            dj=driver.find_element(By.XPATH,
                                '//*[@id="sidebar"]/div/div[1]/div[1]/div/a[1]/h3')
            driver.execute_script("arguments[0].click();", dj)
        print('点击完成')
        crawl_data(classify,classfy_index)  # 开始从第classfy_index个分类开始
        # driver.minimize_window()  # 自动最小化浏览器
    except Exception as e:
        # traceback.print_exc()
        print('判断为还没登录:'+repr(e))
        login_lg(classify,classfy_index)

