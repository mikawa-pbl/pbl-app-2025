from django.db import models
import uuid

# Create your models here.

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class BookReview(models.Model):
    """
    参考書レビューモデル
    科目ごとにおすすめの参考書をユーザが投稿できる
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=50, verbose_name="科目名")
    isbn = models.CharField(max_length=13, verbose_name="ISBN")
    review = models.TextField(max_length=200, verbose_name="レビュー")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "参考書レビュー"
        verbose_name_plural = "参考書レビュー"

    def __str__(self):
        return f"{self.subject} - ISBN:{self.isbn}"