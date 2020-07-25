# -*- coding: utf-8, euc-kr -*-

from time import sleep
from bs4 import BeautifulSoup
from multiprocessing import Process
import os
import calendar
import requests
import re
import csv
import platform


class Writer(object):
    def __init__(self, category_name, date):
        self.user_operating_system = str(platform.system())

        self.category_name = category_name

        self.date = date
        self.save_start_year = self.date['start_year']
        self.save_end_year = self.date['end_year']
        self.save_start_month = None
        self.save_end_month = None
        self.initialize_month()

        self.file = None
        self.initialize_file()

        self.wcsv = csv.writer(self.file)

    def initialize_month(self):
        if len(str(self.date['start_month'])) == 1:
            self.save_start_month = "0" + str(self.date['start_month'])
        else:
            self.save_start_month = str(self.date['start_month'])
        if len(str(self.date['end_month'])) == 1:
            self.save_end_month = "0" + str(self.date['end_month'])
        else:
            self.save_end_month = str(self.date['end_month'])

    def initialize_file(self):
        if self.user_operating_system == "Windows":
            self.file = open('Article_' + self.category_name + '_' + str(self.save_start_year) + self.save_start_month
                             + '_' + str(self.save_end_year) + self.save_end_month + '.csv', 'w', encoding='euc-kr',
                             newline='')
        # Other OS uses utf-8
        else:
            self.file = open('Article_' + self.category_name + '_' + str(self.save_start_year) + self.save_start_month
                             + '_' + str(self.save_end_year) + self.save_end_month + '.csv', 'w', encoding='utf-8',
                             newline='')

    def get_writer_csv(self):
        return self.wcsv

    def close(self):
        self.file.close()



class OverFlow(Exception):
    def __init__(self, args):
        self.args = args
        self.message = " is overflow."

    def __str__(self):
        return str(str(self.args) + self.message)


class UnderFlow(Exception):
    def __init__(self, args):
        self.args = args
        self.message = " is underflow."

    def __str__(self):
        return str(str(self.args) + self.message)


class InvalidArgs(Exception):
    def __init__(self, args):
        self.args = args
        self.message = " is not Invalid Arguments"

    def __str__(self):
        return str(self.args + self.message)


class InvalidCategory(Exception):
    def __init__(self, category):
        self.category = category
        self.message = " is not valid."

    def __str__(self):
        return str(self.category + self.message)


class InvalidYear(Exception):
    def __init__(self, startyear, endyear):
        self.startyear = startyear
        self.endyear = endyear
        self.message = str(startyear) + "(startyear) is bigger than " + str(self.endyear) +"(endyear)"

    def __str__(self):
        return str(self.message)


class InvalidMonth(Exception):
    def __init__(self, month):
        self.month = month
        self.message = str(month) + " is an invalid month"

    def __str__(self):
        return str(self.message)


class OverbalanceMonth(Exception):
    def __init__(self, start_month, end_month):
        self.start_month = start_month
        self.end_month = end_month
        self.message = "start_month(" + str(self.start_month) + ") is an overbalance with end_month" + "(" + str(self.end_month) + ")"

    def __str__(self):
        return str(self.message)


class ResponseTimeout(Exception):
    def __init__(self):
        self.message = "Couldn't get the data"

    def __str__(self):
        return str(self.message)



class ArticleParser(object):
    special_symbol = re.compile('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$&▲▶◆◀■【】\\\=\(\'\"]')
    content_pattern = re.compile('본문 내용|TV플레이어| 동영상 뉴스|flash 오류를 우회하기 위한 함수 추가function  flash removeCallback|tt|앵커 멘트|xa0')

    @classmethod
    def clear_content(cls, text):
        # 기사 본문에서 필요없는 특수문자 및 본문 양식 등을 다 지움
        newline_symbol_removed_text = text.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        special_symbol_removed_content = re.sub(cls.special_symbol, ' ', newline_symbol_removed_text)
        end_phrase_removed_content = re.sub(cls.content_pattern, '', special_symbol_removed_content)
        blank_removed_content = re.sub(' +', ' ', end_phrase_removed_content).lstrip()  # 공백 에러 삭제
        reversed_content = ''.join(reversed(blank_removed_content))  # 기사 내용을 reverse 한다.
        content = ''
        for i in range(0, len(blank_removed_content)):
            # reverse 된 기사 내용중, ".다"로 끝나는 경우 기사 내용이 끝난 것이기 때문에 기사 내용이 끝난 후의 광고, 기자 등의 정보는 다 지움
            if reversed_content[i:i + 2] == '.다':
                content = ''.join(reversed(reversed_content[i:]))
                break
        return content

    @classmethod
    def clear_headline(cls, text):
        # 기사 제목에서 필요없는 특수문자들을 지움
        newline_symbol_removed_text = text.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        special_symbol_removed_headline = re.sub(cls.special_symbol, '', newline_symbol_removed_text)
        return special_symbol_removed_headline

    @classmethod
    def find_news_totalpage(cls, url):
        # 당일 기사 목록 전체를 알아냄
        try:
            totlapage_url = url
            request_content = requests.get(totlapage_url)
            document_content = BeautifulSoup(request_content.content, 'html.parser')
            headline_tag = document_content.find('div', {'class': 'paging'}).find('strong')
            regex = re.compile(r'<strong>(?P<num>\d+)')
            match = regex.findall(str(headline_tag))
            return int(match[0])
        except Exception:
            return 0






