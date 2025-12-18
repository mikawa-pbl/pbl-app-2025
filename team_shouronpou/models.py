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
    password = models.CharField("パスワード", max_length=128) # ハッシュ化して保存
    created_at = models.DateTimeField("登録日時", default=timezone.now)

# --- ★追加: 自身のプロフィール ---
    affiliation = models.CharField("所属（研究室など）", max_length=100, blank=True, null=True)
    age = models.IntegerField("年齢", blank=True, null=True)
    
    # 選択肢の定義
    GENDER_CHOICES = [('male', '男性'), ('female', '女性'), ('other', 'その他')]
    gender = models.CharField("性別", max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    NATIONALITY_CHOICES = [('japan', '日本'), ('other', 'その他')]
    nationality = models.CharField("国籍", max_length=10, choices=NATIONALITY_CHOICES, blank=True, null=True)

    # --- ★追加: 参加したい実験の希望条件 ---
    # 報酬情報（自由記述：例「時給1000円以上」「Amazonギフト券希望」など）
    desired_reward = models.CharField("希望する報酬", max_length=200, blank=True, null=True)
    
    # 実験所要時間（分単位で入力：例 60 = 60分以内）
    desired_max_time = models.IntegerField("希望する最大所要時間(分)", blank=True, null=True)
    
    # 実験の実施時刻 (N時 ~ M時)
    available_slots = models.JSONField("参加可能時間帯", default=list, blank=True, null=True)
    
    def __str__(self):
        return self.username


# --- 掲示板機能 ---

# 実験募集の投稿
class Post(models.Model):
    created_by = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="投稿者"
    )
    title = models.CharField("タイトル", max_length=200)
    
    # --- ★追加: 必須項目 ---
    department = models.CharField("系・所属", max_length=100, default="")
    laboratory = models.CharField("研究室", max_length=100, default="")
    reward = models.CharField("報酬の情報", max_length=200, default="")
    duration = models.IntegerField("実験所要時間(分)", help_text="分単位で入力")

    # --- 既存の必須項目 ---
    content = models.TextField("内容")
    recruitment_end_date = models.DateField("募集終了日")
    
    # --- 募集人数まわり（既存） ---
    max_participants = models.IntegerField("最大募集人数", null=True, blank=True)
    current_participants = models.IntegerField("現在の参加者数", default=0)
    available_slots = models.JSONField("受け入れ可能時間", default=list, blank=True, null=True)

    # --- ★追加・変更: 任意項目 ---
    # 国籍・性別は既存のまま残します
    NATIONALITY_CHOICES = [('japan', '日本'), ('other', 'その他')]
    condition_nationality = models.CharField("国籍条件", max_length=10, choices=NATIONALITY_CHOICES, blank=True, null=True)

    GENDER_CHOICES = [('male', '男性'), ('female', '女性'), ('other', 'その他')]
    condition_gender = models.CharField("性別条件", max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    # 年齢（任意）
    target_age = models.CharField("対象年齢", max_length=100, blank=True, null=True, help_text="例: 20代, 18歳以上 など")
    
    # 健康面の配慮（「持病」から置き換え）
    health_notes = models.TextField("健康面で配慮すべき事項", blank=True, null=True, help_text="持病や通院の有無など")
    
    # 自由項目
    free_notes = models.TextField("その他・自由項目", blank=True, null=True)

    # ★削除: condition_has_disease は削除しました

    created_at = models.DateTimeField("作成日", default=timezone.now)

    def __str__(self):
        return self.title

    @property
    def remaining_spots(self):
        if self.max_participants is None:
            return 999 
        return max(0, self.max_participants - self.current_participants)
