# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и
# сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time
from pprint import pprint

print('Начало\n')

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://mail.ru/')

mail = driver.find_element_by_id('mailbox:login-input')
mail.send_keys('study.ai_172')
domain = driver.find_element_by_id('mailbox:domain')
domain_select = Select(domain)
domain_select.select_by_visible_text('@mail.ru')

try:
    insert_pass = driver.find_element_by_id('mailbox:submit-button')
    insert_pass.click()
except exceptions.NoSuchElementException:
    print('Mail login not found')

password = driver.find_element_by_id('mailbox:password-input')
password.send_keys('NextPassword172')
password.send_keys(Keys.ENTER)

driver.get('https://e.mail.ru/inbox')
links = set() # исключаем дублирование
while True:
    links_len_1 = len(links)
    time.sleep(3)
    actions = ActionChains(driver)
    mails = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    for mail in mails:
        links.add(mail.get_attribute('href'))
    links_len_2 = len(links)
    if links_len_1 == links_len_2:
        break
    actions.move_to_element(mails[-1])
    actions.perform()
mail_info = [] # список для записи в БД
for link in links:
    mail = {}
    driver.get(link)
    subject = driver.find_element_by_class_name('thread__subject').text
    sender = driver.find_element_by_class_name('letter-contact').text
    depart_date = driver.find_element_by_class_name('letter__date').text
    try:
        text = driver.find_element_by_xpath("//div[@class='letter__body']").text
    except:
        text = '0'
    mail['subject'] = subject
    mail['sender'] = sender
    mail['departure_date'] = depart_date
    mail['text'] = text
    mail_info.append(mail)
pprint(mail_info)

client = MongoClient('127.0.0.1', 27017)
db = client['mail_ru_selenium']
letters_collection = db.letters_collection
letters_collection.insert_many(mail_info)

driver.quit()

print('\nКонец\n')