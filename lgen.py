#from uuid import uuid4
import requests
import telegram
import logging
import pandas as pd
from telegram import ChatAction
from telegram.ext import CommandHandler
from telegram.ext import Updater
import bs4
import urllib
import dataframe_image as dfi
from telegram.ext import MessageHandler, Filters
import os
PORT = int(os.environ.get('PORT', 5000))


token = "1396085398:AAHMxqWGiFKCyEdqZZufUrgoA1KyEsWADCs"
booksfromrequest = None
bokreq = None
bot = telegram.Bot(token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот, который поможет найти тебе нужную книгу! Отправь команду /books \"название или автор нужной тебе книги\"")
    print(update.effective_chat.id)


def books(update, context):
    request = context.args
    global bokreq
    bokreq = request
    if len(request) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат команды, введите название книги или автора после команды /books")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Запрос на поиск книги получен, обрабатываю...")
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        df = getsearchresult(request, 1, "def")
        if df.empty:
            context.bot.send_message(chat_id=update.effective_chat.id, text="К сожалению, книги не найдены, попробуйте повторить поиск по другим ключевым словам")
        else:
            dfi.export(df, 'books.png')
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("books.png", 'rb'))
            context.bot.send_message(chat_id=update.effective_chat.id, text="Введите команду \"/downl id\" ,чтобы скачать книгу (на место id укажите id нужной Вам книги). Если нужная книга не найдена, Вы можете поискать ее на другой странице, для этого введите команду /page и через пробел укажите номер страницы для повторного поиска, например \"/page 2\"")


def downl(update, context):
    id = context.args
    if len(id) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат команды, после команды /downl через пробел напишите индекс книги, которую вы хотите скачать")
    try:
        id = int(id[0])
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат команды, попробуйте еще раз (после команды не нужно писать слово id, только цифры)")
    if booksfromrequest == None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Книги не найдены")
    try:
        url, ext, title, size = downloadBook(id, booksfromrequest)
        with open("log.txt", "a") as log:
            log.write(title + " " + size)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Что-то пошло не так, проверьте верно ли введен id книги")
    if int(size) > 25:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Размер книги слишком большой, отправляю ссылку...")
        context.bot.send_message(chat_id=update.effective_chat.id, text=url)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Загружаю книгу...")
        try:
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
            urllib.request.urlretrieve(url, f'{title}.{ext}')
            doc = open(f"{title}.{ext}", "rb")
            context.bot.send_document(chat_id=update.effective_chat.id, document=doc)
            doc.close()
            os.remove(f'{title}.{ext}')
        except:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Случилась ошибка, книга не загружена, попробуйте еще раз")

def page(update, context):
    if bokreq == None:
        context.bot.send_message(chat_id=update.effective_chat.id,text="Введите книгу которую вы ходите искать с помощью команды /book после команды, через пробел напишите название нужной Вам книги")
    else:
        pag = context.args
        if len(pag) == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат команды, после команды /page через пробел номер страницы на которую хотите перейти")
        else:
            try:
                pag = int(pag[0])
            except:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный формат команды, попробуйте еще раз (после команды нужно написать номер страницы)")
            df = getsearchresult(bokreq, pag, "def")
            if df.empty:
                context.bot.send_message(chat_id=update.effective_chat.id, text="К сожалению, книги не найдены, попробуйте повторить поиск по другим ключевым словам")
            else:
                dfi.export(df, 'books.png')
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("books.png", 'rb'))
                context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Введите команду \"/downl id\" , на место id укажите id нужной Вам книги")



def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не знаю такой команды :(")


def getsearchresult(book, page, column):
    params = urllib.parse.urlencode({'req': book, 'column': column, 'page': page})
    url = 'http://libgen.is/search.php?&%s' % params
    source = urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(source, 'lxml')
    page_books = soup.find_all('tr')
    page_books = page_books[3:-1]
    books = page_books
    global booksfromrequest
    booksfromrequest = books
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
    if len(id) == 1:
        id.append(" ")
        author.append(" ")
        title.append(" ")
        publisher.append(" ")
        years.append(" ")
        pages.append(" ")
        language.append(" ")
        size.append(" ")
        extension.append(" ")
    zi = list(zip(id, author, title, publisher, years, pages, language, size, extension))
    df = pd.DataFrame(zi, columns=["ID", "Author", "Title", "Publisher", "Year", "Pages", "Language", "Size", "Extension"])
    return df

def getBooks(book, page, column):
    params = urllib.parse.urlencode({'req': book, 'column': column, 'page': page})
    url = 'http://libgen.is/search.php?&%s' % params
    source = urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(source, 'lxml')
    page_books = soup.find_all('tr')
    page_books = page_books[3:-1]
    books = page_books
    return books

def downloadBook(id, books):
    for book in books:
        s = book.find_all("td")
        if id == int(s[0].text):
            #print('Downloading...')
            extention = s[8].text
            title = s[2].text
            size = s[7].text.split()
            size = size[0]
            mirrors = [s[i].find("a").attrs['href'] for i in range(9,14)]
            #print(mirrors)
            source = urllib.request.urlopen(mirrors[0])
            soup = bs4.BeautifulSoup(source, 'lxml')
            urls = soup.find_all("a")
            for url in urls:
                if url.text == "GET":
                    urla = url.attrs["href"]
                    break
            return urla, extention, title, size


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

books_handler = CommandHandler('books', books)
dispatcher.add_handler(books_handler)

downl_handler = CommandHandler('downl', downl)
dispatcher.add_handler(downl_handler)

page_handler = CommandHandler('page', page)
dispatcher.add_handler(page_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=token)
updater.bot.setWebhook('https://yourherokuappname.herokuapp.com/https://sleepy-beyond-10359.herokuapp.com/' + token)



