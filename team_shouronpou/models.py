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

    # 変更点1: 開始日を削除し、終了日のみにする
    recruitment_end_date = models.DateField(
        verbose_name="募集終了日", null=True, blank=True
    )

    max_participants = models.IntegerField(
        verbose_name="募集人数 (上限)", 
        null=True, blank=True,
        validators=[MinValueValidator(1)]
    )

    current_participants = models.PositiveIntegerField(
        default=0, verbose_name="現在の参加者数"
    )

    # 変更点2: 実験可能時間を保存するJSONフィールド
    # 例: ["mon_1", "wed_3"] のようなリスト形式で保存
    available_slots = models.JSONField(
        verbose_name="実験受け入れ可能時間",
        default=list,
        blank=True
    )

    # 変更点3: 募集条件を選択式に変更
    # 国籍の選択肢
    NATIONALITY_CHOICES = [
        ('japanese', '日本国籍を有する方'),
        ('any', '不問'),
        ('other', 'その他'),
    ]
    condition_nationality = models.CharField(
        max_length=50, verbose_name="参加条件：国籍",
        choices=NATIONALITY_CHOICES,
        null=True, blank=True
    )

    # 性別の選択肢
    GENDER_CHOICES = [
        ('male', '男性のみ'),
        ('female', '女性のみ'),
        ('any', '不問'),
    ]
    condition_gender = models.CharField(
        max_length=50, verbose_name="参加条件：性別",
        choices=GENDER_CHOICES,
        null=True, blank=True
    )

    # 持病の選択肢
    DISEASE_CHOICES = [
        ('none', 'なし（健康な方）'),
        ('any', '不問'),
        ('specific', '特定の持病がないこと（詳細は内容に記述）'),
    ]
    condition_has_disease = models.CharField(
        max_length=50, verbose_name="参加条件：持病",
        choices=DISEASE_CHOICES,
        null=True, blank=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('team_shouronpou:post_detail', args=[str(self.id)])

    @property
    def remaining_spots(self):
        if self.max_participants is None:
            return None
        diff = self.max_participants - self.current_participants
        return max(0, diff)

