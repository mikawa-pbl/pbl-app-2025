# (あなたのアプリ名)/urls.py

from django.urls import path
from . import views

# app_name を設定すると、redirect() などで 'app_name:url_name' という名前が使えて便利
app_name = 'mori_doragon_yuhi_machi'

urlpatterns = [
    # http://.../(アプリのURL)/
    path('', views.index, name='index'), 
    
    # http://.../(アプリのURL)/members/
    path('members/', views.members, name='members'), 
    
    # http://.../(アプリのURL)/update_location/
    # (このURLにフォームが送信される)
    path('update_location/', views.update_location, name='update_location'), 
]