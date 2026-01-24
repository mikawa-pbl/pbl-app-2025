from django.contrib import admin
from .models import Member, Product, ProductSet, ProductSetItem, PriceHistory, Transaction, TransactionItem

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'email', 'store']
    search_fields = ['name', 'student_id', 'email']
    list_filter = ['store']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'current_price', 'description')
        }),
        ('在庫・状態', {
            'fields': ('stock', 'is_active')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


class ProductSetItemInline(admin.TabularInline):
    model = ProductSetItem
    extra = 1
    fields = ['product', 'quantity']


@admin.register(ProductSet)
class ProductSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'get_discount', 'get_available_stock', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_total_price', 'get_discount']
    inlines = [ProductSetItemInline]
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'price', 'description')
        }),
        ('価格情報', {
            'fields': ('get_total_price', 'get_discount'),
            'classes': ['collapse']
        }),
        ('状態', {
            'fields': ('is_active',)
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    def get_total_price(self, obj):
        """構成商品の合計価格"""
        if obj.pk:
            return f"{obj.get_total_component_price()}円"
        return "-"
    get_total_price.short_description = '構成商品合計価格'

    def get_discount(self, obj):
        """割引額"""
        if obj.pk:
            discount = obj.get_discount_amount()
            return f"{discount}円 ({discount / obj.get_total_component_price() * 100:.1f}%)" if obj.get_total_component_price() > 0 else "0円"
        return "-"
    get_discount.short_description = '割引額'

    def get_available_stock(self, obj):
        """販売可能数"""
        if obj.pk:
            return f"{obj.get_stock_status()}セット"
        return "-"
    get_available_stock.short_description = '販売可能数'


@admin.register(ProductSetItem)
class ProductSetItemAdmin(admin.ModelAdmin):
    list_display = ['product_set', 'product', 'quantity']
    list_filter = ['product_set']
    search_fields = ['product_set__name', 'product__name']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['get_item_name', 'old_price', 'new_price', 'changed_at', 'changed_by']
    list_filter = ['changed_at', 'changed_by']
    search_fields = ['product__name', 'product_set__name', 'reason']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'

    def get_item_name(self, obj):
        """商品名またはセット名を取得"""
        if obj.product:
            return obj.product.name
        return f"[セット] {obj.product_set.name}"
    get_item_name.short_description = '商品/セット'


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 1
    fields = ['product', 'product_set', 'quantity', 'price_at_sale', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_date', 'total_amount', 'recorded_by', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'recorded_by', 'transaction_date']
    search_fields = ['notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'transaction_date'
    inlines = [TransactionItemInline]
    fieldsets = (
        ('取引情報', {
            'fields': ('transaction_date', 'total_amount', 'payment_method')
        }),
        ('担当・メモ', {
            'fields': ('recorded_by', 'notes')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'get_item_name', 'quantity', 'price_at_sale', 'subtotal']
    list_filter = ['product', 'product_set', 'transaction__transaction_date']
    search_fields = ['product__name', 'product_set__name', 'transaction__notes']
    readonly_fields = ['subtotal']

    def get_item_name(self, obj):
        """商品名を取得"""
        return obj.get_item_name()
    get_item_name.short_description = '商品/セット'
