from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import time

# MongoDB连接信息,请按实际情况配置
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "mydatabase"
COLLECTION_NAME = "mycollection"

# 连接到MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

#爬取当前页面数据
def f1(url: str):

    # 目标网站的URL
    URL = url

    # 发送请求
    response = requests.get(URL)

    # 解析内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取内容
    # 一，提取标题
    title = soup.find('span', class_='mw-page-title-main').get_text(strip=True)
    # 二，提取内容
    content = soup.find('div', class_='mw-body').get_text(strip=True)
    # 三，提取关联词
    keyword_list = soup.select('.mw-parser-output > p > a')
    # 关联词以数组形式储存，创建空的数组对象
    associated_word = []
    # 遍历写入关联词
    for a in keyword_list:
        keyword = a.string
        associated_word.append(keyword)

    # 将爬取数据存储在MongoDB中
    temp_date = {
        'name': title,
        'content': content,
        'associated_word': associated_word,
    }
    #向数据库写入数据
    collection.insert_one(temp_date)

#获取向下页面的链接
def f2(url:str,n:int):

    #此属性表示爬虫页面的第N个关键词（从0开始），初始值为1
    N = n
    # 目标网站的URL，初始值为https://www.yixue.com/%E8%A7%92%E8%B4%A8%E5%B1%82
    URL = url

    # 发送请求
    response = requests.get(URL)

    # 解析内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 三，提取关联词链接
    keyword_list = soup.select('.mw-parser-output > p > a')

    #初始化关键词链接href属性列表
    url_list = []

    #初始化关键词链接标签的title属性列表
    title_list = []

    #初始化空页面title属性值，用于后续判断向下爬取的页面链接是否为空
    error_info = '页面不存在'

    # 遍历当前页面关联词链接
    for a in keyword_list:

        #循环写入当前页面关键词href属性，拼接协议组成向下爬取的页面链接表
        url = 'https://www.yixue.com/' + str(a.get('href'))
        url_list.append(url)

        #循环写入当前页面关键词title属性
        title = str(a.get('title'))
        title_list.append(title)
    #判断向下爬虫关键词标签的title属性是否为空
    title_set = set(title_list[n])
    error_info_set = set(error_info)
    #如果下个爬虫页面为空，则关键词索引加1，来调取下个关键词链接，若下个关键词仍然为空，则反复自增直到进入else语句
    if len(title_set & error_info_set) > 0:
        N = N + 1
        URL = url_list[N]
        f2(URL, N)
    #重新设定爬取链接，开启新一轮爬虫
    else:URL = url_list[N]
    f1(URL)
    f2(URL,N)
    #休眠一秒，控制爬取速度
    time.sleep(1)
#调用方法
f2('https://www.yixue.com/%E8%A7%92%E8%B4%A8%E5%B1%82',1)

# 关闭数据库连接
client.close()