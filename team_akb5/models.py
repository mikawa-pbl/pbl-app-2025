from django.db import models
from django.utils import timezone
import pytz

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class StatusReport(models.Model):
    """
    ネットワーク状況の報告を保存するモデル
    """
    STATUS_CHOICES = [
        ('slow', '遅い'),  
        ('down', 'つながらない'), 
    ]
    symptom = models.CharField(
        verbose_name='症状',
        max_length=10,
        choices=STATUS_CHOICES
    )

    FLOOR_CHOICES = [
        (1, '1階'),
        (2, '2階'),
        (3, '3階'),
        (4, '4階'),
        (5, '5階'),
        (6, '6階'),
        (7, '7階'),
        (8, '8階'),
        (9, '9階'),
    ]
    floor = models.IntegerField(
        verbose_name='階',
        choices=FLOOR_CHOICES,
        default=1
    )

    description = models.TextField(
        verbose_name='詳細（任意）',
        max_length=100,
        blank=True 
    )

    timestamp = models.DateTimeField(
        verbose_name='発生時刻',
        default=timezone.now
    )

    created_at = models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True
    )

    latitude = models.FloatField(
        verbose_name='緯度',
        blank=True,
        null=True
    )

    longitude = models.FloatField(
        verbose_name='経度',
        blank=True,
        null=True
    )

    def __str__(self):
        # Explicitly define the Tokyo timezone
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        return f'[{self.floor}階] {self.get_symptom_display()} ({self.timestamp.astimezone(tokyo_tz).strftime("%Y-%m-%d %H:%M")})'
