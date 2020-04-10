import json
import re
import time
import requests
from bs4 import BeautifulSoup

MAX_PRICE = 410

WEBSITE_TYPES = ('amazon', 'bestbuy', 'source')

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'scheme': 'https'}


def amazon_check(website):
    """

    :param website: Website Class
    :return: price(float)
    """
    url = website.url
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    price = re.search("\d+\.\d+", soup.find("span", {
        "class": "a-size-large a-color-price olpOfferPrice a-text-bold"}).get_text()).group(0)
    return float(price)


def source_check(website):
    """

    :param website:
    :return: price(float), instock(boolean)
    """
    url = website.url
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    stock = soup.find("div", {"class": "availability-text in-stock aline"})
    price = re.search("\d+\.\d+", soup.find("div", {"class": "pdp-sale-price common-price"}).get_text()).group(0)
    instock = True if stock is not None else False
    return float(price), instock


def bestbuy_check(website):
    """

    :param website:
    :return: price(float), instock(boolean)
    """
    url = website.url
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    stock = soup.find("svg", {"class": "green_2s2Rz icon_3u19d iconStyle_UHoBs icon_3qLg0"})
    search = soup.find("div", {"class": "price_FHDfG large_3aP7Z"}).get_text()
    price = re.search("\d+\.\d+", f'{search[:-2]}.{search[-2:]}').group(0)
    instock = True if stock is not None else False
    return float(price), instock


class Website:

    def __init__(self, url, webtype):
        assert webtype.lower() in WEBSITE_TYPES, "Invalid Website Type"
        self.url = url
        self.webtype = webtype.lower()
        self.price = None
        self.instock = False
        self.valid = False

    def __str__(self):
        return f'Site: {self.webtype} | In Stock: {self.instock} | Price: {self.price} | URL: {self.url}'

    def check(self):
        price = None
        tries = 0
        while price is None and tries <= 30:
            try:
                if self.webtype == 'amazon':
                    price = amazon_check(self)
                    self.instock = True

                elif self.webtype == 'source':
                    price, self.instock = source_check(self)

                elif self.webtype == 'bestbuy':
                    price, self.instock = bestbuy_check(self)

                self.price = price if price is not None else self.price

            except Exception as e:
                # print(f'Error: {e}... Retrying {30-tries} more times.')
                if tries % 5 == 0:
                    time.sleep(1)

                elif tries == 30:
                    print(f'Error: {e}...')

                else:
                    time.sleep(0.1)

                tries += 1

        if self.price is not None and self.instock:
            self.valid = True if self.price < MAX_PRICE else False

        return self.valid

    def save(self):
        with open('sites.json', 'r+') as fh:
            data = json.loads(fh.read())
            fh.seek(0)
            data[self.url] = self.webtype
            json.dump(data, fh, indent=2)
