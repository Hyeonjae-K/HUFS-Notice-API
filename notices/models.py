from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=25)
    url = models.URLField()
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Notice(models.Model):
    title = models.CharField(max_length=100)
    number = models.BigIntegerField()
    author = models.CharField(max_length=25)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category')
    content = models.TextField()
    url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Attachment(models.Model):
    notice = models.ForeignKey(
        Notice, on_delete=models.CASCADE, related_name='notice')
    name = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return f"{self.name} ({self.notice.title})"
