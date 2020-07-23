token = "1396085398:AAHMxqWGiFKCyEdqZZufUrgoA1KyEsWADCs"

import requests
import urllib
import bs4
import re
import pandas as pd
from pprint import pprint
import os
def getsearchresult(term, page, column):
    params = urllib.parse.urlencode({'req': term, 'column': column, 'page': page})
    url = 'http://libgen.is/search.php?&%s' % params
    #print(url)
    source = urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(source, 'lxml')
    #print(soup)
    """with open('htl.txt', 'w') as wr:
        wr.write(str(soup))
    """
    '''
    if page == 1:
        books_found = re.search(r'title id=\d+', str(soup))
        print(books_found)
        print(books_found.group().upper())
        n_books = int(books_found.groups()[0])
    '''
    page_books = soup.find_all('tr')
    page_books = page_books[3:-1]  # Ignore 3 first and the last <tr> label.
    books = page_books
    print(books)
    id = []
    author = []
    title = []
    publisher = []
    years = []
    pages = []
    language = []
    size = []
    extension = []
    for book in books:
        s = book.find_all("td")
        id.append(s[0].text)
        author.append(s[1].text)
        title.append(s[2].text)
        publisher.append(s[3].text)
        years.append(s[4].text)
        pages.append(s[5].text)
        language.append(s[6].text)
        size.append(s[7].text)
        extension.append(s[8].text)

    zi = list(zip(id, author, title, publisher, years, pages, language, size, extension))
    df = pd.DataFrame(zi, columns=["ID", "Author", "Title", "Publisher", "Year", "Pages", "Language", "Size", "Extension"])
    return df


df = getsearchresult("book", 1, "def")

# modified from http://cssmenumaker.com/br/blog/stylish-css-tables-tutorial
css = """<style type=\"text/css\">
table {
color: #333;
font-family: Helvetica, Arial, sans-serif;
width: 640px;
border-collapse:
collapse; 
border-spacing: 0;
}
td, th {
border: 1px solid transparent; /* No more visible border */
height: 30px;
}
th {
background: #DFDFDF; /* Darken header a bit */
font-weight: bold;
}
td {
background: #FAFAFA;
text-align: center;
}
table tr:nth-child(odd) td{
background-color: white;
}
</style>
"""
"""
text_file = open("filename.html", "a")
# write the CSS
text_file.write(css)
# write the HTML-ized Pandas DataFrame
text_file.write(df.to_html())
text_file.close()

"""
"""
import imgkit
import os
path = "/Users/ivashkaleha/PycharmProjects/newlgen/venv/lib/python3.8/site-packages/wkhtmltopdf"
config = imgkit.config(wkhtmltoimage=path)
imgkit.from_url('http://google.com', 'out.jpg')
#img = imgkit.from_url('http://google.com', False)
#print(img)
#imgkitoptions = {"format": "png"}
imgkit.from_file("filename.html", "/Users/ivashkaleha/Desktop/output.png", config=config)
print("sdf")
"""

from bokeh.io import export_png, export_svgs
from bokeh.models import ColumnDataSource, DataTable, TableColumn

"""
def save_df_as_image(df, path):
    source = ColumnDataSource(df)
    df_columns = [df.index.name]
    df_columns.extend(df.columns.values)
    columns_for_table=[]
    for column in df_columns:
        columns_for_table.append(TableColumn(field=column, title=column))

    data_table = DataTable(source=source, columns=columns_for_table, height_policy="auto", width_policy="max", index_position=None)
    export_png(data_table, filename=path, width=10)

save_df_as_image(df, "/Users/ivashkaleha/Desktop/output.png")
"""


import dataframe_image as dfi
dfi.export(df, 'foto.png')


