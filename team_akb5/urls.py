from django.urls import path
from . import views
from .views import UserView, AdminView, StatusReportCreateView

app_name = "team_akb5"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('admin/', AdminView.as_view(), name='admin'),
    path('user/', UserView.as_view(), name='user'),
    path('status_report_form/', StatusReportCreateView.as_view(), name='status_report_form'),
]
