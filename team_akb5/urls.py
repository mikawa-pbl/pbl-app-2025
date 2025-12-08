from django.urls import path
from . import views
from .views import StatusReportListView, StatusReportCreateView

app_name = "team_akb5"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('status_list/', StatusReportListView.as_view(), name='status_list'),
    path('status_report_form/', StatusReportCreateView.as_view(), name='status_report_form'),
]
