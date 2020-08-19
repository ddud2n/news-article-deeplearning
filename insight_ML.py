from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re

from konlpy.tag import Mecab
from tensorflow.keras import utils
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< 인사이트ㅡ 뉴스 검색시 리스트 크롤링하는 프로그램 > 
- 크롤링 해오는 것 : 제목,날짜,내용요약본, link
- 리스트 -> 딕셔너리 -> df -> ML 돌리기
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
date_text = []
contents_text = []
link_text = []
result = {}

# 엑셀로 저장하기 위한 변수
#RESULT_PATH = 'C:/Users/sujin/PycharmProjects/Crawling/'  # 결과 저장할 경로
#now = datetime.now()  # 파일이름 현 시간으로 저장하기



# 내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<p class="psil_txt">', '',
                                      str(contents)).strip()  # 앞에 필요없는 부분 제거
    second_cleansing_contents = re.sub('</p>', '',
                                       first_cleansing_contents).strip()  # 뒤에 필요없는 부분 제거
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)


#page : 페이지 인덱스
#query : 검색어


def crawler(maxpage, query):

    page = 1
    BASE_URL = 'https://insight.co.kr/search/?'
    QUERY_URL = 'query=%s&page%d'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    while page <= int(maxpage):

        url = BASE_URL + QUERY_URL%(query, int(page))
        response = requests.get(url, headers = HEADERS)
        html = response.text

        # 뷰티풀소프의 인자값 지정
        soup = BeautifulSoup(html, 'html.parser')

        # 제목&링크추출
        titlist = soup.select('.search-list-article-title')
        for tit in titlist:
            title_text.append(tit.text.strip())  # 제목
            link_text.append(tit.get('href'))  # 링크


        # 기자&날짜 추출
        date_lists = soup.select('.search-list-article-byline')
        for date_list in date_lists:
            list_date = date_list.text.split('·')
            if len(list_date) == 2:
                list_date = [list_date[1]]
            date_text.append(list_date[0])  # 날짜

        # 본문요약본
        contents_lists = soup.select('.search-list-article-summary')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)  # 본문요약 정제화


        # 모든 리스트 딕셔너리형태로 저장
        result = {"date": date_text, "title": title_text,  "contents": contents_text, "link": link_text}

        print(page)

        df = pd.DataFrame(result)  # df로 변환
        page += 1

    return df
    # 새로 만들 파일이름 지정
    #outputFileName = '인사이트_ %s-%s-%s  %s시 %s분 %s초.csv' % (
    #now.year, now.month, now.day, now.hour, now.minute, now.second)
    #df.to_csv(RESULT_PATH + outputFileName, index=False, encoding='euc-kr')


def ML():
    model = load_model('./news_lstm_usev3.model')

    with open('./tokenizer_usev3.pickle', 'rb') as handle:
        tok = pickle.load(handle)

    tag_classes = ['NNG', 'NNP']
    category = {0:'세계', 1:'코로나', 2:'사회',
            3:'문화', 4:'정치', 5:'IT과학', 6:'경제'}
    m = Mecab()

    info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)
    maxpage = input("최대 크롤링할 페이지 수 입력하시오: ")
    query = input("검색어 입력: ")
    data = crawler(maxpage, query)

    result = ""
    '''
    value = m.parseToNode(str(data).strip())
    while value:
        tag = value.feature.split(',')[0]
        word = value.feature.split(',')[3]
        if tag in tag_classes and word != "*":
            result += word.strip() + " "
    '''
    print("------------------크롤링 끝---------------------")
    ind = int(len(data.index))
    while(ind):
        print(str(data.loc[ind-1]['title']))
        print(str(data.loc[ind-1]['date']))
        print(str(data.loc[ind-1]['contents']))
        print(str(data.loc[ind-1]['link']))
        value = m.pos((str(data.loc[ind-1]['title'])+str(data.loc[ind-1]['contents'])).strip())
        for i in value:
            if i[1] in tag_classes and i[0] != '*':
                result += i[0] + " "

        x = [result.split()]
        sequence_data = tok.texts_to_sequences(x)
        pad_sequence_data = sequence.pad_sequences(sequence_data)

        for idx, i in enumerate(model.predict(pad_sequence_data)[0]):
            print(category[idx], i * 100)

        ind = ind - 1
        print("--------------------------------------------")

ML()