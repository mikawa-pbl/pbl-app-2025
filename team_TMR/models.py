from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# 招待コードモデル
class InvitationCode(models.Model):
    code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

# プロフィールモデル
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_constraint=False)
    nickname = models.CharField(max_length=100, blank=True)
    affiliation = models.CharField(max_length=200, blank=True, help_text="所属（例：〇〇大学 〇〇学部）")
    contact = models.EmailField(max_length=255, blank=True, null=True, help_text="連絡先（任意）")

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    db_alias = 'team_TMR' 
    if created:
        Profile.objects.using(db_alias).create(user_id=instance.id)
    else:
        try:
            Profile.objects.using(db_alias).get(user_id=instance.id)
        except Profile.DoesNotExist:
            Profile.objects.using(db_alias).create(user_id=instance.id)

# ロードマップモデル（★ここに start_date, end_date があることが必須です）
class Roadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roadmaps", db_constraint=False)
    title = models.CharField(max_length=200, verbose_name="タイトル")
    
    # ★この2行が必要です
    start_date = models.DateField(verbose_name="開始日", null=True, blank=True)
    end_date = models.DateField(verbose_name="終了日", null=True, blank=True)
    
    content = models.TextField(help_text="詳細な内容", verbose_name="詳細")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', '-created_at']

    def __str__(self):
        return self.title

# ESモデル
class ES(models.Model):
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