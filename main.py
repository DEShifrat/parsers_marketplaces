import requests
from time import sleep
import random
from bs4 import BeautifulSoup
import pandas
from pandas import ExcelWriter
import openpyxl
import lxml
import urllib.parse


# url = f'https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search='
# search_data = [f'футболка','гирлянда','штаны','одежда','Смартфон','Косметика','Детские товары','обувь']
# search_random = random.choice(search_data)
# safe_string = urllib.parse.quote_plus(search_random)
# full_url=url+safe_string

# функция обращения к html странички с headers для обхода проблем с постоянным использованием ресурсов сайта
def get_html(full_url, params=None):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    # возврат html  кода страницы
    html = requests.get(full_url, headers=headers, params=params)
    return html


# функция получения количества страниц
def get_pages(html):
    soup = BeautifulSoup(html.text, 'lxml')
    #функция обработки исключений
    try:
        good_count = soup.find('h1').find_next('span').get_text(strip=True).replace("\xa0", '').split()[0]
        pages = int(good_count) // 100 + 1
    except:
        pages = 1
    return pages

# Функция сбора информации со страницы
def get_content(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('div', class_="product-card")
    global title
    title = soup.h1.text
    cards = []
    for item in items:
        # проверка на наличии скидки, если нет, то поле пустое
        try:
            discount = item.find('span', class_='product-card__sale active')
            if discount:
                discount = discount.get_text(strip=True).replace('%', '')
            else:
                discount = item.find('span', class_='product-card__sale').get_text(strip=True).replace('%', '')
        except:
            discount = 0
        # проверка цены
        try:
            price = item.find(class_='lower-price').get_text(strip=True).replace('\xa0', '').replace('₽', '')
        except:
            price = item.find('span', class_='price-commission__current-price').get_text(strip=True).replace('\xa0',
                                                                                                             '').replace(
                '₽', '')

        cards.append({
            'brand': item.find('strong', class_='brand-name').get_text(strip=True).replace('/', ''),
            'title': item.find('span', class_='goods-name').get_text(),
            'price': int(price),
            'discount': int(discount),
            'link': f'https://www.wildberries.ru{item.find("a", class_="product-card__main").get("href")}',
        })
    return cards

#Сохранение данных в Excel
def save_exel(data, file_name):
    dataframe = pandas.DataFrame(data)
    writer = ExcelWriter(f'{file_name}.xlsx')
    dataframe.to_excel(writer, 'data')
    writer.save()
    print(f'Данные сохранены в файл "{file_name}.xlsx"')



# сновная функция парсинга
def parser(full_url):
    print(f'Парсим данные с: "{full_url}"')
    html = get_html(full_url)
    #проверка доступности сервера
    if html.status_code == 200:
        pages = get_pages(html)
        print(f'Количество страниц: {pages}')
        cards = []
        pages = int(input('Введите количество страниц: '))
        for page in range(1, pages + 1):
            print(f'Парсинг страницы: {page}')
            html = get_html(full_url, params={'sort': 'popular', 'page': page})
            cards.extend(get_content(html))
        print(f'Всего: {len(cards)} позиций')
        save_exel(cards, title)
    else:
        print(f'Ответ сервера:{html.status_code}. Парсинг невозможен!')


if __name__ == "__main__":
    parser('https://www.wildberries.ru/catalog/obuv/zhenskaya/botinki-i-polubotinki?sort=popular&page=1&xsubject=2956&bid=4d673eae-e1ce-4b00-8010-81fb3cb94c721')