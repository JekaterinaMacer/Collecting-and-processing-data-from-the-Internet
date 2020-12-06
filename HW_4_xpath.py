# 1. Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath.
# Структура данных должна содержать:
# название источника; наименование новости; ссылку на новость; дата публикации.
# 2. Сложить собранные данные в БД
from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}
main_link_yandex = 'https://yandex.ru/news/'
response = requests.get(main_link_yandex, headers=headers)
dom = html.fromstring(response.text)
news = dom.xpath("//a[contains(@href, 'index') and @class='news-card__link']")

news_yandex = []
for e in news:
    title = e.xpath(".//text()")
    link = e.xpath("./@href")
    time = e.xpath('..//span[@class="mg-card-source__time"]/text()')
    source_name = e.xpath('..//span[@class="mg-card-source__source"]//text()')
    yandex_news = {'source': main_link_yandex, 'link': link, 'source_name': source_name, 'title': title,
                    'time': time}
    news_yandex.append(yandex_news)

pprint(news_yandex)

client = MongoClient('127.0.0.1', 27017)
db = client['Yandex_Lenta_Mail_news']
news_from_yandex = db.news_from_yandex
news_from_yandex.insert_many(news_yandex)

main_link_mail = 'https://news.mail.ru/'
response = requests.get(main_link_mail, headers=headers)
dom = html.fromstring(response.text)
links = dom.xpath('//div[contains(@class, "daynews__item")]//@href|//a[@class="list__text"]//@href')

news_mail = []
for link in links:
    response = requests.get(link, headers=headers)
    dom = html.fromstring(response.text)
    title = dom.xpath("//h1[@class='hdr__inner']/text()")
    date = dom.xpath("//@datetime")
    source_name = dom.xpath("//span[@class='breadcrumbs__item']//span[@class='link__text']/text()")
    mail_news = {'source': main_link_mail, 'link': main_link_mail + link, 'source_name': source_name, 'title': title,
                    'date': date}
    news_mail.append(mail_news)

pprint(news_mail)

# client = MongoClient('127.0.0.1', 27017)
# db = client['Yandex_Lenta_Mail_news']
news_from_mail = db.news_from_mail
news_from_mail.insert_many(news_mail)

main_link_lenta = 'https://lenta.ru/'
response = requests.get(main_link_lenta, headers=headers)
dom = html.fromstring(response.text)
lentas = dom.xpath("//div[contains(@class,'span8')]//div[contains(@class,'span4')]/div[contains(@class,'item')]")

news_lenta = []
for element in lentas:
    title = str(element.xpath(".//a/text()")).replace('xa0', ' ').replace("['", "").replace("']", "")
    link = str(element.xpath("./a/@href")).replace("['", "").replace("']", "")
    # date = dom.xpath("//@datetime[1]")
    time = str(element.xpath('..//time[@class="g-time__title"]/text()')).replace("T", " time: ").replace("+03:00", " MSK")
    source_name = "https://lenta.ru"
    lenta_news = {'source': main_link_lenta, 'link': main_link_mail + link, 'source_name': source_name, 'title': title,
                    'date': date}
    news_lenta.append(lenta_news)

pprint(news_lenta)

# client = MongoClient('127.0.0.1', 27017)
# db = client['Yandex_Lenta_Mail_news']
news_from_lenta = db.news_from_lenta
news_from_lenta.insert_many(news_lenta)

