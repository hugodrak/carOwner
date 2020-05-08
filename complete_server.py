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
        polis = False
        if splitted[3] == "person":
            ort = unquote(splitted[4])
            name_split = splitted[5].split('-')
            name = unquote(" ".join(name_split[0:-1]))
            year = name_split[-1]
            car = soup.find_all('h1', {"class": "card-title"})[0].text
            owner = {'polis': polis, 'car': car, 'ort': ort, 'name': name, 'birth_year': year, 'url': owner_url, 'reg': reg_nr.upper()}
        elif splitted[3] == "foretag":
            name_split = splitted[4].split('-')
            if name_split[-1] == "2021000076":
                polis = True
            name = unquote(" ".join(name_split))
            car = soup.find_all('h1', {"class": "card-title"})[0].text
            owner = {'polis': polis, 'car': car, 'name': name, 'url': owner_url, 'reg': reg_nr.upper()}
        else:
            owner = {"null": "null"}
        return owner
    else:
        return {"null": "regnr not found"}

def make_html(owner):
    if "null" not in owner.keys():
        if "ort" in owner.keys():
            out = f"""
            <!doctype html>

        <html lang="en">
        <head>
          <meta charset="utf-8">

          <title>Car Owner Sweden</title>
          <meta name="description" content="Car Owner Sweden">
          <meta name="author" content="SitePoint">
        </head>

        <body>
            <h1>CarOwner</h1>
            <ul>
                <li><h2>Reg Nr: {owner['reg']}</h2></li>
                <li><h2>Bil: {owner['car']}</h2></li>
                <li><h2>Ort: {owner['ort']}</h2></li>
                <li><h2>Ägare: {owner['name']}</h2></li>
                <li><h2>Födelseår: {owner['birth_year']}</h2></li>
            </ul>
            <a href={owner['url']}>Full länk</a>
        </body>
        </html>
            """
        else:
            polis = ""
            if owner["polis"] == True:
                polis = '<h1 style="color: red;">Detta är en polis!</h1>'
            out = f"""
            <!doctype html>

        <html lang="en">
        <head>
          <meta charset="utf-8">

          <title>Car Owner Sweden</title>
          <meta name="description" content="Car Owner Sweden">
          <meta name="author" content="SitePoint">
        </head>

        <body>
            <h1>CarOwner</h1>
            {polis}
            <ul>
                <li><h2>Reg Nr: {owner['reg']}</h2></li>
                <li><h2>Bil: {owner['car']}</h2></li>
                <li><h2>Företag: {owner['name']}</h2></li>
            </ul>
            <a href={owner['url']}>Full länk</a>
        </body>
        </html>
            """
    else:
        out = owner["null"]
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
        raw_content = self.handle_http()
        if self.path[:4] == "/api":
            self.wfile.write(json.dumps(raw_content).encode('utf-8'))
        else:
            if type(raw_content) == dict:
                content = make_html(raw_content)
            elif type(raw_content) == str:
                content = raw_content
            else:
                return 0
            self.wfile.write(content.encode('utf-8'))


    def handle_http(self):
        if self.path == "/":
            to_user = "Hello World\n Please use /*dittregnr* or /api/*dittregnr*"
        else:
            path = self.path.replace("/", "")
            if path[:3] == "api":
                path = path[3:]
            if len(path) == 6 and path[3:5].isdigit():
                  to_user = get_owner(path)
            else:
                return "Wrong format"
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
