#!/usr/bin/env python3.7

__author__ = "Johannes Trepesch"
__version__ = "LOL"
__license__ = "MIT"

import requests
import getpass
from requests.auth import HTTPBasicAuth
from pathlib import Path
from xml.etree import ElementTree

from gooddogfetchnewspaper import fetch_newspaper_binaries, get_issue_name, get_isodate


def folder_exists(tree):
    for response in tree.findall('{DAV:}response'):
        for href in response.findall('{DAV:}href'):
            return True
    return False


def createFolderIfNotExists(session, base_url, folder_path):
    folders = folder_path.split('/')

    for index, folder in enumerate(folders):
        path = '/'.join(folders[0:index] + [folder])
        response = session.request(
            'PROPFIND', base_url + path)
        tree = ElementTree.fromstring(response.content)

        if folder_exists(tree):
            print('{} already exists, no action needed.'.format(base_url + path))
        else:
            print('Creating folder {}'.format(base_url + path))
            response = session.request(
                'MKCOL', base_url + path)
            print(response.status_code)


def upload_to_cloud(newspaper, username, password):
    year, week, _ = get_isodate()
    issue_name = get_issue_name()
    issue_url = '/'.join([base_url, str(year), str(week), ''])

    with requests.Session() as session:
        session.auth = (username, password)

        createFolderIfNotExists(session, base_url,
                                '/'.join([str(year), str(week)]))

        for file_format, binaries in newspaper.items():
            file_name = "{}.{}".format(issue_name, file_format)
            response = session.put(
                issue_url + file_name, data=binaries)


if __name__ == "__main__":
    username_nc = input('username nextcloud: ')
    password_nc = getpass.getpass('password nextcloud: ')

    username_fr = input('username newspaper: ')
    password_fr = getpass.getpass('password newspaper: ')

    domain = input('nextcloud domain (without https://): ')

    base_url = 'https://{}/remote.php/dav/files/{}/newspaper/'.format(
        domain, username_nc)

    newspaper = fetch_newspaper_binaries(username_fr, password_fr)
    upload_to_cloud(newspaper, username_nc, password_nc)