class ArticleCrawler(object):
    def __init__(self):
        self.categories = {'정치': 100, '경제': 101, '사회': 102, '생활문화': 103, '세계': 104, 'IT과학': 105, '오피니언': 110,
                           'politics': 100, 'economy': 101, 'society': 102, 'living_culture': 103, 'world': 104,
                           'IT_science': 105, 'opinion': 110}
        self.selected_categories = []
        self.date = {'start_year': 0, 'start_month': 0, 'end_year': 0, 'end_month': 0}
        self.user_operating_system = str(platform.system())

    def set_category(self, *args):
        for key in args:
            if self.categories.get(key) is None:
                raise InvalidCategory(key)
        self.selected_categories = args

    def set_date_range(self, start_year, start_month, end_year, end_month):
        args = [start_year, start_month, end_year, end_month]
        if start_year > end_year:
            raise InvalidYear(start_year, end_year)
        if start_month < 1 or start_month > 12:
            raise InvalidMonth(start_month)
        if end_month < 1 or end_month > 12:
            raise InvalidMonth(end_month)
        if start_year == end_year and start_month > end_month:
            raise OverbalanceMonth(start_month, end_month)
        for key, date in zip(self.date, args):
            self.date[key] = date
        print(self.date)

    @staticmethod
    def make_news_page_url(category_url, start_year, end_year, start_month, end_month):
        made_urls = []
        for year in range(start_year, end_year + 1):
            if start_year == end_year:
                year_startmonth = start_month
                year_endmonth = end_month
            else:
                if year == start_year:
                    year_startmonth = start_month
                    year_endmonth = 12
                elif year == end_year:
                    year_startmonth = 1
                    year_endmonth = end_month
                else:
                    year_startmonth = 1
                    year_endmonth = 12

            for month in range(year_startmonth, year_endmonth + 1):
                for month_day in range(1, calendar.monthrange(year, month)[1] + 1):
                    if len(str(month)) == 1:
                        month = "0" + str(month)
                    if len(str(month_day)) == 1:
                        month_day = "0" + str(month_day)

                    # 날짜별로 Page Url 생성
                    url = category_url + str(year) + str(month) + str(month_day)

                    # totalpage는 네이버 페이지 구조를 이용해서 page=10000으로 지정해 totalpage를 알아냄
                    # page=10000을 입력할 경우 페이지가 존재하지 않기 때문에 page=totalpage로 이동 됨 (Redirect)
                    totalpage = ArticleParser.find_news_totalpage(url + "&page=10000")
                    for page in range(1, totalpage + 1):
                        made_urls.append(url + "&page=" + str(page))
        return made_urls

    @staticmethod
    def get_url_data(url, max_tries=10):
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url)
            except requests.exceptions:
                sleep(60)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout()

    def crawling(self, category_name):
        # Multi Process PID
        print(category_name + " PID: " + str(os.getpid()))

        writer = Writer(category_name=category_name, date=self.date)

        # 기사 URL 형식
        url = "http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=" + str(
            self.categories.get(category_name)) + "&date="

        # start_year년 start_month월 ~ end_year의 end_month 날짜까지 기사를 수집합니다.
        day_urls = self.make_news_page_url(url, self.date['start_year'], self.date['end_year'],
                                           self.date['start_month'], self.date['end_month'])
        print(category_name + " Urls are generated")
        print("The crawler starts")

        for URL in day_urls:

            regex = re.compile("date=(\d+)")
            news_date = regex.findall(URL)[0]

            request = self.get_url_data(URL)

            document = BeautifulSoup(request.content, 'html.parser')

            # html - newsflash_body - type06_headline, type06
            # 각 페이지에 있는 기사들 가져오기
            post_temp = document.select('.newsflash_body .type06_headline li dl')
            post_temp.extend(document.select('.newsflash_body .type06 li dl'))

            # 각 페이지에 있는 기사들의 url 저장
            post = []
            for line in post_temp:
                post.append(line.a.get('href'))  # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
            del post_temp

            for content_url in post:  # 기사 URL
                # 크롤링 대기 시간
                sleep(0.01)

                # 기사 HTML 가져옴
                request_content = self.get_url_data(content_url)
                try:
                    document_content = BeautifulSoup(request_content.content, 'html.parser')
                except:
                    continue

                try:
                    # 기사 제목 가져옴
                    tag_headline = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                    text_headline = ''  # 뉴스 기사 제목 초기화
                    text_headline = text_headline + ArticleParser.clear_headline(
                        str(tag_headline[0].find_all(text=True)))
                    if not text_headline:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 본문 가져옴
                    tag_content = document_content.find_all('div', {'id': 'articleBodyContents'})
                    text_sentence = ''  # 뉴스 기사 본문 초기화
                    text_sentence = text_sentence + ArticleParser.clear_content(str(tag_content[0].find_all(text=True)))
                    if not text_sentence:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 언론사 가져옴
                    tag_company = document_content.find_all('meta', {'property': 'me2:category1'})
                    text_company = ''  # 언론사 초기화
                    text_company = text_company + str(tag_company[0].get('content'))
                    if not text_company:  # 공백일 경우 기사 제외 처리
                        continue

                    # CSV 작성
                    wcsv = writer.get_writer_csv()
                    wcsv.writerow([news_date, category_name, text_company, text_headline, text_sentence, content_url])

                    del text_company, text_sentence, text_headline
                    del tag_company
                    del tag_content, tag_headline
                    del request_content, document_content

                except Exception as ex:  # UnicodeEncodeError ..
                    # wcsv.writerow([ex, content_url])
                    del request_content, document_content
                    pass
        writer.close()

    def start(self):
        # MultiProcess 크롤링 시작
        for category_name in self.selected_categories:
            proc = Process(target=self.crawling, args=(category_name,))
            proc.start()


if __name__ == "__main__":
    Crawler = ArticleCrawler()
    Crawler.set_category("생활문화", "IT과학") # 정치, 경제, 생활문화, IT과학, 사회, 세계 카테고리 사용 가능
    Crawler.set_date_range(2020, 7, 2020, 7)
    Crawler.start()