class DownloadBook():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    accept_charset = 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
    accept_lang = 'en-US,en;q=0.8'
    connection = 'keep-alive'

    headers = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Charset': accept_charset,
        'Accept-Language': accept_lang,
        'Connection': connection,
    }

    DOWNLOAD_PATH = "."

    def save_book(download_link, file_name):
        if os.path.exists(DOWNLOAD_PATH) and os.path.isdir(DOWNLOAD_PATH):
            bad_chars = '\/:*?"<>|'
            for char in bad_chars:
                file_name = file_name.replace(char, " ")
            print('Downloading...')
            path = '{}/{}'.format(DOWNLOAD_PATH, file_name)
            requests.request.urlretrieve(download_link, filename=path)
            print('Book downloaded to {}'.format(os.path.abspath(path)))
        elif os.path.isfile(DOWNLOAD_PATH):
            print('The download path is not a directory. Change it in settings.py')
        else:
            print('The download path does not exist. Change it in settings.py')

    def default_mirror(link, filename):
        '''This is the default (and first) mirror to download.
        The base of this mirror is http://booksdescr.org'''
        req = urllib.request.Request(link, headers=DownloadBook.headers)
        source = requests.request.urlopen(req)
        soup = bs4.BeautifulSoup(source, 'lxml')

        for a in soup.find_all('a'):
            if a.text == 'Libgen':
                download_url = a.attrs['href']
                DownloadBook.save_book(download_url, filename)


    def second_mirror(link, filename):
        '''This is the second mirror to download.
        The base of this mirror is https://libgen.me'''
        req = urllib.request.Request(link, headers=DownloadBook.headers)
        source = urllib.request.urlopen(req)
        soup = bs4.BeautifulSoup(source, 'lxml')
        mother_url = "https://libgen.me"

        for a in soup.find_all('a'):
            if a.text == 'Get from vault':
                next_link = a.attrs['href']
                next_req = urllib.request.Request(mother_url + next_link, headers=DownloadBook.headers)
                next_source = urllib.request.urlopen(next_req)
                next_soup = bs4.BeautifulSoup(next_source, 'lxml')
                for next_a in next_soup.find_all('a'):
                    if next_a.text == 'Get':
                        item_url = next_a.attrs['href']
                        DownloadBook.save_book(item_url, filename)

    def third_mirror(link, filename):
        '''This is the third mirror to download.
        The base of this mirror is http://library1.org'''
        req = requests.request.Request(link, headers=DownloadBook.headers)
        source = requests.request.urlopen(req)
        soup = bs4.BeautifulSoup(source, 'lxml')

        for a in soup.find_all('a'):
            if a.text == 'GET':
                download_url = a.attrs['href']
                DownloadBook.save_book(download_url, filename)

    def fourth_mirror(link, filename):
        '''This is the fourth mirror to download.
        The base of this mirror is https://b-ok.cc'''
        req = requests.request.Request(link, headers=DownloadBook.headers)
        source = requests.request.urlopen(req)
        soup = bs4.BeautifulSoup(source, 'lxml')
        mother_url = "https://b-ok.cc"

        for a in soup.find_all('a'):
            if a.text == 'DOWNLOAD':
                next_link = a.attrs['href']
                next_req = requests.request.Request(mother_url + next_link, headers=DownloadBook.headers)
                next_source = requests.request.urlopen(next_req)
                next_soup = bs4.BeautifulSoup(next_source, 'lxml')
                for next_a in next_soup.find_all('a'):
                    if ' Download  ' in next_a.text:
                        item_url = next_a.attrs['href']
                        DownloadBook.save_book(mother_url + item_url, filename)

    def fifth_mirror(link, filename):
        '''This is the fifth mirror to download.
        The base of this mirror is https://bookfi.net'''
        req = requests.request.Request(link, headers=DownloadBook.headers)
        source = requests.request.urlopen(req)
        soup = bs4.BeautifulSoup(source, 'lxml')

        for a in soup.find_all('a'):
            if 'Скачать' in a.text:
                download_url = a.attrs['href']
                DownloadBook.save_book(download_url, filename)


import requests
import datetime

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]

        return last_update






def main():
    greet_bot = BotHandler(token)
    greetings = ('здравствуй', 'привет', 'ку', 'здорово')
    now = datetime.datetime.now()

    new_offset = None
    today = now.day
    hour = now.hour

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
            greet_bot.send_message(last_chat_id, 'Доброе утро, {}'.format(last_chat_name))
            today += 1

        elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
            greet_bot.send_message(last_chat_id, 'Добрый день, {}'.format(last_chat_name))
            today += 1

        elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
            greet_bot.send_message(last_chat_id, 'Добрый вечер, {}'.format(last_chat_name))
            today += 1

        new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()