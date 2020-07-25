# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_citations(content):
    out = 0
    for char in range(0, len(content)):
        if content[char:char + 9] == 'Cited by ':
            init = char + 9
            for end in range(init + 1, init + 6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)


def get_year(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[char - 5:char - 1]
    if not out.isdigit():
        out = 0
    return int(out)


def get_author(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[0:char - 1]
            break
    return out



keyword = "코로나"
number_of_results = 100
save_database = True
now = datetime.now()
outputFileName = 'Google_ %s-%s-%s  %s시 %s분 %s초.csv' % (
    now.year, now.month, now.day, now.hour, now.minute, now.second)
path = 'C:/Users/sujin/PycharmProjects/Crawling/'  # path to save the data

links = list()
title = list()
year = list()
rank = list()
author = list()
rank.append(0)

def crawler(keyword, number_of_results):
    for n in range(0, int(number_of_results), 10):
        url = 'https://scholar.google.com/scholar?start=' + str(n) + '&q=' + keyword.replace(' ', '+') + '&scisbd=1'
        page = requests.get(url)
        c = page.content

        soup = BeautifulSoup(c, 'html.parser')

        mydivs = soup.findAll("div", {"class": "gs_r gs_or gs_scl"})

        for div in mydivs:
            try:
                links.append(div.find('h3').find('a').get('href'))
            except:
                links.append('Look manually at: https://scholar.google.com/scholar?start=' + str(
                    n) + '&q=non+intrusive+load+monitoring')

            try:
                title.append(div.find('h3').find('a').text)
            except:
                title.append('Could not catch title')


            year.append(get_year(div.find('div', {'class': 'gs_a'}).text))
            author.append(get_author(div.find('div', {'class': 'gs_a'}).text))
            rank.append(rank[-1] + 1)

    data = pd.DataFrame(zip(author, title, year, links), index=rank[1:],
                    columns=['Author', 'Title',  'Year', 'Source'])
    data.to_csv(path + outputFileName, index=False, encoding='utf-8-sig')


def main():
    info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)
    number_of_results = input("최대 크롤링할 논문의 수 입력하시오: ")
    keyword = input("검색어 입력: ")
    crawler(keyword, number_of_results)


main()



