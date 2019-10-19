#!/usr/bin/env python3.7

__author__ = "Johannes Trepesch"
__version__ = "LOL"
__license__ = "MIT"

from bs4 import BeautifulSoup
from pathlib import Path
import datetime
import requests
import getpass

base_url = 'https://digital.freitag.de/'
login_url = base_url + 'login/'


def setup_login_data(text, username, password):
    soup = BeautifulSoup(text, 'lxml')
    csrf_middleware_token = soup.select_one(
        'input[name="csrfmiddlewaretoken"]')['value']
    nextPage = '/'

    return {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_middleware_token,
        'next': nextPage
    }


def get_download_urls(content):
    soup = BeautifulSoup(content, 'lxml')
    pdf_url = soup.select_one('a[class$="-pdf"]')['href']
    epub_url = soup.select_one('a[class$="-epub"]')['href']

    if pdf_url.startswith('/'):
        pdf_url = base_url + pdf_url[1:]
    if epub_url.startswith('/'):
        epub_url = base_url + epub_url[1:]

    return pdf_url, epub_url


def fetch_newspaper_binaries(username, password):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Referer': login_url + '?next=/',
    }

    with requests.Session() as session:

        login_page = session.get(login_url)
        payload = setup_login_data(login_page.text, username, password)
        start_page = session.post(login_url,
                                  data=payload, headers=headers)

        pdf_url, epub_url = get_download_urls(start_page.content)

        session.headers['Referer'] = base_url
        pdf = session.get(pdf_url)
        epub = session.get(epub_url)

        return {
            'pdf': pdf.content,
            'epub': epub.content
        }


def get_isodate():
    today = datetime.date.today()

    return today.isocalendar()


def create_path(*folders):
    path = Path(*folders)
    path.mkdir(parents=True, exist_ok=True)

    return path


def get_issue_name():
    year, week, _ = get_isodate()
    return '{}{}-der-freitag'.format(year, week)


def write_file(newspaper, path):
    issue_name = get_issue_name()

    for file_format, binaries in newspaper.items():
        file_name = '{}.{}'.format(issue_name, file_format)
        with open(Path(path, file_name), 'wb') as f:
            f.write(binaries)


if __name__ == "__main__":
    username = input('username: ')
    password = getpass.getpass()
    newspaper = fetch_newspaper_binaries(username, password)

    year, week, _ = get_isodate()
    path = create_path('newspaper', str(year), str(week))
    write_file(newspaper, path)
