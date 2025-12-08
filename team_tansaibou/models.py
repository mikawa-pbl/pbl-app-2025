from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal
import uuid


class Store(models.Model):
    """模擬店モデル（1店舗 = 1ユーザーアカウント）"""
    # Note: user_id is stored as IntegerField to avoid cross-database FK issues
    # User model is in 'default' DB, Store is in 'team_tansaibou' DB
    user_id = models.IntegerField('ユーザーID', unique=True)
    name = models.CharField('店舗名', max_length=100)
    slug = models.SlugField('識別子', max_length=50, unique=True)
    description = models.TextField('説明', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '店舗'
        verbose_name_plural = '店舗'

    def __str__(self):
        return self.name

    def get_user(self):
        """関連するUserオブジェクトを取得"""
        from django.contrib.auth.models import User
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]
            slug = base_slug
            counter = 1
            while Store.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Member(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='店舗',
        null=True,
        blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Product(models.Model):
    """個別商品"""
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='店舗',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=100,
        verbose_name='商品名'
    )
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='現在価格'
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='在庫数'
    )
    description = models.TextField(
        blank=True,
        verbose_name='説明'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='販売中'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.current_price}円) - 在庫{self.stock}"

    def check_stock(self, quantity):
        """在庫チェック"""
        return self.stock >= quantity


class ProductSet(models.Model):
    """セット商品"""
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='product_sets',
        verbose_name='店舗',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=100,
        verbose_name='セット名'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='セット価格'
    )
    description = models.TextField(
        blank=True,
        verbose_name='説明'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='販売中'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'セット商品'
        verbose_name_plural = 'セット商品'
        ordering = ['name']

    def __str__(self):
        return f"[セット] {self.name} ({self.price}円)"

    def get_total_component_price(self):
        """構成商品の合計価格を計算"""
        return sum(
            item.product.current_price * item.quantity
            for item in self.items.all()
        )

    def get_discount_amount(self):
        """割引額を計算"""
        return self.get_total_component_price() - self.price

    def check_stock(self, quantity):
        """セット在庫チェック（すべての構成商品の在庫を確認）"""
        for item in self.items.all():
            if not item.product.check_stock(item.quantity * quantity):
                return False
        return True

    def get_stock_status(self):
        """在庫状況を取得（最も少ない構成商品から計算）"""
        if not self.items.exists():
            return 0
        return min(
            item.product.stock // item.quantity
            for item in self.items.all()
        )


class ProductSetItem(models.Model):
    """セット構成商品"""
    product_set = models.ForeignKey(
        ProductSet,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='セット商品'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='商品'
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='数量'
    )

    class Meta:
        verbose_name = 'セット構成商品'
        verbose_name_plural = 'セット構成商品'
        unique_together = ['product_set', 'product']

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class PriceHistory(models.Model):
    """価格変更履歴（個別商品とセット商品の両方に対応）"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_history',
        verbose_name='商品'
    )
    product_set = models.ForeignKey(
        ProductSet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='price_history',
        verbose_name='セット商品'
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='変更前価格'
    )
    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='変更後価格'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        verbose_name='変更者'
    )
    reason = models.TextField(
        blank=True,
        verbose_name='変更理由'
    )

    class Meta:
        verbose_name = '価格変更履歴'
        verbose_name_plural = '価格変更履歴'
        ordering = ['-changed_at']

    def clean(self):
        """バリデーション: product と product_set のどちらか一方のみ"""
        if not (bool(self.product) ^ bool(self.product_set)):
            raise ValidationError('商品またはセット商品のどちらか一方を選択してください')

    def __str__(self):
        item = self.product or self.product_set
        return f"{item.name}: {self.old_price}円 → {self.new_price}円"


class Transaction(models.Model):
    """販売取引"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', '現金'),
        ('card', 'カード'),
        ('electronic', '電子マネー'),
        ('other', 'その他'),
    ]

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='店舗',
        null=True,
        blank=True
    )
    transaction_date = models.DateTimeField(
        verbose_name='販売日時'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='合計金額'
    )
    recorded_by = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        verbose_name='担当者'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        verbose_name='支払方法'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='メモ'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '販売取引'
        verbose_name_plural = '販売取引'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['-transaction_date']),
            models.Index(fields=['recorded_by']),
        ]

    def __str__(self):
        return f"{self.transaction_date.strftime('%Y-%m-%d %H:%M')} - {self.total_amount}円"


class TransactionItem(models.Model):
    """取引明細（個別商品とセット商品を区別）"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='取引'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='商品'
    )
    product_set = models.ForeignKey(
        ProductSet,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='セット商品'
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='数量'
    )
    price_at_sale = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='販売時価格'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='小計'
    )

    class Meta:
        verbose_name = '取引明細'
        verbose_name_plural = '取引明細'
        ordering = ['id']

    def clean(self):
        """バリデーション: product と product_set のどちらか一方のみ"""
        if not (bool(self.product) ^ bool(self.product_set)):
            raise ValidationError('商品またはセット商品のどちらか一方を選択してください')

    def __str__(self):
        item = self.product or self.product_set
        return f"{item.name} x{self.quantity}"

    def get_item_name(self):
        """商品名を取得"""
        if self.product:
            return self.product.name
        return f"[セット] {self.product_set.name}"

    def check_and_reduce_stock(self):
        """在庫チェックと減算"""
        if self.product:
            # 個別商品の場合
            if not self.product.check_stock(self.quantity):
                raise ValidationError(
                    f'{self.product.name}の在庫が不足しています。'
                    f'必要: {self.quantity}, 在庫: {self.product.stock}'
                )
            self.product.stock -= self.quantity
            self.product.save()

        elif self.product_set:
            # セット商品の場合
            if not self.product_set.check_stock(self.quantity):
                # 在庫不足の商品を特定
                insufficient_items = []
                for item in self.product_set.items.all():
                    required = item.quantity * self.quantity
                    if item.product.stock < required:
                        insufficient_items.append(
                            f'{item.product.name}(必要: {required}, 在庫: {item.product.stock})'
                        )
                raise ValidationError(
                    f'セット商品の構成商品の在庫が不足しています: {", ".join(insufficient_items)}'
                )

            # 構成商品の在庫を減算
            for item in self.product_set.items.all():
                item.product.stock -= item.quantity * self.quantity
                item.product.save()

    def save(self, *args, **kwargs):
        # 小計を自動計算
        self.subtotal = self.price_at_sale * self.quantity

        # 新規作成時のみ在庫を減算
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            self.check_and_reduce_stock()
