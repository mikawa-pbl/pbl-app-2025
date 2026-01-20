from django.db import models
from django.utils import timezone


class Account(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = '会社'
        verbose_name_plural = '会社'

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)  # イベントのタイトル
    description = models.TextField(blank=True)  # イベントの説明
    start_time = models.DateTimeField()  # 開始日時
    end_time = models.DateTimeField()  # 終了日時

    def __str__(self):
        return self.title


class Memo(models.Model):
    # アカウント（ユーザー）
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)

    # 就活関連フィールド
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='memos')  # 会社
    job_category = models.CharField(max_length=100, default='', blank=True)  # 職種カテゴリー
    interview_stage = models.CharField(max_length=100, default='')  # 面接段階
    interview_date = models.DateField(null=True, blank=True)  # 面接日

    # 面接詳細フィールド（面接系イベント用）
    interview_questions = models.TextField(blank=True, default='')  # 面接で聞かれたこと
    interview_details = models.TextField(blank=True, default='')  # 面接の詳細メモ

    # メモ内容
    title = models.CharField(max_length=100, blank=True, default='')  # メモのタイトル
    content = models.TextField()  # メモの内容

    # 日時フィールド
    date = models.DateField(default=timezone.now)  # メモの対象日付(既存データには今日の日付が設定されます)
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    def __str__(self):
        company_name = self.company.name if self.company else '(会社未設定)'
        return f"{company_name} - {self.interview_stage}: {self.content[:30]}"


class QuestionAnswer(models.Model):
    """面接質問への回答を保存するモデル"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()  # 質問内容
    answer = models.TextField(blank=True, default='')  # 回答内容
    related_memo = models.ForeignKey(Memo, on_delete=models.SET_NULL, null=True, blank=True)  # 関連するメモ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        company_name = self.company.name if self.company else '共通質問'
        return f"{company_name}: {self.question[:30]}"
