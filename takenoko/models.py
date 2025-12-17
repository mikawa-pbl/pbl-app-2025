from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from uuid import uuid4
import os
from datetime import datetime

# アバター画像のファイル名を生成する関数
def avatar_upload_path(instance, filename):
    """
    アバター画像の保存パスとファイル名を生成
    形式: takenoko/avatars/{user_id}_{timestamp}.{拡張子}
    例: takenoko/avatars/abc123_20231217_143052.jpg
    """
    ext = os.path.splitext(filename)[1].lower()  # 拡張子を取得（.jpg など）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{instance.user_id}_{timestamp}{ext}"
    return os.path.join('takenoko', 'avatars', new_filename)

# --- ユーザー情報 ---
class TakenokoUser(models.Model):
    user_id = models.CharField("ユーザーID", max_length=50, unique=True, primary_key=True, default=uuid4, editable=False)
    email = models.EmailField("メールアドレス", unique=True)
    password = models.CharField("パスワードハッシュ", max_length=128)

    # プロフィール
    avatar = models.ImageField("ユーザーアイコン", upload_to=avatar_upload_path, blank=True, null=True)
    nickname = models.CharField("ニックネーム", max_length=50)
    student_id = models.CharField("学籍番号", max_length=20, unique=True, default='unknown')
    MAJOR_CHOICES = [
        ('1st', '機械工学系'),
        ('2nd', '電気・電子情報工学系'),
        ('3rd', '情報・知能工学系'),
        ('4th', '応用化学・生命工学系'),
        ('5th', '建築都市システム学系'),
        ('other', '未配属・その他'),
    ]
    major = models.CharField("専攻", max_length=50, choices=MAJOR_CHOICES, default='other')
    GRADE_CHOICES = [
        ('b1', '学部1年'),
        ('b2', '学部2年'),
        ('b3', '学部3年'),
        ('b4', '学部4年'),
        ('m1', '修士1年'),
        ('m2', '修士2年'),
        ('d',  '博士課程'),
        ('other', 'その他'),
    ]
    grade = models.CharField("学年", max_length=10, choices=GRADE_CHOICES, default='b1')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'takenoko_users'
        verbose_name = 'Takenoko User'
        verbose_name_plural = 'Takenoko Users'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.nickname} ({self.user_id})"


# --- アイテムタグ ---
# タグの追加・編集はDjangoシェルで行うことを想定
# 例:
# uv run python manage.py shell
# >>> from takenoko.models import Tag
# タグを追加---------------------------------
# >>> Tag.objects.create(name='textbook', display_name='教科書')
# タグを削除---------------------------------
# >>> Tag.objects.get(name='textbook').delete()
# 登録したタグの確認-----------------------------
# >>> Tag.objects.all()
class Tag(models.Model):
    name = models.CharField("タグ名", max_length=50, unique=True, primary_key=True)
    display_name = models.CharField("表示名", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ"
    
    def __str__(self):
        return self.display_name


# --- アイテム情報（Item） ---
class Item(models.Model):
    # 状態の選択肢
    CONDITION_CHOICES = [
        ('new', '新品・未使用'),
        ('good', '目立った傷なし'),
        ('bad', '傷や汚れあり'),
    ]

    # 取引状況の選択肢
    STATUS_CHOICES = [
        ('active', '出品中'),
        ('negotiation', '交渉中'),
        ('sold', '売り切れ'),
    ]

    # 対象学年の選択肢
    TARGET_GRADE_CHOICES = [
        ('all', '全学年向け'),
        ('b1', '学部1年向け'),
        ('b2', '学部2年向け'),
        ('b3', '学部3年向け'),
        ('b4', '学部4年向け'),
        ('m1', '修士1年向け'),
        ('m2', '修士2年向け'),
        ('d', '博士課程向け'),
    ]

    # --- 基本情報 ---
    name = models.CharField("商品名", max_length=100)
    image = models.ImageField("商品画像", upload_to='takenoko/items/', blank=True, null=True)
    price = models.PositiveIntegerField("値段")
    description = models.TextField("説明文", blank=True)
    
    # --- 商品の属性 ---
    condition = models.CharField("状態", max_length=10, choices=CONDITION_CHOICES, default='good')
    target_grade = models.CharField("対象学年", max_length=10, choices=TARGET_GRADE_CHOICES, default='all')
    tags = models.ManyToManyField(Tag, related_name='items', verbose_name="タグ/カテゴリ", blank=True)

    # --- システム管理用 ---
    status = models.CharField("取引状況", max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField("出品日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    sold_at = models.DateTimeField("成約日時", null=True, blank=True)

    # --- ユーザーとの紐付け ---
    seller = models.ForeignKey(TakenokoUser, on_delete=models.CASCADE, related_name='sold_items', verbose_name="出品者")
    buyer = models.ForeignKey(TakenokoUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='bought_items', verbose_name="購入者")

    class Meta:
        ordering = ['-created_at']  # 新しい順に表示
        verbose_name = "商品"
        verbose_name_plural = "商品"
    
    def __str__(self):
        return f"{self.name} - {self.price}"