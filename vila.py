import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
from requests.exceptions import RetryError


def collect_data(urls):
    ua = UserAgent()
    retry_strategy = Retry(
        total=10,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    category = 'MS'
    lang = 'EN'
    sku = 10000
    with open(f'{category}{lang}.csv', 'w', encoding='cp1251', errors='replace', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        spamwriter.writerow(["Category", "Title", "Description", "Text", "Photo", "Price", "SKU"])
        k = 1
        for url in urls:
            r = http.get(url, headers={'user-agent': ua.random})
            soup = BeautifulSoup(r.text, 'lxml')
            items = soup.find('ul', id='villas-listing').find_all('li')
            for item in items:
                url = 'https://fantasiavillas.com' + item.find('a').get('href')
                price = str(item.find('span', class_='short-desc'))
                if '€' in price or '$' in price:
                    price = price.split('strong>')[-1].split(' /')[0]
                    if '$' in price:
                        price = price.split('.')[-2].split()[-1].strip()
                    else:
                        price = price.replace('.', '').split()
                        price = price[-2].split(',')[0].strip()
                else:
                    price = ''
                try:
                    r = http.get(url, headers={'user-agent': ua.random})
                except RetryError:
                    continue
                soup = BeautifulSoup(r.text, 'lxml')
                try:
                    name = soup.find('h1', class_='single-page-title tk-lora fw-normal').text
                except AttributeError:
                    continue
                description = '\n'.join([i.text for i in soup.find('section', class_='content-tab clearfix tab-section'
                                                                                     ' visible-tab').find_all('p')])
                description = description.split('Registration number')[0]
                if description == '':
                    description = soup.find('section',
                                            class_='content-tab clearfix tab-section visible-tab').text.strip()
                images = soup.find_all('img')[1:]
                image_urls = []
                for image in images:
                    url = image.get('data-src')
                    if url[:2] != '//':
                        url = '//cdn.fantasiavillas.com' + url
                    url = 'https:' + url
                    image_urls.append(url)
                params = soup.find('ul', id='specifications').find_all('li')
                pos = f'{category}{k}'
                k += 1
                sku += 1
                spamwriter.writerow([f'{category}/{lang}', pos,
                                     params[1].text + '.' + 'Guests:'.join(params[2].text.split('Guests')),
                                     description.replace(name, pos), ';'.join(image_urls), price, sku])
                with open(f'{category}{lang}.txt', 'a', encoding='UTF-8') as file:
                    file.write(f'{name} - {pos}\n')


def main():
    collect_data(['https://fantasiavillas.com/destinations/greece-villa-rentals/mykonos-villa-rentals/',
                  'https://fantasiavillas.com/destinations/greece-villa-rentals/santorini-villa-rentals/'])


if __name__ == '__main__':
    main()
