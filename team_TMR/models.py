from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# 招待コードモデル
class InvitationCode(models.Model):
    """
    ユーザー登録時に使用する招待コード。
    """
    code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

# プロフィールモデル
class Profile(models.Model):
    """
    Django標準のUserモデルに紐づくプロフィール。
    """
    # 【修正】異なるDB間のリレーションのため db_constraint=False を追加
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_constraint=False)
    nickname = models.CharField(max_length=100, blank=True)
    affiliation = models.CharField(max_length=200, blank=True, help_text="所属（例：〇〇大学 〇〇学部）")
    contact = models.EmailField(max_length=255, blank=True, null=True, help_text="連絡先（任意）")

    def __str__(self):
        return self.user.username

# --- ★★★ シグナルの修正点 ★★★ ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Userが保存されたときに、'team_TMR' データベース側で Profile を
    作成または更新するシグナル。
    """
    db_alias = 'team_TMR' 

    if created:
        # 【修正】user=instance ではなく user_id=instance.id を使用してルーター制限を回避
        Profile.objects.using(db_alias).create(user_id=instance.id)
    else:
        try:
            # 【修正】ここも user_id で検索
            profile = Profile.objects.using(db_alias).get(user_id=instance.id)
            pass 
        except Profile.DoesNotExist:
            # 【修正】ここも user_id で作成
            Profile.objects.using(db_alias).create(user_id=instance.id)

# ロードマップモデル
class Roadmap(models.Model):
    # 【修正】異なるDB間のリレーションのため db_constraint=False を追加
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roadmaps", db_constraint=False)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="ステップや目標などを自由に記述してください。")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# ES（エントリーシート）モデル
class ES(models.Model):
    # 【修正】異なるDB間のリレーションのため db_constraint=False を追加
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="es_entries", db_constraint=False)
    company = models.CharField(max_length=100, verbose_name="企業名")
    question = models.TextField(verbose_name="設問")
    answer = models.TextField(verbose_name="回答")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ES"
        verbose_name_plural = "ES"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.company} - {self.question[:30]}..."