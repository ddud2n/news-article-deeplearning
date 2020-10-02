import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
#ㄴㅇㅋㄹ럻ㄹㅎㅇㄹㅇ로허ㅏㅓㅣㅗㅓㅗㅊㅌㅋ
def main():

    sourcecode = urllib.request.urlopen("https://news.sbs.co.kr/news/newsflash.do?plink=GNB&cooper=SBSNEWS").read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    list_href = []
    list_content = []
    list_title =[]
    list_writer =[]
    list_date=[]

    for href in soup.find_all("a", class_="news"):
        list_href.append("https://news.sbs.co.kr" + href["href"])

    for tit in soup.find_all("strong", class_="sub"):
        list_title.append(tit.text)

    for name in soup.find_all("em", class_="name"):
        list_writer.append(name.text)

    for date in soup.find_all("span", class_="date"):
        list_date.append(date.text)

    for i in range(0, len(list_href)):
        url = list_href[i]
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")
        list_content.append(soup.find("div", class_="text_area").get_text())

    now = datetime.now()
    path = 'C:/Users/sujin/PycharmProjects/Crawling/'
    outputFileName = 'SBS최신_ %s-%s-%s  %s시 %s분 %s초.csv' % (
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    result = {"titile": list_title, "writer": list_writer,"date":list_date,"content": list_content, "link": list_href}
    df = pd.DataFrame(result)
    df.to_csv(path + outputFileName, index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    main()

