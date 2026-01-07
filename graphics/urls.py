from django.urls import path
from . import views

app_name = "graphics"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    # 旧レビュー一覧（後方互換性のため残す）
    path('book-reviews/', views.book_reviews, name='book_reviews'),
    # 新しいレビュー関連URL
    path('subject-reviews/', views.subject_review_list, name='subject_review_list'),
    path('book-reviews-list/', views.book_review_list, name='book_review_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('book/<str:isbn>/', views.book_detail, name='book_detail'),
    # レビュー追加
    path('book-reviews/add/', views.add_book_review, name='add_book_review'),
    path('subject-reviews/add/', views.add_subject_review, name='add_subject_review'),
    # 科目検索
    path('search/', views.search_courses, name='search_courses'),
    # API
    path('api/teacher-autocomplete/', views.teacher_autocomplete, name='teacher_autocomplete'),
    path('api/subject-autocomplete/', views.subject_autocomplete, name='subject_autocomplete'),
    path('api/isbn-lookup/', views.isbn_lookup, name='isbn_lookup'),
    # 認証
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]