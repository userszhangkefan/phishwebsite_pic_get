import os
from urllib.parse import urlparse
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from tqdm import tqdm

# -*- coding: utf-8 -*-
# @Author : Kefan
# @Time : 2023/3/1 22:05
driver = webdriver.Chrome()
driver.implicitly_wait(3)


##获取phishingtank中的非法页面网址,参数为需求多少页面，返回result_list
def get_valid_url(pagenum_pre, pagenum_last):
    result_list = []
    # tqdm进度条展示比较好看
    pbar = tqdm(range(pagenum_pre, pagenum_last))
    for i in pbar:
        pbar.set_description("正在加载Phishtank非法在线页面url第 %d 页 " % i)
        driver.get('https://phishtank.org/phish_search.php?page=' + str(i) + "&active=y&valid=y&Search=Search")

        try:
            tbody = driver.find_element('tag name', 'tbody')
            trs = tbody.find_elements('tag name', 'tr')
            for tr in trs:
                if "VALID PHISH" in tr.text and "ONLINE" in tr.text:
                    for text in tr.text.split():
                        if "http" in text:
                            result_list.append(text)
        except:
            continue
    driver.quit()
    return result_list


##将result_list写入txt文件,result_list从get_valid_url获取,保存到txt_location
def write_url(result_list, txt_location):
    with open(txt_location, 'w') as f:
        # tqdm写入
        pbar = tqdm(result_list)
        for url in pbar:
            pbar.set_description("正在将url写入文本文档...")
            f.write(url + '\n')


##方法一和二的结合，将非法页面存入对应txt文件
def output_phishtotxt(pagenum_pre, pagenum_last, txt_location):
    ##获取目标url并且返回为一个集合列表
    phish_url_list = get_valid_url(pagenum_pre, pagenum_last)
    ##写入对应txt文件
    write_url(phish_url_list, txt_location)


# 对txt中的url数据进行清洗,输出为error_log
def clean(txt_location,titles_location=None,error_log_location=None):
    logs = []
    # 将txt文件转换为列表urls
    with open(txt_location, 'r') as f:
        lines = f.readlines()  # 读取文件中的所有行
        urls = [line.strip() for line in lines]  # 将每行去除换行符后添加到列表中

    driver = webdriver.Chrome()
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(10)
    str = ['https://replit.com/', 'https://replit.com']
    titles_notfound = ['404 Not Found', '隐私设置错误']
    titles_record = []
    # 假设urls是包含多个URL的列表
    pbar = tqdm(urls)
    for url in pbar:
        pbar.set_description("清理进度...")
        try:
            driver.get(url)
            time.sleep(3)
            com = driver.find_elements(By.XPATH, "//*[@href]")
            titles = driver.title
            # 记录
            titles_record.append(titles + " " + url)
            if titles in titles_notfound:
                logs.append(url + " error type: __ " + titles)
                urls.remove(url)
            else:
                for mes in com:
                    if mes.get_attribute('href') in str:
                        # 删掉该url
                        logs.append(url + " error type: __ " + mes.get_attribute('href'))
                        urls.remove(url)
                        break

        except Exception as e:
            logs.append(url + " error type can not open")
            urls.remove(url)

    # 关闭浏览器
    driver.quit()

    #清洗完重新写回txt文件
    write_url(urls, txt_location)
    #参数可选项，输出对于url错误日志和url对应标签和url
    if error_log_location!=None:
        write_url(logs, error_log_location)
    if titles_location!=None:
        write_url(titles_record, titles_location)

# 需要挂梯子，将txt_file里的url取出，依次打开截屏并且保存到savepng_folder文件夹下
def output_phishtopng(txt_location, savepng_folder):
    # 创建 Chrome 浏览器对象
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(10)

    with open(txt_location, 'r') as f:
        lines = f.readlines()  # 读取文件中的所有行
        urls = [line.strip() for line in lines]  # 将每行去除换行符后添加到列表中

    # 假设urls是包含多个URL的列表
    pbar = tqdm(urls)
    for url in pbar:
        # 解析URL，提取域名作为文件名
        pbar.set_description("当前正在保存png图片...进度条:")
        parsed_url = urlparse(url)
        file_name = parsed_url.netloc + '.png'
        try:
            # 打开网页
            driver.get(url)
            # 保存截图

            file_path = os.path.join(savepng_folder, file_name)
            time.sleep(3)
            driver.save_screenshot(file_path)
        except Exception as e:
            urls.remove(url)
            continue
    # 重新写入
    write_url(urls, txt_location)
    # 关闭浏览器
    driver.quit()


# 将phishtank网页pre到last页面的非法钓鱼网站进行保存到对应folder中
def start_getphishwebpng(pagenum_pre, pagenum_last, txt_location, savepng_folder):
    output_phishtotxt(pagenum_pre, pagenum_last, txt_location)
    output_phishtopng(txt_location, savepng_folder)
