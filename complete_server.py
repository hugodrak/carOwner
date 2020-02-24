#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

BASE_URL = "https://biluppgifter.se/"


def get_owner(reg_nr: str):
    r = requests.get(BASE_URL+"/fordon/"+reg_nr.upper())
    soup = BeautifulSoup(r.text, 'html.parser')
    if len(soup.find_all('a', {"class": "gtm-merinfo"})) > 0:
        owner_url = soup.find_all('a', {"class": "gtm-merinfo"})[0]['href']
        splitted = owner_url.split('/')
        ort = unquote(splitted[4])
        name_split = splitted[5].split('-')
        name = unquote(" ".join(name_split[0:-2]))
        year = name_split[-1]
        car = soup.find_all('h1', {"class": "card-title"})[0].text
        owner = {'car': car, 'ort': ort, 'name': name, 'birth_year': year, 'url': owner_url}
        return owner


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        content = self.handle_http()
        self.wfile.write(json.dumps(content).encode(encoding='utf_8'))

    def handle_http(self):
        if self.path == "/":
            to_user = {"Hello World": "ok"}
        else:
            to_user = {"info": get_owner(self.path.replace("/", ""))}
        return to_user


HOST_NAME = 'localhost'
PORT_NUMBER = 8000

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))