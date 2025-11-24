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
    # 就活関連フィールド
    company_name = models.CharField(max_length=200, default='')  # 会社名
    interview_stage = models.CharField(max_length=100, default='')  # 面接段階
    interview_date = models.DateField(null=True, blank=True)  # 面接日
    status = models.CharField(max_length=100, default='')  # 選考状況

    # メモ内容
    content = models.TextField()  # メモの内容

    # 日時フィールド
    date = models.DateField(default=timezone.now)  # メモの対象日付(既存データには今日の日付が設定されます)
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    def __str__(self):
        return f"{self.company_name} - {self.interview_stage}: {self.content[:30]}"
