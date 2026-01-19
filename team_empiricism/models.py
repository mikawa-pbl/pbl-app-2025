from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

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

    # # カテゴリの選択肢 (要件3.2のフィルタリング項目より)
    # CATEGORY_CHOICES = (
    #     ('psychology', '心理学'),
    #     ('medical', '医学'),
    #     ('engineering', '工学'),
    #     ('survey', 'アンケート'),
    #     ('other', 'その他'),
    # )
    ## *後で変更：タグが荒い？制限は必要*

    # 研究室の選択肢(V3.1)
    LAB_CHOICES = (
        ('hukumura', '生体運動制御システム研究室（福村研）'),
        ('kitazaki', '視覚心理物理学研究室（北崎研）'),
        ('nakauti', '視覚認知情報学研究室（中内研）'),
        ('other', 'その他'),
    )

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
    
    # category = models.CharField(
    #     verbose_name='カテゴリ',
    #     max_length=50,
    #     choices=CATEGORY_CHOICES,
    #     default='other'
    # )

    # フィールド定義部分の修正（category → laboratory に変更）V3.1
    category = models.CharField(
        max_length=50,
        choices=LAB_CHOICES, # ここで上記の選択肢を指定
        verbose_name='研究室', # 画面上のラベルも「研究室」に変更
        default='other'
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