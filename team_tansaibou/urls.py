from django.urls import path

from . import views
from . import api_views

app_name = "team_tansaibou"
urlpatterns = [
    # 認証
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # レジ画面（ホーム）
    path('', views.register_sale, name='index'),
    path('register/', views.register_sale, name='register_sale'),

    # 販売関連
    path('sales/', views.sale_list, name='sale_list'),

    # 商品管理
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/restock/', views.product_restock, name='product_restock'),

    # セット商品管理
    path('product-sets/', views.productset_list, name='productset_list'),
    path('product-sets/add/', views.productset_add, name='productset_add'),
    path('product-sets/<int:productset_id>/edit/', views.productset_edit, name='productset_edit'),

    # 担当者管理
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_add, name='member_add'),
    path('members/<int:member_id>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:member_id>/delete/', views.member_delete, name='member_delete'),

    # ダッシュボードAPI
    path('api/dashboard/today-sales/', api_views.today_sales, name='api_today_sales'),
    path('api/dashboard/hourly-stats/', api_views.hourly_stats, name='api_hourly_stats'),
    path('api/dashboard/yearly-comparison/', api_views.yearly_comparison, name='api_yearly_comparison'),
    path('api/dashboard/daily-comparison/', api_views.daily_comparison, name='api_daily_comparison'),
    path('api/dashboard/product-ranking/', api_views.product_ranking, name='api_product_ranking'),
    path('api/dashboard/stock-prediction/', api_views.stock_prediction, name='api_stock_prediction'),
]
