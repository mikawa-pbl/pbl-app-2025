from django.urls import path
from . import views

app_name = "graphics"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('book-reviews/', views.book_reviews, name='book_reviews'),
    path('book-reviews/add/', views.add_book_review, name='add_book_review'),
    path('subject-reviews/add/', views.add_subject_review, name='add_subject_review'),
    path('search/', views.search_courses, name='search_courses'),
    path('api/teacher-autocomplete/', views.teacher_autocomplete, name='teacher_autocomplete'),
    path('api/subject-autocomplete/', views.subject_autocomplete, name='subject_autocomplete'),
    path('api/isbn-lookup/', views.isbn_lookup, name='isbn_lookup'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]