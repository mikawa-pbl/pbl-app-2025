from django.urls import path
from . import views

app_name = "graphics"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
    path('book-reviews/', views.book_reviews, name='book_reviews'),
    path('book-reviews/add/', views.add_book_review, name='add_book_review'),
]