# -*- coding: utf-8 -*-
import urllib.request
from requests.utils import requote_uri
import ssl
import socket
from html import escape
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of


def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


def wait_connection(periode=1):
    while not is_connected():
        print(".", end="")
        sleep(periode)


wait_connection_fonction = wait_connection


def htmlFromUrl(
    url, verify=True, timeout=None, wait_connection=False, selenium_browser=None
):
    if wait_connection:
        wait_connection_fonction()
    url = requote_uri(url)
    if selenium_browser is not None:
        selenium_browser.get(url)
        old_page = selenium_browser.find_element_by_tag_name("html")
        selenium_browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
        # WebDriverWait(selenium_browser, 10).until(staleness_of(old_page))
        sleep(5)
        html = selenium_browser.execute_script(
            "return document.documentElement.outerHTML;"
        )
    else:
        if verify is False:
            myssl = ssl.create_default_context()
            myssl.check_hostname = False
            myssl.verify_mode = ssl.CERT_NONE
            resource = urllib.request.urlopen(url, None, timeout, context=myssl)
        else:
            resource = urllib.request.urlopen(url, None, timeout)
        charset = resource.headers.get_content_charset()
        if charset is None:
            charset = "utf-8"
        html = resource.read().decode(charset)
    return html


def extract(line, before, after):
    beforeIndex = line.find(before)
    if beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = line.find(after, startIndex)
        return line[startIndex:endIndex]
    else:
        return None


def extractVideoAndAudioUrls(html):
    links = set()

    # cherche sous la form
    before = "youtube.com/embed/"
    after = '"'
    searchIndex = 0
    beforeIndex = html.find(before, searchIndex)
    while beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = html.find(after, startIndex)
        youtubeId = html[startIndex:endIndex].split("?")[0]
        if youtubeId.startswith("v="):
            youtubeId = youtubeId[2:]
        youtubeLink = "http://www.youtube.com/watch?v=" + youtubeId
        links.add(youtubeLink)
        beforeIndex = html.find(before, endIndex)

    # cherche sous la form
    # //youtube.com/watch?v= ne permetait pas de telecharger toutes les video d'un compte youtube
    before = "watch?v="
    after = '"'
    searchIndex = 0
    beforeIndex = html.find(before, searchIndex)
    while beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = html.find(after, startIndex)
        youtubeId = html[startIndex:endIndex].split("?")[0]
        youtubeLink = "http://www.youtube.com/watch?v=" + youtubeId
        links.add(youtubeLink)
        beforeIndex = html.find(before, endIndex)

    # cherche videos vimeo
    before = "vimeo.com/video/"
    after = '"'
    searchIndex = 0
    beforeIndex = html.find(before, searchIndex)
    while beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = html.find(after, startIndex)
        youtubeId = html[startIndex:endIndex].split("?")[0]
        youtubeLink = "http://player.vimeo.com/video/" + youtubeId
        links.add(youtubeLink)
        beforeIndex = html.find(before, endIndex)

    # cherche videos dailymotion
    before = "//www.dailymotion.com/embed/video/"
    after = '"'
    searchIndex = 0
    beforeIndex = html.find(before, searchIndex)
    while beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = html.find(after, startIndex)
        Id = html[startIndex:endIndex].split("?")[0]
        link = "http://www.dailymotion.com/embed/video/" + Id
        links.add(link)
        beforeIndex = html.find(before, endIndex)

    # cherche sons soudcloud
    before = "api.soundcloud.com%2Ftracks%2F"
    after = "&"
    searchIndex = 0
    beforeIndex = html.find(before, searchIndex)
    while beforeIndex != -1:
        startIndex = beforeIndex + len(before)
        endIndex = html.find(after, startIndex)
        Id = html[startIndex:endIndex].split("?")[0]
        link = (
            "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/"
            + Id
        )
        links.add(link)
        beforeIndex = html.find(before, endIndex)

    return sorted(list(links))
