from django.db import models
from django.utils import timezone


class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Event(models.Model):
    title = models.CharField(max_length=200)  # イベントのタイトル
    description = models.TextField(blank=True)  # イベントの説明
    start_time = models.DateTimeField()  # 開始日時
    end_time = models.DateTimeField()  # 終了日時

    def __str__(self):
        return self.title


class Memo(models.Model):
    date = models.DateField(default=timezone.now)  # メモの対象日付（既存データには今日の日付が設定されます）
    content = models.TextField()  # メモの内容
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    def __str__(self):
        return f"{self.date}: {self.content[:50]}"  # 日付とメモの冒頭50文字を表示
