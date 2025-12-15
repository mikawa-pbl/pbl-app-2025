from django.contrib import admin
from .models import Tag, Post

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "end_date", "created_at")
    list_filter = ("date", "end_date", "tags")
    search_fields = ("title", "body")
