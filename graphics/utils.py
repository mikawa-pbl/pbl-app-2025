"""
Utility functions for graphics app
"""

import urllib.request
import json
import re
from .models import CourseOffering


def format_author_name(author_raw):
    """
    Format author name by removing birth year and replacing commas with spaces

    Args:
        author_raw (str): Raw author name (e.g., "斎藤,康毅,1984-")

    Returns:
        str: Formatted author name (e.g., "斎藤 康毅")
    """
    if not author_raw:
        return None

    # Remove birth year pattern (e.g., "1984-")
    author = re.sub(r',?\s*\d{4}-?\s*', '', author_raw)

    # Replace commas with spaces
    author = author.replace(',', ' ')

    # Remove extra spaces
    author = ' '.join(author.split())

    return author if author else None


def format_publication_date(pubdate_raw):
    """
    Format publication date from YYYYMM to YYYY年MM月

    Args:
        pubdate_raw (str): Raw publication date (e.g., "202404")

    Returns:
        str: Formatted date (e.g., "2024年04月") or None
    """
    if not pubdate_raw:
        return None

    # Expected format: YYYYMM
    if len(pubdate_raw) >= 6 and pubdate_raw[:6].isdigit():
        year = pubdate_raw[:4]
        month = pubdate_raw[4:6]
        return f"{year}年{month}月"

    return None


def fetch_book_info_from_openbd(isbn):
    """
    Fetch book information from OpenBD API

    Args:
        isbn (str): ISBN code

    Returns:
        dict: Book information (title, author, publication_date) or None
    """
    url = f"https://api.openbd.jp/v1/get?isbn={isbn}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

            if data and data[0]:
                book_data = data[0]

                # Get title
                title = None
                if 'summary' in book_data and 'title' in book_data['summary']:
                    title = book_data['summary']['title']

                # Get author and format it
                author = None
                if 'summary' in book_data and 'author' in book_data['summary']:
                    author_raw = book_data['summary']['author']
                    author = format_author_name(author_raw)

                # Get publication date and format it
                publication_date = None
                if 'summary' in book_data and 'pubdate' in book_data['summary']:
                    pubdate_raw = book_data['summary']['pubdate']
                    publication_date = format_publication_date(pubdate_raw)

                return {
                    'title': title,
                    'author': author,
                    'publication_date': publication_date
                }
            else:
                return None

    except Exception as e:
        # Return None if error occurs
        print(f"OpenBD API Error: {e}")
        return None


def get_year_choices():
    """
    Get year choices for forms

    Returns:
        list: List of tuples (year, display_name)
    """
    years = CourseOffering.objects.using('graphics').values_list('year', flat=True).distinct().order_by('-year')
    return [(year, f'{year}年度') for year in years]


def get_semester_choices():
    """
    Get semester choices for forms with filtering and display name mapping

    Returns:
        list: List of tuples (semester, display_name)
    """
    semesters = CourseOffering.objects.using('graphics').values_list('semester', flat=True).distinct().order_by('semester')

    # 除外する学期と表示名の変更
    exclude_semesters = ['2年通年', '前2＋後1', '前期＋後1']
    display_names = {
        '前期1': '前1',
        '前期2': '前2',
        '後期1': '後1',
        '後期2': '後2',
    }

    semester_choices = []
    for sem in semesters:
        if sem not in exclude_semesters:
            display_name = display_names.get(sem, sem)
            semester_choices.append((sem, display_name))

    return semester_choices


def format_review_data(review, review_type='book'):
    """
    Format review data for display

    Args:
        review: BookReview or SubjectReview instance
        review_type: 'book' or 'subject'

    Returns:
        dict: Formatted review data
    """
    if review_type == 'book':
        return {
            'type': 'book',
            'subject': review.subject,
            'isbn': review.isbn,
            'title': review.title,
            'author': review.author,
            'publication_date': review.publication_date,
            'review': review.review,
            'rating': review.rating,
            'created_at': review.created_at,
        }
    else:  # subject
        teachers = review.course_offering.teachers.all()
        teacher_names = ', '.join([teacher.name for teacher in teachers])

        return {
            'type': 'subject',
            'subject': review.course_offering.subject.name,
            'year': review.course_offering.year,
            'semester': review.course_offering.semester,
            'course_info': f"{review.course_offering.year}年度 {review.course_offering.semester} {review.course_offering.grade}",
            'teachers': teacher_names,
            'review': review.review,
            'rating': review.rating,
            'created_at': review.created_at,
        }


def get_all_reviews(book_reviews, subject_reviews):
    """
    Combine and sort book reviews and subject reviews

    Args:
        book_reviews: QuerySet of BookReview
        subject_reviews: QuerySet of SubjectReview

    Returns:
        list: Sorted list of formatted reviews
    """
    all_reviews = []

    # 参考書レビューをリストに追加（subjectが空でないもののみ）
    for review in book_reviews:
        if review.subject:
            all_reviews.append(format_review_data(review, 'book'))

    # 科目レビューをリストに追加
    for review in subject_reviews:
        all_reviews.append(format_review_data(review, 'subject'))

    # 作成日時でソート（新しい順）
    all_reviews.sort(key=lambda x: x['created_at'], reverse=True)

    return all_reviews
