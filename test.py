from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

# MongoDB连接信息,请按实际情况配置
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "mydatabase"
COLLECTION_NAME = "mycollection"

# 连接到MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# 目标网站的URL
URL = "https://www.yixue.com/%E8%A7%92%E8%B4%A8%E5%B1%82"

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

collection.insert_one(temp_date)

# 关闭数据库连接
client.close()