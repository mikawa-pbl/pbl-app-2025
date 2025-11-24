# shiokara/urls.py
from django.urls import path
from . import views

app_name = "shiokara"

urlpatterns = [
    path("", views.department_list, name="department_list"),
    path("departments/<str:short_name>/",
         views.department_detail, name="department_detail"),
    path("search/", views.company_search, name="company_search"),
]
