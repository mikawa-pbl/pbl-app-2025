from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Member, BookReview
from .forms import BookReviewForm
from .utils import fetch_book_info_from_openbd


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

            # ISBNから書籍情報を取得
            isbn = review.isbn
            book_info = fetch_book_info_from_openbd(isbn)

            if book_info:
                review.title = book_info.get('title')
                review.author = book_info.get('author')
                review.publication_date = book_info.get('publication_date')

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