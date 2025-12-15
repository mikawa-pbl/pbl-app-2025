from django.db import models
from django.utils import timezone

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Reservation(models.Model):
    """ 施設予約モデル """

    # ステータスフロー: 署名待ち -> 承認待ち -> 承認済み/却下
    STATUS_CHOICES = [
        ('pending_signature', '署名待ち'),
        ('pending_approval', '承認待ち'), # 署名完了、承認者待ち
        ('approved', '承認済み'),
        ('rejected', '却下'),
    ]

    facility_name = models.CharField(verbose_name='施設名', max_length=100)
    applicant_name = models.CharField(verbose_name='申請者名', max_length=100)

    # 新規追加: 責任者（署名者）の名前
    signer_name = models.CharField(verbose_name='責任者（署名者）', max_length=100, default='')

    # 新規追加: 承認者からのコメント
    approver_comment = models.TextField(verbose_name='承認者コメント', blank=True, null=True)

    start_time = models.DateTimeField(verbose_name='開始日時')
    end_time = models.DateTimeField(verbose_name='終了日時')

    status = models.CharField(
        verbose_name='予約状況',
        max_length=20, # 文字数が増えたので拡張
        choices=STATUS_CHOICES,
        default='pending_signature' # 最初は署名待ち
    )

    created_at = models.DateTimeField(verbose_name='申請日時', default=timezone.now)

    def __str__(self):
        return f"{self.facility_name} - {self.status}"

class Notification(models.Model):
    """ 通知モデル """
    # どの役職宛の通知か
    ROLE_CHOICES = [
        ('applicant', '申請者'),
        ('signer', '署名者'),
        ('approver', '承認者'),
    ]

    recipient_role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.CharField(max_length=255)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE) # 関連する予約
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient_role}: {self.message}"