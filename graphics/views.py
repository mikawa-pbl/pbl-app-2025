from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Member, BookReview
from .forms import BookReviewForm


def index(request):
    return render(request, 'teams/graphics/index.html')


def members(request):
    qs = Member.objects.using('graphics').all()
    return render(request, 'teams/graphics/members.html', {'members': qs})


def add_book_review(request):
    """
    参考書レビュー追加ビュー
    """
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            # graphicsデータベースに保存
            review = form.save(commit=False)
            review.save(using='graphics')
            messages.success(request, '参考書レビューを登録しました。')
            return redirect('graphics:book_reviews')
    else:
        form = BookReviewForm()

    return render(request, 'teams/graphics/add_book_review.html', {'form': form})


def book_reviews(request):
    """
    参考書レビュー一覧ビュー
    """
    reviews = BookReview.objects.using('graphics').all()
    return render(request, 'teams/graphics/book_reviews.html', {'reviews': reviews})