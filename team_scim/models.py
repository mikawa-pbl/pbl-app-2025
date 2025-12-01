from django.db import models
from django.utils import timezone

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
class Reservation(models.Model):
    """ 施設予約モデル """
    
    # 予約状況の選択肢
    STATUS_CHOICES = [
        ('pending', '申請中'),
        ('approved', '承認済み'),
        ('rejected', '却下'),
    ]

    facility_name = models.CharField(verbose_name='施設名', max_length=100)
    applicant_name = models.CharField(verbose_name='申請者名', max_length=100)
    
    start_time = models.DateTimeField(verbose_name='開始日時')
    end_time = models.DateTimeField(verbose_name='終了日時')
    
    status = models.CharField(
        verbose_name='予約状況',
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending' # デフォルトは「申請中」
    )
    
    created_at = models.DateTimeField(verbose_name='申請日時', default=timezone.now)

    def __str__(self):
        # 管理画面などで見やすくするための設定
        return f"{self.facility_name} ({self.start_time.strftime('%Y-%m-%d %H:%M')}) - {self.status}"