from django.contrib import admin
from .models import Paper

# Register your models here.

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'booktitle', 'url', 'doi')
    search_fields = ('title', 'author', 'booktitle', 'year')
    list_filter = ('year', 'booktitle')