from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Account(models.Model):
    username = models.CharField("ユーザー名", max_length=150, unique=True)
    password = models.CharField("パスワード", max_length=128) 
    created_at = models.DateTimeField("登録日時", default=timezone.now)
    affiliation = models.CharField("所属（研究室など）", max_length=100, blank=True, null=True)
    age = models.IntegerField("年齢", blank=True, null=True)
    GENDER_CHOICES = [('male', '男性'), ('female', '女性'), ('other', 'その他')]
    gender = models.CharField("性別", max_length=10, choices=GENDER_CHOICES, blank=False, null=False)
    nationality = models.CharField("国籍", max_length=100, blank=True, null=True)
    desired_max_time = models.IntegerField("希望最大時間", blank=True, null=True)
    available_slots = models.JSONField("空き時間", default=list, blank=True, null=True)

    def __str__(self):
        return self.username

class Post(models.Model):
    title = models.CharField("タイトル", max_length=200)
    department = models.CharField("系・所属", max_length=100)
    laboratory = models.CharField("研究室", max_length=100)
    reward = models.CharField("報酬", max_length=200)
    duration = models.IntegerField("所要時間(分)")
    content = models.TextField("内容詳細")
    recruitment_end_date = models.DateField("募集終了日")
    created_at = models.DateTimeField(auto_now_add=True)
    
    created_by = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='posts',
        null=True,
        blank=True
    )

    max_participants = models.IntegerField("最大募集人数", null=True, blank=True)
    current_participants = models.IntegerField("現在の参加者数", default=0)
    available_slots = models.JSONField("受け入れ可能時間", default=list, blank=True, null=True)

    condition_nationality = models.CharField(
        "国籍条件", 
        max_length=100, 
        blank=True, null=True,
        help_text="例: 日本国籍の方のみ、日本語が流暢な方、など"
    )

    GENDER_CHOICES = [
        ('unspecified', '指定なし'),
        ('male', '男性'), 
        ('female', '女性')
    ]
    condition_gender = models.CharField(
        "性別条件", 
        max_length=15, 
        choices=GENDER_CHOICES, 
        default='unspecified',
        blank=False, null=False
    )
    target_age = models.CharField("対象年齢", max_length=100, blank=True, null=True)
    health_notes = models.TextField("健康面で配慮すべき事項", blank=True, null=True)
    free_notes = models.TextField("その他・自由記述", blank=True, null=True)

    # --- 今回追加 ---
    message_for_applicants = models.TextField(
        "応募者へのメッセージ", 
        blank=True, 
        null=True, 
        help_text="応募ボタンが押された後に表示されます。連絡先などを記載してください。"
    )

    @property
    def remaining_spots(self):
        if self.max_participants is None:
            return None
        return max(0, self.max_participants - self.current_participants)

    def __str__(self):
        return self.title

class Application(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='applications')
    # ゲストでもOKにするため null=True, blank=True を追加
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='my_applications', null=True, blank=True)
    email = models.EmailField("連絡用メールアドレス")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ログインユーザーは1回制限。ゲスト(user=None)は制限の対象外にするため
        # Djangoのunique_togetherはNULLを無視するので、ゲストは複数回応募可能です。
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.post.title}"