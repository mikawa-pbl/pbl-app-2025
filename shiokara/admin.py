# shiokara/admin.py
from django.contrib import admin
from .models import Department, Company  # Company もあれば一緒に


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name")
    search_fields = ("name", "short_name")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("departments",)  # ManyToMany の場合
