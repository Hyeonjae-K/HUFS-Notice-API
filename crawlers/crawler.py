import requests
from bs4 import BeautifulSoup
from itertools import chain

from notices.models import Category, Notice, Attachment


class Soft:
    def crawl(self):
        row_selector = '#board-container > div.list > form:nth-child(2) > table > tbody > tr'
        content_selector = '#board-container > div.view > table > tr > td'
        category = Category.objects.get(id=1)

        # [(author, url, numbers) or None, ...]
        data = [self.parseRow(row) for row in BeautifulSoup(requests.get(
            category.url).text, 'html.parser').select(row_selector)]
        # Remove None and Redundancy
        data = [info for info in data if info and not Notice.objects.filter(
            url=info[1])]

        # info[1] = url
        detail_pages = [BeautifulSoup(requests.get(info[1]).text, 'html.parser').select(
            content_selector) for info in data]
        # Remove title prefix
        titles = [detail_page[0].text[5:] for detail_page in detail_pages]
        # detail_page[-1] is main content section
        contents = [str(detail_page[-1].select_one('div'))
                    for detail_page in detail_pages]
        # detail_page[2] is attachment section
        attachments = [self.parseAttachments(detail_page[2])
                       for detail_page in detail_pages]

        notices = [Notice(title=title, number=info[2], author=info[0], category=category, content=content, url=info[1])
                   for title, info, content in zip(titles, data, contents)]
        if notices:
            Notice.objects.bulk_create(notices)
        # flatten 2D list to 1D list
        attachments = list(chain.from_iterable([self.getAttachments(
            notice, attachment) for notice, attachment in zip(notices, attachments) if attachment]))
        if attachments:
            Attachment.objects.bulk_create(attachments)

    def parseRow(self, row):
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

    def parseAttachments(self, attachment_section):
        '''return [(attachment_title, attachment_download_url), ...] or []'''
        attachment_selector = 'td > a'
        url_prefix = 'https://builder.hufs.ac.kr'
        attachments = attachment_section.select(attachment_selector)

        return [(attachment.text.strip(), url_prefix+attachment.get('onclick')[attachment.get('onclick').find("'")+1:attachment.get('onclick').rfind("'")]) for attachment in attachments]

    def getAttachments(self, notice, attachments):
        return [Attachment(notice=notice, name=attachment[0], url=attachment[1]) for attachment in attachments]


class Ces:
    url_prefix = 'https://computer.hufs.ac.kr'

    def crawl(self):
        row_selector = 'table > tbody > tr'
        content_selector = 'body > div'
        title_selector = 'div.board-view-info > div.view-info > h2'
        main_content_selector = 'div > div.view-con'
        attachment_selector = 'div.view-file > dl > dd > ul > li > a'
        category = Category.objects.get(id=2)

        data = [self.parseRow(row) for row in BeautifulSoup(requests.get(
            category.url).text, 'html.parser').select(row_selector)]
        data = [
            info for info in data if not Notice.objects.filter(url=info[1])]

        detail_pages = [BeautifulSoup(requests.get(
            info[1]).text, 'html.parser').select_one(content_selector) for info in data]
        titles = [detail_page.select_one(title_selector).text.strip()
                  for detail_page in detail_pages]
        contents = [str(detail_page.select_one(main_content_selector))
                    for detail_page in detail_pages]
        attachments = [self.parseAttachments(detail_page.select(
            attachment_selector)) for detail_page in detail_pages]

        notices = [Notice(title=title, number=info[2], author=info[0], category=category,
                          content=content, url=info[1]) for title, info, content in zip(titles, data, contents)]
        if notices:
            Notice.objects.bulk_create(notices)
        attachments = list(chain.from_iterable([self.getAttachments(
            notice, attachment) for notice, attachment in zip(notices, attachments) if attachment]))
        if attachments:
            Attachment.objects.bulk_create(attachments)

    def parseRow(self, row):
        number_selector = 'tr > td.td-num'
        author_selector = 'tr > td.td-write'
        title_selector = 'tr > td.td-subject > a'

        number = int(row.select_one(number_selector).text)
        author = row.select_one(author_selector).text.strip()
        url = self.url_prefix + row.select_one(title_selector).get('href')

        return author, url, number

    def parseAttachments(self, attachments):
        return [(attachment.text.strip(), self.url_prefix + attachment.get('href')) for attachment in attachments]

    def getAttachments(self, notice, attachments):
        return [Attachment(notice=notice, name=attachment[0], url=attachment[1]) for attachment in attachments]
