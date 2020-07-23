from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< SBS 뉴스 검색시 리스트 크롤링하는 프로그램 > _select사용
- 크롤링 해오는 것 : 제목,날짜,내용요약본, link
- 리스트 -> 딕셔너리 -> df -> 엑셀로 저장 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
date_text = []
contents_text = []
link_text = []
result = {}

# 엑셀로 저장하기 위한 변수
RESULT_PATH = 'C:/Users/sujin/PycharmProjects/Crawling/'  # 결과 저장할 경로
now = datetime.now()  # 파일이름 현 시간으로 저장하기


# 날짜 정제화 함수
def date_cleansing(test):
    pattern = '\d+.(\d+).(\d+)'  # 정규표현식
    r = re.compile(pattern)
    match = r.search(test).group(0)  # 2018.11.05
    date_text.append(match)

# 내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<p class="psil_txt">', '',
                                      str(contents)).strip()  # 앞에 필요없는 부분 제거
    second_cleansing_contents = re.sub('</p>', '',
                                       first_cleansing_contents).strip()  # 뒤에 필요없는 부분 제거
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)


#pageID : 페이지 인덱스
#query : 검색어
#collection : nnews
#sort : 최신순- DATE, 인기순-POP, 인기도순-RANK
#searchOption : 전체검색-1, 일주일검색-2, 한달검색-3, 날짜검색-4
#searchSection : 검색범위 정치-1, 경제-2, 사회-3, 국제-7, 생활문화-8, 연예-14, 스포츠-9 -> 해당 데이터를 비우면 전체 검색


def crawler(maxpage, query, sort, s_date, e_date, section):

    page = 1
    BASE_URL = 'https://news.sbs.co.kr/news/search/main.do?'
    QUERY_URL = 'pageIdx=%d&searchTermStartDate=%s&searchTermEndDate=%s&query=%s&collection=%s&searchOption=%d&searchSection=%s&sort=%s'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    SEARCHSECTION = [str(section)]

    while page <= int(maxpage):

        url = BASE_URL + QUERY_URL%(page, s_date, e_date, query, 'nnews', 4, "|".join(SEARCHSECTION), sort)
        response = requests.get(url, headers = HEADERS)
        html = response.text

        # 뷰티풀소프의 인자값 지정
        soup = BeautifulSoup(html, 'html.parser')

        # 제목추출
        titlist = soup.select('.psil_tit')
        for tit in titlist:
            title_text.append(tit.text.strip())  # 제목

        # 링크추출
        atags = soup.select('.psil_link')
        for atg in atags:
            link_text.append(atg.get('href'))  # 제목

        # 날짜 추출
        date_lists = soup.select('.psil_info')
        for date_list in date_lists:
            test = date_list.text
            date_cleansing(test)  # 날짜 정제 함수사용

        # 본문요약본
        contents_lists = soup.select('.psil_txt')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)  # 본문요약 정제화


        # 모든 리스트 딕셔너리형태로 저장
        result = {"date": date_text, "title": title_text,  "contents": contents_text, "link": link_text}
        print(page)

        df = pd.DataFrame(result)  # df로 변환
        page += 1

    # 새로 만들 파일이름 지정
    outputFileName = 'SBS_ %s-%s-%s  %s시 %s분 %s초.csv' % (
    now.year, now.month, now.day, now.hour, now.minute, now.second)
    df.to_csv(RESULT_PATH + outputFileName, index=False, encoding='ms949')


def main():
    info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)

    maxpage = input("최대 크롤링할 페이지 수 입력하시오: ")
    query = input("검색어 입력: ")
    sort = input("뉴스 검색 방식 입력(최신순- DATE, 인기순-POP, 인기도순-RANK): ")
    s_date = input("시작날짜 입력(2020.01.01): ")
    e_date = input("끝날짜 입력(2020.01.01): ")
    section =input("검색범위 ( 검색범위 정치-01, 경제-02, 사회-03, 국제-07, 생활문화-08, 연예-14, 스포츠-09) : ")

    crawler(maxpage, query, sort, s_date, e_date, section)


main()
