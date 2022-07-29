from rest_framework import serializers

from notices.models import Category, Notice, Attachment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'url')


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'name', 'url')


class NoticeSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(
        many=True, read_only=True, source='notice')
    category_name = serializers.CharField(source='category.name')

    class Meta:
        model = Notice
        fields = ('id', 'title', 'number', 'author', 'category_name',
                  'attachments', 'content', 'url', 'created_date')


class NoticeListSerialzer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')

    class Meta:
        model = Notice
        fields = ('id', 'title', 'category_name', 'created_date')
