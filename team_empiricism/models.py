# Create your models here.
from django.db import models
from django.utils import timezone

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Post(models.Model):

    """
    掲示板の投稿データを表すモデル
    """
    content = models.TextField(
        verbose_name='投稿内容',
    )
    created_at = models.DateTimeField(
        verbose_name='投稿日時',
        default=timezone.now,
    )

    class Meta:
        # 投稿日時の降順（新しい順）で並び替える
        ordering = ['-created_at']

    def __str__(self):
        return self.content[:20]
# --- ここまで追加 ---