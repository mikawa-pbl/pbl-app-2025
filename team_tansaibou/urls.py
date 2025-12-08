from django.urls import path

from . import views

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

    # その他
    path('members/', views.members, name='members'),
]
