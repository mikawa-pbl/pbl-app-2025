from django.db import models
from django.utils import timezone
import pytz # Re-introduce pytz

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

    LOCATION_CHOICES = [
        ('A', 'A棟'),
        ('B', 'B棟'),
        ('C', 'C棟'),
        ('D', 'D棟'),
    ]
    location = models.CharField(
        verbose_name='場所',
        max_length=1,
        choices=LOCATION_CHOICES
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

    def __str__(self):
        # Explicitly define the Tokyo timezone
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        return f'[{self.get_location_display()}] {self.get_symptom_display()} ({self.timestamp.astimezone(tokyo_tz).strftime("%Y-%m-%d %H:%M")})'
