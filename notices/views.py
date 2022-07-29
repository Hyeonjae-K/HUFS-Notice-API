from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from apscheduler.schedulers.background import BackgroundScheduler

from notices.models import Category, Notice
from notices.serializers import NoticeSerializer, NoticeListSerialzer, CategorySerializer
from crawlers import crawler

sched = BackgroundScheduler()
sched.add_job(crawler.crawl_soft, 'cron', minute='0')
sched.start()


class OneResultSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    pagination_class = OneResultSetPagination


class NoticeListViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeListSerialzer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
