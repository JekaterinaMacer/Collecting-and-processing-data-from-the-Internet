# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
import requests
from pprint import pprint
import re
from bs4 import BeautifulSoup as bs
import pandas as pd
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)

main_link = 'https://hh.ru/search/vacancy'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'}
vacancies = []
vacancy = 'Accountant'

page = 0
while True:
    params = {'L_is_autosearch':'false', 'area': '2', 'clusters':'true',
        'enable_snippets':'true', 'text': vacancy, 'page': page}
    response = requests.get(main_link, params=params, headers=headers)

    if response.status_code == 200:
        dom = bs(response.text, 'html.parser')
        vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})

        for vac in vacancy_list:
            vacancy_data = {}
            vacancy_name = vac.find('a').text
            vacancy_link = vac.find('a')['href']
            vacancy_salary = vac.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            regex_num = re.compile('\d+')
            s = regex_num.search(vacancy_link)
            vacancy_id = vacancy_link[s.start():s.end()]

            if not vacancy_salary:
                salary_min = None
                salary_max = None
                salary_currency = None
            else:
                vacancy_salary = vacancy_salary.getText().replace(u'\xa0', u'')
                vacancy_salary = re.split(r'\s|-', vacancy_salary)
                if vacancy_salary[0] == 'до':
                    salary_min = None
                    salary_max = float(vacancy_salary[1])
                    salary_currency = vacancy_salary[2]
                elif vacancy_salary[0] == 'от':
                    salary_max = None
                    salary_min = float(vacancy_salary[1])
                    salary_currency = vacancy_salary[2]
                else:
                    salary_max = float(vacancy_salary[1])
                    salary_min = float(vacancy_salary[0])
                    salary_currency = vacancy_salary[2]

            vacancy_data['_id'] = int(vacancy_id)
            vacancy_data['name'] = vacancy_name
            vacancy_data['vacancy_link'] = vacancy_link
            vacancy_data['salary_min'] = salary_min
            vacancy_data['salary_max'] = salary_max
            vacancy_data['currency'] = salary_currency
            vacancies.append(vacancy_data)

    if dom.find(text='дальше'):
        page += 1
    else:
        break

maxsalary = 155000
df = pd.DataFrame(vacancies)
db = client['hhru']
vacancies_hh = db.vacancies_hh

for vacancy in vacancies_hh.find({'$or': [{'salary_max': {'$gt': maxsalary}}, {'salary_min': {'$gt': maxsalary}}]}):
     pprint(vacancy)

n = 0
for v in vacancies:
    n = vacancies_hh.count_documents({'_id': v['_id']})
    if n == 0:
        vacancies_hh.insert_one({'_id': v['_id'], 'currency': v['currency'], 'name': v['name'], 'salary_max': v['salary_max'],
        'salary_min': v['salary_min'], 'vacancy_link': v['vacancy_link'], 'comment': 'new vacancy'})
        print('New vacancy is added')
    else:
        print('This vacancy is already existed')