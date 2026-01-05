from django.contrib import admin
from .models import Member, Product, GiryulinkUser

# Register your models here.

@admin.register(GiryulinkUser)
class GiryulinkUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'created_at')
    search_fields = ('email', 'name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'user', 'image')
    search_fields = ('title', 'description')
    list_filter = ('user',)
    ordering = ('-id',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')

