import requests
from bs4 import BeautifulSoup as bs 
import json

class ScrapeHelper():
    def __init__(self):
        self.proxies = {
            'http':'http://lum-customer-hl_26f509b3-zone-static:emgsedqdj28n@zproxy.lum-superproxy.io:22225', 
            'https':'http://lum-customer-hl_26f509b3-zone-static:emgsedqdj28n@zproxy.lum-superproxy.io:22225'
        }
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }

    def get_soup(self, url, proxy=True):
        if proxy:
            r = requests.get(url, proxies = self.proxies, healders = self.headers)
        else:
            r = requests.get(url)
        soup = bs(r.text, 'html.parser')
        return soup

    