import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import csv


def write_cmc_top():
    url = 'https://coinmarketcap.com'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Получим линки ТОП-100 криптовалют с сайта https://coinmarketcap.com
        links = {}
        for link in soup.find_all('a', class_='cmc-link'):
            href = link.get('href')
            if href and href.startswith('/currencies/') and '#' not in href:
                links[url + href] = None

        # Обработаем (спарсим) уникальные линки с информацией о криптовалютах и получим:
        # Name - название криптовалюты, MC - market capitalization (рыночная капитализация)
        data = []
        total_market_cap = 0
        for unique_link in links.keys():
            response = requests.get(unique_link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                name_raw = soup.find('span', {'data-role': 'coin-name'}).text
                name = name_raw.replace(' price', '').replace('\xa0', '')
                market_cap_raw = soup.find('dd', class_='sc-f70bb44c-0 bCgkcs base-text').text
                market_cap = market_cap_raw.split('$')[-1].strip()
                market_cap_num = int(
                    float(
                        market_cap.replace(',', '').replace('B', 'e9').replace('M', 'e6')))  # Преобразуем в целое число
                total_market_cap += market_cap_num
                data.append({'Name': name, 'MC': market_cap_num})

        # Преобразуем data в датафрейм pandas и рассчитаем MP - Market percentage (процент рынка) по каждой крипте
        df = pd.DataFrame(data)
        df['MP'] = (df['MC'] / total_market_cap) * 100
        df['MP'] = df['MP'].round(0).astype(int).astype(str) + '%'
        df['MC'] = df['MC'].apply(lambda x: f'{x:,}')

        # Выведем получившийся датафрейм в консоль
        print(df)

        # Сохраним DataFrame в CSV, используя пробел в качестве разделителя
        file_name = f'{datetime.now().hour}.{datetime.now().minute} {datetime.now().strftime("%d.%m.%Y")}.csv'
        df.to_csv(file_name, sep=' ', index=False, quoting=csv.QUOTE_NONNUMERIC)
    else:
        print('Ошибка при получении данных с сайта CoinMarketCap')


if __name__ == '__main__':
    write_cmc_top()
