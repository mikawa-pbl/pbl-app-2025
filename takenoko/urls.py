from django.urls import path
from . import views

app_name = "takenoko"
urlpatterns = [
    path('', views.main, name='main'),
    path('members/', views.members, name='members'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('item_create/', views.item_create, name='item_create'),
    path('product_details/', views.product_details, name='product_details'),
    path('purchased_items/', views.purchased_items, name='purchased_items'),
    path('listing_items/', views.listing_items, name='listing_items'),
    path('create_complete/', views.create_complete, name='create_complete'),
    path('start_trading/', views.start_trading, name='start_trading'),
    path('item_delete/', views.item_delete, name='item_delete'),
    path('item_edit/', views.item_edit, name='item_edit'),
    path('edit_complete/', views.edit_complete, name='edit_complete'),
]