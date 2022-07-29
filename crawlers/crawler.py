import requests
from bs4 import BeautifulSoup
from itertools import chain

from notices.models import Category, Notice, Attachment


def crawl_soft():
    row_selector = '#board-container > div.list > form:nth-child(2) > table > tbody > tr'
    content_selector = '#board-container > div.view > table > tr > td'
    category = Category.objects.get(id=1)

    # [(author, url, numbers) or None, ...]
    data = [_parseRow(row) for row in BeautifulSoup(requests.get(
        category.url).text, 'html.parser').select(row_selector)]
    # Remove None and Redundancy
    data = [info for info in data if info and not Notice.objects.filter(
        number=info[2])]

    # info[1] = url
    detail_pages = [BeautifulSoup(requests.get(info[1]).text, 'html.parser').select(
        content_selector) for info in data]
    # Remove title prefix
    titles = [detail_page[0].text[5:] for detail_page in detail_pages]
    # detail_page[-1] is main content section
    contents = [str(detail_page[-1].select_one('div'))
                for detail_page in detail_pages]
    # detail_page[2] is attachment section
    attachments = [_parseAttachments(detail_page[2])
                   for detail_page in detail_pages]

    notices = [Notice(title=title, number=info[2], author=info[0], category=category, content=content, url=info[1])
               for title, info, content in zip(titles, data, contents)]
    if notices:
        Notice.objects.bulk_create(notices)
    # flatten 2D list to 1D list
    attachments = list(chain.from_iterable([_getAttachments(
        notice, attachment) for notice, attachment in zip(notices, attachments) if attachment]))
    if attachments:
        Attachment.objects.bulk_create(attachments)


def _parseRow(row):
    '''if fixed notice return None
    else (author, url, number)'''
    title_selector = 'td.title > a'
    author_selector = 'td:nth-child(5)'
    url_prefix = 'https://builder.hufs.ac.kr/user/'

    if not row.span:
        return

    author = row.select_one(author_selector).text.strip()
    url = url_prefix + row.select_one(title_selector).get('href')
    number = int(url[url.rfind('=')+1:])

    return author, url, number


def _parseAttachments(attachment_section):
    '''return [(attachment_title, attachment_download_url), ...] or []'''
    attachment_selector = 'td > a'
    url_prefix = 'https://builder.hufs.ac.kr'
    attachments = attachment_section.select(attachment_selector)

    return [(attachment.text.strip(), url_prefix+attachment.get('onclick')[attachment.get('onclick').find("'")+1:attachment.get('onclick').rfind("'")]) for attachment in attachments]


def _getAttachments(notice, attachments):
    return [Attachment(notice=notice, name=attachment[0], url=attachment[1]) for attachment in attachments]
