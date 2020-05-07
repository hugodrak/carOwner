#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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

def make_html(owner):
    out = f"""
    <!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>The HTML5 Herald</title>
  <meta name="description" content="The HTML5 Herald">
  <meta name="author" content="SitePoint">
</head>

<body>
    <h1>CarOwner</h1>
    <ul>
        <li><h2>Bil: {owner['car']}</h2></li>
        <li><h2>Ort: {owner['ort']}</h2></li>
        <li><h2>Ägare: {owner['name']}</h2></li>
        <li><h2>Födelseår: {owner['birth_year']}</h2></li>
    </ul>
    <a href={owner['url']}>Full länk</a>
</body>
</html>
    """
    return out


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        if self.path[:4] == "/api":
            self.send_header('Content-type', 'application/json')
        else:
            self.send_header('Content-type', 'text/html')
        self.send_header('charset', 'utf-8')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        content = self.handle_http()
        if self.path[:4] == "/api":
            self.wfile.write(json.dumps(content).encode('utf-8'))
        else:
            self.wfile.write(make_html(content).encode('utf-8'))


    def handle_http(self):
        if self.path == "/":
            to_user = {"Hello World": "ok"}
        else:
            to_user = {"car": "Ford Fiesta 1.4 i", "ort": "Trollhättan", "name": "Krister Joakim Berg", "birth_year": "1968", "url": "http://www.merinfo.se/person/Trollh%C3%A4ttan/Krister-Joakim-Berg-1968/bptl7-2m8y8?utm_source=biluppgifter&utm_medium=owner&utm_term=person"}
            #to_user = get_owner(self.path.replace("/", ""))

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
