from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Laboratory(models.Model):
    """
    研究室モデル (Ver 5.0)
    動的に追加可能にするため、ハードコードからモデルへ移行
    """
    name = models.CharField(
        verbose_name='研究室名',
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '研究室'
        verbose_name_plural = '研究室一覧'

class ExperimentPost(models.Model):
    """
    実験協力者募集の投稿モデル（Ver 3.0）
    要件定義書の「データモデル・入力フィールド提案」準拠
    ユーザー認証を廃止し、簡易パスワード認証を採用（Ver 3.0）
    """

    # ステータスの選択肢
    STATUS_CHOICES = (
        ('open', '募集中'),
        ('closed', '募集終了'),
    )
    ## *後で検討：終了間近、強調を作成するか？*

    # 研究室の選択肢(V3.1) -> Laboratoryモデルへ移行(V5.0)
    # LAB_CHOICES = ( ... ) 廃止

    # フィールド定義
    title = models.CharField(
        verbose_name='実験名（タイトル）',
        max_length=200
    )
    
    # 変更点(V3): ユーザーモデル紐付け(author)を廃止し、主催者名を追加
    organizer_name = models.CharField(
        verbose_name='主催者名',
        max_length=100,
        help_text='研究室名や氏名など'
    )

    # 変更点(V3): 編集・削除用の4桁数字パスワードを追加
    edit_password = models.CharField(
        verbose_name='編集・削除用パスワード',
        max_length=4,
        validators=[RegexValidator(regex=r'^\d{4}$', message='パスワードは4桁の数字で入力してください')],
        help_text='4桁の数字を入力してください（例: 1234）'
    )

    description = models.TextField(
        verbose_name='実験概要'
    )
    
    # フィールド定義部分の修正（category → laboratory に変更）V5.0
    laboratory = models.ForeignKey(
        'Laboratory',
        on_delete=models.PROTECT, # 研究室が削除されても投稿は消さない（あるいはSET_NULL）だが、通常研究室は消さないのでPROTECT
        verbose_name='研究室',
        null=True, # 既存データ移行用 & 任意選択
        blank=True
    )

    # 重要：Google Forms 機能
    application_url = models.URLField(
        verbose_name='応募用URL',
        help_text='Google Forms等のURLを入力してください'
    )

    start_date = models.DateField(
        verbose_name='募集開始日',
        default=timezone.now
    )

    end_date = models.DateField(
        verbose_name='募集終了日',
        default=timezone.now
    )

    duration = models.CharField(
        verbose_name='所要時間',
        max_length=100,
        help_text='例: 60分程度'
    )

    location = models.CharField(
        verbose_name='実施場所',
        max_length=200,
        help_text='例: ○○キャンパス 3号館201室'
    )

    reward = models.CharField(
        verbose_name='謝礼',
        max_length=200,
        help_text='例: 時給1140円'
    )

    requirements = models.TextField(
        verbose_name='応募条件',
        blank=True,
        null=True
    )
    ## *help_text 追加したい*

    capacity = models.IntegerField(
        verbose_name='募集人数',
        default=1,
        help_text='例: 10'
    )

    status = models.CharField(
        verbose_name='ステータス',
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'
    )

    created_at = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name='更新日時',
        auto_now=True
    )

    def __str__(self):
        return self.title

    @staticmethod
    def process_automatic_updates():
        """
        要件3.6 自動処理機能の実装
        1. 募集終了日を過ぎた'open'ステータスの投稿を'closed'に変更
        2. 募集終了日から1週間(7日)経過した投稿を物理削除
        """
        from datetime import timedelta
        today = timezone.now().date()
        
        # 1. 自動ステータス変更: open でかつ end_date < today のものを closed に
        # (end_date が昨日の日付なら、今日は募集終了している)
        expired_posts = ExperimentPost.objects.filter(
            status='open',
            end_date__lt=today
        )
        if expired_posts.exists():
            expired_posts.update(status='closed')

        # 2. 自動削除: end_date から7日経過したものを削除
        # 今日が 1/20 だとすると、end_date が 1/13 より前 (1/12以下) なら削除対象
        # 1/13 + 7日 = 1/20 なので、今日削除される
        deletion_threshold = today - timedelta(days=7)
        posts_to_delete = ExperimentPost.objects.filter(
            end_date__lt=deletion_threshold
        )
        if posts_to_delete.exists():
            posts_to_delete.delete()

    class Meta:
        verbose_name = '実験募集投稿'
        verbose_name_plural = '実験募集投稿一覧'