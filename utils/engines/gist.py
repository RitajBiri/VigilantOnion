#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Andrey Glauzer'
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Andrey Glauzer"
__status__ = "Development"

import requests
import json
import re
import logging
import re
import urllib.parse
from random import choice
import time
from bs4 import BeautifulSoup


class GistAPI:
    def __init__(self):
        self.logger = logging.getLogger('Class:GistAPI')

        self.desktop_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0']

    @property
    def random_headers(self):
        return {
            'User-Agent': choice(self.desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    @property
    def start(self):
        self.cookies()
        self.pagination()
        self.scraping()
        return self.raw()

    def cookies(self):

        self.logger.info('Iniciando Scrap no Gist.')

        with requests.Session() as self.session:
            self.headers = self.random_headers

            request = self.session.get(
                'https://gist.github.com/search?l=Text&q=.onion', headers=self.headers)

            if request.status_code == 200:
                pass
            else:
                GistAPI.start

    def pagination(self):
        request = self.session.get(
            f"https://gist.github.com/search?l=Text&q={urllib.parse.quote('.onio')}", headers=self.headers)
        self.soup = BeautifulSoup(request.content, features="lxml")

        pages = []
        self.urls = ["https://gist.github.com/search?l=Text&q=.onion"]
        try:
            for pagination in self.soup.find('div', {'class': 'pagination'}).findAll('a'):
                pages.append(pagination.get_text())
        except:
            pages = False

        if pages:
            cont = 2
            while cont <= 1:  # int(pages[-2]):
                cont += 1
                full_url = f"https://gist.github.com/search?l=Text&p={cont-1}&q={urllib.parse.quote('.onio')}"
                self.urls.append(full_url)

    def scraping(self):
        url = []
        for inurl in self.urls:
            self.logger.debug(f"Conectando em {inurl}")
            time.sleep(5)
            request = self.session.get(inurl, headers=self.headers)

            if request.status_code == 200:
                soup = BeautifulSoup(request.content, features="lxml")
                for code in soup.findAll('div', {'class': 'gist-snippet'}):
                    if '.onion' in code.get_text().lower():
                        for raw in code.findAll('a', {'class': 'link-overlay'}):
                            try:
                                url.append(raw['href'])
                            except:
                                pass
            self.urls_raw = []
            for get in url:
                self.logger.debug(f"Conectando em {get}")
                time.sleep(5)
                try:
                    request = self.session.get(get, headers=self.headers)

                    if request.status_code == 200:
                        soup = BeautifulSoup(request.content, features="lxml")

                        for raw in soup.findAll('a', {'class': 'btn btn-sm'}):
                            try:
                                gist_url = f"https://gist.githubusercontent.com{raw['href']}"

                                self.urls_raw.append(gist_url)

                            except:
                                pass
                except(requests.exceptions.ConnectionError,
                       requests.exceptions.ChunkedEncodingError,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.InvalidURL) as e:
                    self.logger.error(
                        f"I was unable to connect to the url, because an error occurred.\n{e}")
                    pass

    def raw(self):
        self.logger.info('Performing replaces and regex. WAIT...')
        itens = []
        onionurl = []
        for raw in self.urls_raw:
            if '.txt' in raw.lower() \
                    or '.csv' in raw.lower():
                time.sleep(5)
                request = self.session.get(raw, headers=self.headers)
                self.soup = BeautifulSoup(request.content, features="lxml")
                for pre in self.soup.findAll('body'):
                    list = pre.get_text().split('\n')
                    itens.extend(list)

                regex = re.compile(
                    "[A-Za-z0-9]{0,12}\.?[A-Za-z0-9]{12,50}\.onion")

                for lines in itens:
                    rurls = lines \
                        .replace('\xad', '') \
                        .replace('\n', '') \
                        .replace("http://", '') \
                        .replace("https://", '') \
                        .replace("www.", "")

                    url = regex.match(rurls)

                    if url is not None:
                        onionurl.append(url.group())

        return onionurl
