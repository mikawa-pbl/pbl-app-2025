from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator

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
        blank=True,
        validators=[MinValueValidator(1)]
    )
    condition_nationality = models.CharField(
        max_length=100,
        verbose_name="参加条件：国籍",
        null=True, blank=True,
        help_text="例: 日本国籍を有する方、不問 など"
    )
    condition_gender = models.CharField(
        max_length=100,
        verbose_name="参加条件：性別",
        null=True, blank=True,
        help_text="例: 男性のみ、女性のみ、不問 など"
    )
    condition_has_disease = models.CharField(
        max_length=200,
        verbose_name="参加条件：持病の有無",
        null=True, blank=True,
        help_text="例: なし、呼吸器系の持病がないこと など"
    )
    current_participants = models.PositiveIntegerField(
        default=0,
        verbose_name="現在の参加者数"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # 詳細ページへのURLを返す
        return reverse('team_shouronpou:post_detail', args=[str(self.id)])

    @property
    def remaining_spots(self):
        if self.max_participants is None:
            return None # 上限なし
        diff = self.max_participants - self.current_participants
        return max(0, diff)
