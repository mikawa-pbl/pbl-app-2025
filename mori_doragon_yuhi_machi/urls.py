# (あなたのアプリ名)/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('places/add/', views.add_place, name='add_place'), 
    path('places/delete/', views.delete_place, name='delete_place'), 
    path('add_member/', views.add_member, name='add_member'),
    path('delete_member/', views.delete_member, name='delete_member'),
    path('reset_to_home/', views.reset_to_home, name='reset_to_home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
