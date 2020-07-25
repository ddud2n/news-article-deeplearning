# -*- encoding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< RISS 검색시 리스트 크롤링하는 프로그램 > _select사용
- 크롤링 해오는 것 : 제목,날짜,내용요약본, link
- 리스트 -> 딕셔너리 -> df -> 엑셀로 저장 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
author_text = []
cert_text =[]
book_text=[]
number_text=[]
year_text = []
link_text = []
result = {}

# 엑셀로 저장하기 위한 변수
RESULT_PATH = 'C:/Users/sujin/PycharmProjects/Crawling/'  # 결과 저장할 경로
now = datetime.now()  # 파일이름 현 시간으로 저장하기

# StartCount=0 , 100 ,200
# icate=re_a_kor , re_a_over
# colName=re_a_kor , re_a_over
# pageScale=100
# query=코로나
# strSort=DATE, RANK

def crawler(page, query, icate, sort):

    startcount = 0
    maxpage = int(page)*100
    BASE_URL = 'http://www.riss.kr/search/Search.do?'
    QUERY_URL = 'isDetailSearch=N&searchGubun=true&viewYn=OP&onHanja=false&strSort=%s&iStartCount=%d&fsearchMethod=search&sflag=1&isFDetailSearch=N&icate=%s&colName=%s&pageScale=100&query=%s'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    while startcount < maxpage:

        url = BASE_URL + QUERY_URL%(sort, startcount, icate, icate, query)
        response = requests.get(url, headers = HEADERS)
        html = response.text

        # 뷰티풀소프의 인자값 지정
        soup = BeautifulSoup(html, 'html.parser')

        # 제목추출
        titlist = soup.select('li>div.cont> p.title')
        for tit in titlist:
            title_text.append(tit.text.strip())  # 제목

        # 링크추출
        linklists = soup.select('li>div.cont> p.title> a')
        for linklist in linklists:
            link_text.append('http://www.riss.kr'+linklist['href'])  # 링크주소


        # 저자, 발행기관, 년도, 학술지명, 권호사항 추출
        etc_lists = soup.select('li>div.cont>p.etc>span')
        for i in range(0,len(etc_lists),5):
            author_text.append(etc_lists[i].text) #저자
            cert_text.append(etc_lists[i+1].text)  # 발행기관
            year_text.append(etc_lists[i+2].text)  # 년도
            book_text.append(etc_lists[i + 3].text)  # 학술지명
            number_text.append(etc_lists[i + 4].text)  # 권호사항

        # 모든 리스트 딕셔너리형태로 저장
        result = {"title": title_text, "auathor":author_text, "cert":cert_text,  "year": year_text, "book": book_text, "number": number_text,"link": link_text}
        print(startcount)

        df = pd.DataFrame(result)  # df로 변환
        startcount += 100

    # 새로 만들 파일이름 지정
    outputFileName = 'RISS_ %s-%s-%s  %s시 %s분 %s초.csv' % (
    now.year, now.month, now.day, now.hour, now.minute, now.second)
    df.to_csv(RESULT_PATH + outputFileName, index=False, encoding='utf-8-sig')


def main():
    info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)

    page = input("최대 크롤링할 페이지 수 입력하시오: ")
    query = input("검색어 입력: ")
    icate = input("검색범위 ( 국내 : re_a_kor , 해외 : re_a_over) : ")
    sort = input("정렬방식 ( 최신순 : DATE, 정확도순 : RANK) : ")

    crawler(page, query, icate,sort)


main()
