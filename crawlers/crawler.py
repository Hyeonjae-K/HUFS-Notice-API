import requests
from bs4 import BeautifulSoup
from itertools import chain

from notices.models import Category, Notice, Attachment


def crawl_soft():
    row_selector = '#board-container > div.list > form:nth-child(2) > table > tbody > tr'
    title_selector = 'td.title > a'
    author_selector = 'td:nth-child(5)'
    url_prefix = 'https://builder.hufs.ac.kr'
    content_selector = '#board-container > div.view > table > tr > td'
    attachment_selector = 'td > a'
    category = Category.objects.get(id=1)
    rows = [row for row in BeautifulSoup(requests.get(
        category.url).text, 'html.parser').select(row_selector) if row.span]
    titles = [row.select_one(title_selector).text.strip() for row in rows]
    new_indexes = [i for i, title in enumerate(
        titles) if not Notice.objects.filter(title=title)]
    rows = [rows[i] for i in new_indexes]
    titles = [titles[i] for i in new_indexes]
    authors = [row.select_one(author_selector).text.strip() for row in rows]
    urls = [url_prefix + '/user/' +
            row.select_one(title_selector).get('href')for row in rows]
    numbers = list(map(int, [url[url.rfind('=')+1:] for url in urls]))
    detail_pages = [BeautifulSoup(requests.get(url).text, 'html.parser').select(
        content_selector) for url in urls]
    contents = [str(detail_page[-1].select_one('div'))
                for detail_page in detail_pages]
    attachments = [[(attach.text.strip(), url_prefix + attach.get('onclick')[attach.get('onclick').find("'")+1:attach.get('onclick').rfind("'")])
                    for attach in detail_page[2].select(attachment_selector)] for detail_page in detail_pages]
    notices = [Notice(title=title, number=number, author=author, category=category, content=content, url=url)
               for title, number, author, content, url in zip(titles, numbers, authors, contents, urls)]
    Notice.objects.bulk_create(notices)
    attachments = list(chain.from_iterable([_getAttachments(
        notice, attachment) for notice, attachment in zip(notices, attachments) if attachment]))
    Attachment.objects.bulk_create(attachments)


def _getAttachments(notice, attachments):
    return [Attachment(notice=notice, name=attachment[0], url=attachment[1]) for attachment in attachments]
