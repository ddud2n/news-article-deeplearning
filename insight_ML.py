from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from konlpy.tag import Mecab
import pickle
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import load_model
import json

title_text = []
date_text = []
contents_text = []
link_text = []


def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<p class="psil_txt">', '',
                                      str(contents)).strip()
    second_cleansing_contents = re.sub('</p>', '',
                                       first_cleansing_contents).strip()
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)


def crawler(maxpage, query):
    result = {}
    del title_text[:]o
    del date_text[:]
    del contents_text[:]
    del link_text[:]
    page = 1
    base_url = 'https://insight.co.kr/search/?'
    query_url = 'query=%s&page%d'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    while page <= int(maxpage):
        url = base_url + query_url%(query, int(page))
        response = requests.get(url, headers=headers)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        titlist = soup.select('.search-list-article-title')
        for tit in titlist:
            title_text.append(tit.text.strip())
            link_text.append(tit.get('href'))

        date_lists = soup.select('.search-list-article-byline')
        for date_list in date_lists:
            list_date = date_list.text.split('·')
            if len(list_date) == 2:
                list_date = [list_date[1]]
            date_text.append(list_date[0])

        contents_lists = soup.select('.search-list-article-summary')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)

        result = {"date": date_text, "title": title_text, "contents": contents_text, "link": link_text}
        df = pd.DataFrame(result)
        page += 1
    return df


def mL(temp, temp1):
    model = load_model('./news_lstm_usev3.model')
    with open('./tokenizer_usev3.pickle', 'rb') as handle:
        tok = pickle.load(handle)
    tag_classes = ['NNG', 'NNP']
    category = {0: '세계', 1: '코로나', 2: '사회', 3: '문화', 4: '정치', 5: 'IT과학', 6: '경제'}
    m = Mecab()
    data = crawler(temp, temp1)

    ind = len(data.index)
    json_list = {}
    while (ind):
        element = {}
        result_ml =""
        element['title'] = str(data.loc[len(data.index) - ind]['title'])
        element['date'] = str(data.loc[len(data.index) - ind]['date'])
        element['contents'] = str(data.loc[len(data.index) - ind]['contents'])
        element['link'] = str(data.loc[len(data.index) - ind]['link'])
        value = m.pos((str(data.loc[len(data.index) - ind]['title']) + str(data.loc[len(data.index) - ind]['contents'])).strip())
        for i in value:
            if i[1] in tag_classes and i[0] != '*':
                result_ml += i[0] + " "
        x = [result_ml.split()]
        sequence_data = tok.texts_to_sequences(x)
        pad_sequence_data = sequence.pad_sequences(sequence_data)
        element['probability'] = {}
        for idx, i in enumerate(model.predict(pad_sequence_data)[0]):
            element['probability'][category[idx]] = round((i * 100), 2)
        ind = ind - 1
        json_list[len(data.index) - ind] = element
    return json_list

from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def hello():
    return "this is main page"

@app.route("/get")
def user():
    temp = request.args.get('page', '1')
    temp1 = request.args.get('query', '코로나')
    return json.dumps(mL(temp, temp1), ensure_ascii=False)

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)
