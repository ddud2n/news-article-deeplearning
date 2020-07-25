#-*- coding: utf-8 -*-
import os
import sys
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime, timedelta
import pandas as pd

dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir, '../save'))



base_url = "http://news.naver.com/#"

def collecting(base_url):

    data = urlopen(base_url).read()
    soup = BeautifulSoup(data, "html.parser")
    total_data = soup.find_all(attrs={'class': 'main_component droppable'})

    colect_time = str(datetime.utcnow().replace(microsecond=0) + timedelta(hours=9))[:16]

    list1_category = []
    list1_title = []
    list1_article_body = []
    list1_time = []

    for each_data in total_data:

        category = ""

        try:
            category = str(each_data.find_all(attrs={'class': 'tit_sec'})).split('>')[2][:-3]
        except:
            pass

        data = str(each_data.find_all(attrs={'class': 'mlist2 no_bg'}))

        news_list = data.split('<li>')

        for each_news in news_list[1:]:

            news_block = each_news.split('href="')[1]
            # print(news_block)

            title = news_block.split('<strong>')[1].split('</strong>')[0]
            # print(title)
            news_url = news_block.split('"')[0].replace("amp;", "")
            # print(news_url)
            soup2 = BeautifulSoup(urlopen(news_url).read(), "html.parser")

            article_body = str(soup2.find(attrs={'id': 'articleBodyContents'}).text)

            list1_category.append(category)
            list1_title.append(title)
            list1_article_body.append(article_body)
            list1_time.append(colect_time)

    result = {"titile":list1_title, "category":list1_category, "time":list1_time, "content": list1_article_body }


    df = pd.DataFrame(result)
    now = datetime.now()
    path = 'C:/Users/sujin/PycharmProjects/Crawling/'
    outputFileName = 'Naver속보_ %s-%s-%s  %s시 %s분 %s초.csv' % (
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    df.to_csv(path + outputFileName, index=False, encoding='utf-8-sig')


collecting(base_url)
