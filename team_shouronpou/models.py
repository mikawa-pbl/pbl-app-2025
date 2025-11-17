from django.db import models
from django.conf import settings
from django.urls import reverse

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# --- 掲示板機能 ---

# 実験募集の投稿
class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="募集タイトル")
    content = models.TextField(verbose_name="募集内容")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    recruitment_start_date = models.DateField(
        verbose_name="募集開始日", 
        null=True,  # 入力なし(空)でもOK
        blank=True  # フォームで空欄を許可
    )
    recruitment_end_date = models.DateField(
        verbose_name="募集終了日",
        null=True,
        blank=True
    )
    max_participants = models.IntegerField(
        verbose_name="募集人数 (上限)",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # 詳細ページへのURLを返す
        return reverse('team_shouronpou:post_detail', args=[str(self.id)])