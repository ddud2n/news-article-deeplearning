import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


def get_source(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[0:char - 2]
    return out


def main():

    list_href = []
    list_content = []
    list_title =[]
    list_source =[]
    list_date=[]

    url = "https://news.nate.com/recent?mid=n0100"
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    divs = soup.find_all("div", class_="mduSubjectList")

    for div in divs :
        link = div.find("a")["href"]
        list_href.append("http:" + link)
        tit = div.find("strong")
        list_title.append(tit.text)
        content = div.find("span", class_="tb")
        list_content.append(content.text)
        source = div.find("span", class_="medium")
        list_source.append(get_source(source.text))
        date = source.find("em")
        list_date.append(date.text)





    now = datetime.now()
    path = 'C:/Users/sujin/PycharmProjects/Crawling/'
    outputFileName = 'Nate최신_ %s-%s-%s  %s시 %s분 %s초.csv' % (
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    result = {"titile": list_title, "writer": list_source, "date": list_date, "content": list_content,
              "link": list_href}
    df = pd.DataFrame(result)
    df.to_csv(path + outputFileName, index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    main()

