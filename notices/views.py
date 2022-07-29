from notices.models import Category, Notice
from rest_framework import viewsets
from notices.serializers import NoticeSerializer, NoticeListSerialzer, CategorySerializer


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer


class NoticeListViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeListSerialzer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
