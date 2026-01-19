from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Member, BookReview, SubjectReview, CourseOffering, Teacher, GraphicsUser, Book
from .forms import BookReviewForm, SubjectReviewForm, SignupForm, LoginForm, PasswordResetRequestForm, PasswordResetForm, BookReviewEditForm, SubjectReviewEditForm
from .utils import (
    fetch_book_info_from_openbd,
    get_year_choices,
    get_semester_choices,
    get_all_reviews
)


# ログインチェック用デコレータ
def login_required(view_func):
    """
    ログインが必要なビューに適用するデコレータ
    """
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('graphics_user_id')
        if not user_id:
            messages.warning(request, 'ログインが必要です。')
            return redirect('graphics:login')
        return view_func(request, *args, **kwargs)
    return wrapper   


def index(request):
    # 最近の5件の科目レビューを取得
    recent_subject_reviews = SubjectReview.objects.using('graphics').all().order_by('-created_at')[:5]

    context = {
        'recent_subject_reviews': recent_subject_reviews,
    }

    return render(request, 'teams/graphics/index.html', context)


def members(request):
    qs = Member.objects.using('graphics').all()
    return render(request, 'teams/graphics/members.html', {'members': qs})


@login_required
def add_book_review(request):
    """
    レビュー追加ビュー（科目レビュー・参考書レビュー）
    URLパラメータから科目情報を取得して初期値に設定可能
    """
    # URLパラメータから科目名やcourse_idを取得
    subject_name_param = request.GET.get('subject', '')
    course_id_param = request.GET.get('course_id', '')
    review_type_param = request.GET.get('review_type', 'book')  # デフォルトは書籍レビュー

    book_form = BookReviewForm(initial={'subject': subject_name_param} if subject_name_param else None)

    # 年度と学期の選択肢を取得
    year_choices = get_year_choices()
    semester_choices = get_semester_choices()

    subject_form = SubjectReviewForm()
    subject_form.fields['year'].choices = year_choices
    subject_form.fields['semester'].choices = semester_choices
    if year_choices:
        subject_form.fields['year'].initial = year_choices[0][0]  # 最新年度をデフォルト

    # course_idが指定されている場合、科目名と年度・学期を初期値に設定
    if course_id_param:
        try:
            course = CourseOffering.objects.using('graphics').get(id=course_id_param)
            subject_form.fields['subject_name'].initial = course.subject.name
            subject_form.fields['year'].initial = course.year
            subject_form.fields['semester'].initial = course.semester
        except CourseOffering.DoesNotExist:
            pass

    if request.method == 'POST':
        book_form = BookReviewForm(request.POST)
        if book_form.is_valid():
            # graphicsデータベースに保存
            review = book_form.save(commit=False)

            # ログインユーザーを設定
            user_id = request.session.get('graphics_user_id')
            if user_id:
                review.user_id = user_id

            # ISBNから書籍情報を取得または作成
            if review.isbn:
                isbn = review.isbn

                # 既存の書籍レコードを検索
                try:
                    book = Book.objects.using('graphics').get(isbn=isbn)
                except Book.DoesNotExist:
                    # 書籍が存在しない場合、APIから情報を取得して作成
                    book_info = fetch_book_info_from_openbd(isbn)

                    if book_info:
                        book = Book.objects.using('graphics').create(
                            isbn=isbn,
                            title=book_info.get('title'),
                            author=book_info.get('author'),
                            publication_date=book_info.get('publication_date'),
                            cover_image_url=book_info.get('cover_image_url')
                        )
                    else:
                        # API情報がない場合は空の書籍レコードを作成
                        book = Book.objects.using('graphics').create(isbn=isbn)

                # レビューに書籍を関連付け
                review.book = book

            review.save(using='graphics')
            messages.success(request, '参考書レビューを登録しました。')
            return redirect('graphics:my_reviews')

    context = {
        'book_form': book_form,
        'subject_form': subject_form,
        'review_type': review_type_param,  # レビュータイプをテンプレートに渡す
    }
    return render(request, 'teams/graphics/add_book_review.html', context)


def add_subject_review(request):
    """
    科目レビュー追加ビュー
    """
    if request.method == 'POST':
        # 年度と開講学期の選択肢を取得
        year_choices = get_year_choices()
        semester_choices = get_semester_choices()

        form = SubjectReviewForm(request.POST)
        form.fields['year'].choices = year_choices
        form.fields['semester'].choices = semester_choices

        if form.is_valid():
            subject_name = form.cleaned_data.get('subject_name')
            year = form.cleaned_data.get('year')
            semester = form.cleaned_data.get('semester')

            # 科目名と年度と開講学期からCourseOfferingを取得
            query = CourseOffering.objects.using('graphics').filter(
                subject__name=subject_name
            )

            # 年度が指定されている場合はフィルタ
            if year:
                query = query.filter(year=int(year))

            # 開講学期が指定されている場合はフィルタ
            if semester:
                query = query.filter(semester=semester)

            course_offering = query.first()

            if not course_offering:
                # エラーメッセージを作成
                error_parts = []
                if year:
                    error_parts.append(f'{year}年度')
                if semester:
                    error_parts.append(f'開講学期「{semester}」')
                error_parts.append(f'科目「{subject_name}」')

                error_msg = '、'.join(error_parts) + 'に該当する科目が見つかりませんでした。'
                messages.error(request, error_msg)

                # フォームデータを保持してページを再表示
                book_form = BookReviewForm()
                context = {
                    'book_form': book_form,
                    'subject_form': form,
                }
                return render(request, 'teams/graphics/add_book_review.html', context)

            # graphicsデータベースに保存
            review = form.save(commit=False)
            review.course_offering = course_offering

            # ログインユーザーを設定
            user_id = request.session.get('graphics_user_id')
            if user_id:
                review.user_id = user_id

            review.save(using='graphics')
            messages.success(request, '科目レビューを登録しました。')
            return redirect('graphics:my_reviews')

    # POSTでない場合やバリデーションエラーの場合は、add_book_reviewにリダイレクト
    return redirect('graphics:add_book_review')




@login_required
def search_courses(request):
    """
    科目検索ビュー
    同じ科目名・開講学科・開講学期の科目は統合して表示
    """
    # 検索が実行されたかどうか（GETリクエストが送信されたかどうか）
    # request.GET.keys()をチェックして、フォームが送信されたかを判定
    is_search = len(request.GET) > 0

    # 検索パラメータを取得
    grade = request.GET.get('grade', '')
    department = request.GET.get('department', '')
    semester = request.GET.get('semester', '')
    required = request.GET.get('required', '')
    subject_name = request.GET.get('subject_name', '')
    teacher_name = request.GET.get('teacher_name', '')
    has_review = request.GET.get('has_review', '')

    courses = None
    total_count = 0

    if is_search:
        # 全ての開講情報を取得
        courses = CourseOffering.objects.using('graphics').all()

        # 学年でフィルタ
        if grade and grade != '全体':
            courses = courses.filter(grade__contains=grade)

        # 学科でフィルタ
        if department and department != '全体':
            courses = courses.filter(departments__name=department)

        # 開講学期でフィルタ
        if semester and semester != '全':
            if semester == '通年':
                courses = courses.filter(semester__contains='通年')
            elif semester == '前':
                courses = courses.filter(Q(semester__contains='前期') & ~Q(semester__contains='前期1') & ~Q(semester__contains='前期2'))
            elif semester == '後':
                courses = courses.filter(Q(semester__contains='後期') & ~Q(semester__contains='後期1') & ~Q(semester__contains='後期2'))
            elif semester == '前1':
                courses = courses.filter(semester__contains='前期1')
            elif semester == '前2':
                courses = courses.filter(semester__contains='前期2')
            elif semester == '後1':
                courses = courses.filter(semester__contains='後期1')
            elif semester == '後2':
                courses = courses.filter(semester__contains='後期2')

        # 選択必修でフィルタ
        if required and required != '全体':
            if required == '必修':
                courses = courses.filter(is_required=True)
            else:  # 選択 or 選必修
                courses = courses.filter(is_required=False)

        # 科目名でフィルタ
        if subject_name:
            courses = courses.filter(subject__name__icontains=subject_name)

        # 教員名でフィルタ
        if teacher_name:
            courses = courses.filter(teachers__name__icontains=teacher_name)

        # 重複を除去
        courses = courses.distinct()

        # 科目を統合: 科目名・開講学科・開講学期が同じものを1つにまとめる
        unified_courses = {}
        for course in courses:
            # 学科名のリストを取得してソート（一意なキーを作るため）
            dept_names = sorted([dept.name for dept in course.departments.all()])
            dept_key = ','.join(dept_names)

            # 一意なキー: 科目名 + 学科 + 学期
            unique_key = f"{course.subject.name}|{dept_key}|{course.semester}"

            if unique_key not in unified_courses:
                # 最新年度の情報を代表として使用
                unified_courses[unique_key] = course
            else:
                # より新しい年度があれば更新
                if course.year > unified_courses[unique_key].year:
                    unified_courses[unique_key] = course

        # 各コースに学科数、平均評価、レビュー数を追加
        courses_with_ratings = []
        for unique_key, course in unified_courses.items():
            course.dept_count = course.departments.count()

            # この科目の全年度のレビューを集計
            # 科目名・学科・学期が同じすべてのCourseOfferingのレビューを取得
            dept_names = sorted([dept.name for dept in course.departments.all()])
            same_courses = CourseOffering.objects.using('graphics').filter(
                subject__name=course.subject.name,
                semester=course.semester
            )
            # 学科も一致するものだけ
            for sc in same_courses:
                sc_dept_names = sorted([dept.name for dept in sc.departments.all()])
                if sc_dept_names != dept_names:
                    same_courses = same_courses.exclude(id=sc.id)

            # 科目レビューの平均評価とレビュー数を計算（全年度分）
            subject_reviews = SubjectReview.objects.using('graphics').filter(
                course_offering__in=same_courses
            )
            review_count = subject_reviews.count()
            course.review_count = review_count

            if review_count > 0:
                # 平均評価を計算
                total_rating = sum(review.rating for review in subject_reviews)
                course.avg_rating = total_rating / review_count
            else:
                course.avg_rating = 0

            # 評価があるもののみを表示フィルタ
            if has_review:
                if review_count > 0:
                    courses_with_ratings.append(course)
            else:
                courses_with_ratings.append(course)

        # フィルタ適用後のコースリストを使用
        courses = courses_with_ratings
        total_count = len(courses_with_ratings)

        # ページネーション (1ページあたり10件)
        paginator = Paginator(courses, 10)
        page = request.GET.get('page', 1)

        try:
            courses = paginator.page(page)
        except PageNotAnInteger:
            # ページ番号が整数でない場合、最初のページを表示
            courses = paginator.page(1)
        except EmptyPage:
            # ページ番号が範囲外の場合、最後のページを表示
            courses = paginator.page(paginator.num_pages)
    else:
        total_count = 0

    context = {
        'courses': courses,
        'total_count': total_count,
        'is_search': is_search,
        # 検索条件を保持
        'search_params': {
            'grade': grade,
            'department': department,
            'semester': semester,
            'required': required,
            'subject_name': subject_name,
            'teacher_name': teacher_name,
            'has_review': has_review,
        }
    }

    return render(request, 'teams/graphics/search_courses.html', context)


def teacher_autocomplete(request):
    """
    教員名のオートコンプリートAPI
    """
    query = request.GET.get('q', '')
    if query:
        teachers = Teacher.objects.using('graphics').filter(name__icontains=query).values_list('name', flat=True)[:10]
        return JsonResponse({'teachers': list(teachers)})
    return JsonResponse({'teachers': []})


def subject_autocomplete(request):
    """
    科目名のオートコンプリートAPI
    """
    query = request.GET.get('q', '')
    if query:
        from .models import Subject
        subjects = Subject.objects.using('graphics').filter(name__icontains=query).values_list('name', flat=True)[:10]
        return JsonResponse({'subjects': list(subjects)})
    return JsonResponse({'subjects': []})


def isbn_lookup(request):
    """
    ISBN検索API
    ISBNコードから書籍情報を取得
    """
    isbn = request.GET.get('isbn', '')
    if not isbn:
        return JsonResponse({'success': False, 'error': 'ISBNを入力してください'})

    # ハイフンを除去
    isbn = isbn.replace('-', '')

    # ISBNのバリデーション
    if len(isbn) != 13 or not isbn.isdigit():
        return JsonResponse({'success': False, 'error': 'ISBNコードは13桁の数字で入力してください'})

    # OpenBD APIから情報を取得
    book_info = fetch_book_info_from_openbd(isbn)

    if book_info:
        return JsonResponse({
            'success': True,
            'title': book_info.get('title'),
            'author': book_info.get('author'),
            'publication_date': book_info.get('publication_date'),
            'cover_image_url': book_info.get('cover_image_url')
        })
    else:
        return JsonResponse({'success': False, 'error': '書籍情報が見つかりませんでした'})


def signup(request):
    """
    サインアップビュー
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'アカウントを作成しました。ログインしてください。')
            return redirect('graphics:login')
    else:
        form = SignupForm()

    return render(request, 'teams/graphics/signup.html', {'form': form})


def login(request):
    """
    ログインビュー
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email_prefix = form.cleaned_data['email_prefix'].strip().lower()
            password = form.cleaned_data['password']

            # 完全なメールアドレスを生成
            email = f"{email_prefix}@tut.jp"

            try:
                user = GraphicsUser.objects.using('graphics').get(email__iexact=email)

                if user.check_password(password):
                    # セッションにユーザーIDを保存
                    request.session['graphics_user_id'] = user.user_id
                    request.session['graphics_user_nickname'] = user.nickname
                    messages.success(request, f'ようこそ、{user.nickname}さん！')
                    return redirect('graphics:index')
                else:
                    messages.error(request, 'メールアドレスまたはパスワードが間違っています。')
            except GraphicsUser.DoesNotExist:
                messages.error(request, 'メールアドレスまたはパスワードが間違っています。')
    else:
        form = LoginForm()

    return render(request, 'teams/graphics/login.html', {'form': form})


def logout(request):
    """
    ログアウトビュー
    """
    request.session.pop('graphics_user_id', None)
    request.session.pop('graphics_user_nickname', None)
    messages.success(request, 'ログアウトしました。')
    return redirect('graphics:index')


def course_detail_legacy(request, course_id):
    """
    旧URL用の科目詳細ビュー（後方互換性）
    course_idから新URLへリダイレクト
    """
    from urllib.parse import quote
    try:
        course = CourseOffering.objects.using('graphics').get(id=course_id)
        # 新URLへリダイレクト
        return redirect('graphics:course_detail',
                       subject_name=quote(course.subject.name),
                       semester=quote(course.semester))
    except CourseOffering.DoesNotExist:
        messages.error(request, '科目が見つかりませんでした。')
        return redirect('graphics:search_courses')


def course_detail(request, subject_name, semester):
    """
    科目詳細ページ
    科目名と開講学期から科目を特定し、最新年度の情報を表示
    過去年度の担当教員情報も表示
    """
    from urllib.parse import unquote

    # URLエンコードされた科目名をデコード
    subject_name = unquote(subject_name)
    semester = unquote(semester)

    # 科目名と学期から該当する全年度の開講情報を取得
    courses = CourseOffering.objects.using('graphics').filter(
        subject__name=subject_name,
        semester=semester
    ).order_by('-year')  # 新しい年度順

    if not courses.exists():
        messages.error(request, '科目が見つかりませんでした。')
        return redirect('graphics:search_courses')

    # 最新年度の情報を代表として使用
    latest_course = courses.first()

    # 過去年度の担当教員情報を収集
    past_teachers_by_year = []
    for course in courses:
        if course.id != latest_course.id:
            teachers = course.teachers.all()
            teacher_names = ', '.join([teacher.name for teacher in teachers])
            past_teachers_by_year.append({
                'year': course.year,
                'teachers': teacher_names
            })

    # この科目の全年度のレビューを取得
    subject_reviews_qs = SubjectReview.objects.using('graphics').filter(
        course_offering__in=courses
    ).order_by('-created_at')

    # ページネーション（科目レビュー）
    subject_paginator = Paginator(subject_reviews_qs, 5)
    subject_page = request.GET.get('subject_page', 1)
    try:
        subject_reviews = subject_paginator.page(subject_page)
    except PageNotAnInteger:
        subject_reviews = subject_paginator.page(1)
    except EmptyPage:
        subject_reviews = subject_paginator.page(subject_paginator.num_pages)

    # この科目に関連する参考書レビューを取得
    book_reviews = BookReview.objects.using('graphics').filter(
        subject=latest_course.subject.name
    ).order_by('-created_at')

    # 書籍ごとにグループ化
    books_dict = {}
    for review in book_reviews:
        if review.book:
            isbn = review.book.isbn
            if isbn not in books_dict:
                books_dict[isbn] = {
                    'book': review.book,
                    'review_count': 0,
                    'avg_rating': 0,
                    'total_rating': 0,
                }
            books_dict[isbn]['review_count'] += 1
            # rating が 0 以上の場合のみ集計（スター未選択を除外）
            if review.rating > 0:
                books_dict[isbn]['total_rating'] += review.rating

    # 平均評価を計算
    books_with_reviews = []
    for isbn, data in books_dict.items():
        data['avg_rating'] = data['total_rating'] / data['review_count'] if data['review_count'] > 0 else 0
        books_with_reviews.append(data)

    # ページネーション（参考書）
    books_paginator = Paginator(books_with_reviews, 5)
    books_page = request.GET.get('books_page', 1)
    try:
        books_with_reviews_paginated = books_paginator.page(books_page)
    except PageNotAnInteger:
        books_with_reviews_paginated = books_paginator.page(1)
    except EmptyPage:
        books_with_reviews_paginated = books_paginator.page(books_paginator.num_pages)

    # 担当教員のリストを取得（最新年度）
    teachers = latest_course.teachers.all()
    teacher_names = ', '.join([teacher.name for teacher in teachers])

    # 学科のリストを取得
    departments = latest_course.departments.all()
    department_names = ', '.join([dept.name for dept in departments])

    context = {
        'course': latest_course,
        'teacher_names': teacher_names,
        'department_names': department_names,
        'past_teachers_by_year': past_teachers_by_year,  # 過去年度の担当教員
        'subject_reviews': subject_reviews,
        'books_with_reviews': books_with_reviews_paginated,
        'subject_reviews_count': subject_reviews_qs.count(),
        'books_count': len(books_with_reviews),
    }

    return render(request, 'teams/graphics/course_detail.html', context)






def book_detail(request, isbn):
    """
    書籍詳細ページ
    特定の書籍に対する全レビューを表示
    """
    # 遷移元のcourse_idを取得
    course_id = request.GET.get('course_id', None)

    try:
        book = Book.objects.using('graphics').get(isbn=isbn)
    except Book.DoesNotExist:
        messages.error(request, '書籍が見つかりませんでした。')
        return redirect('graphics:book_review_list')

    # この書籍に対するレビューを取得
    reviews_qs = BookReview.objects.using('graphics').filter(book=book).order_by('-created_at')

    # 平均評価を計算（rating > 0 のレビューのみ）
    total_rating = 0
    rating_count = 0
    for review in reviews_qs:
        if review.rating > 0:
            total_rating += review.rating
            rating_count += 1
    avg_rating = total_rating / rating_count if rating_count > 0 else 0

    # ページネーション（参考書レビュー）
    paginator = Paginator(reviews_qs, 5)
    page = request.GET.get('page', 1)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    context = {
        'book': book,
        'reviews': reviews,
        'reviews_count': reviews_qs.count(),
        'avg_rating': avg_rating,
        'course_id': course_id,  # 遷移元のcourse_idをテンプレートに渡す
    }

    return render(request, 'teams/graphics/book_detail.html', context)


@login_required
def my_reviews(request):
    """
    自分の投稿したレビュー一覧
    書籍レビューと科目レビューを分けて表示し、それぞれページネーション
    """
    user_id = request.session.get('graphics_user_id')

    # ユーザーが投稿したレビューを取得
    book_reviews_qs = BookReview.objects.using('graphics').filter(user_id=user_id).order_by('-created_at')
    subject_reviews_qs = SubjectReview.objects.using('graphics').filter(user_id=user_id).order_by('-created_at')

    # 書籍レビューのページネーション
    book_paginator = Paginator(book_reviews_qs, 5)
    book_page = request.GET.get('book_page', 1)
    try:
        book_reviews = book_paginator.page(book_page)
    except PageNotAnInteger:
        book_reviews = book_paginator.page(1)
    except EmptyPage:
        book_reviews = book_paginator.page(book_paginator.num_pages)

    # 科目レビューのページネーション
    subject_paginator = Paginator(subject_reviews_qs, 5)
    subject_page = request.GET.get('subject_page', 1)
    try:
        subject_reviews = subject_paginator.page(subject_page)
    except PageNotAnInteger:
        subject_reviews = subject_paginator.page(1)
    except EmptyPage:
        subject_reviews = subject_paginator.page(subject_paginator.num_pages)

    context = {
        'book_reviews': book_reviews,
        'subject_reviews': subject_reviews,
        'book_reviews_count': book_reviews_qs.count(),
        'subject_reviews_count': subject_reviews_qs.count(),
    }

    return render(request, 'teams/graphics/my_reviews.html', context)


@login_required
def edit_book_review(request, review_id):
    """
    参考書レビュー編集ビュー
    """
    user_id = request.session.get('graphics_user_id')

    try:
        review = BookReview.objects.using('graphics').get(id=review_id, user_id=user_id)
    except BookReview.DoesNotExist:
        messages.error(request, 'レビューが見つからないか、編集権限がありません。')
        return redirect('graphics:my_reviews')

    if request.method == 'POST':
        form = BookReviewEditForm(request.POST, instance=review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.save(using='graphics')
            messages.success(request, '参考書レビューを更新しました。')
            return redirect('graphics:my_reviews')
    else:
        form = BookReviewEditForm(instance=review)

    context = {
        'form': form,
        'review': review,
        'review_type': 'book'
    }
    return render(request, 'teams/graphics/edit_review.html', context)


@login_required
def edit_subject_review(request, review_id):
    """
    科目レビュー編集ビュー
    """
    user_id = request.session.get('graphics_user_id')

    try:
        review = SubjectReview.objects.using('graphics').get(id=review_id, user_id=user_id)
    except SubjectReview.DoesNotExist:
        messages.error(request, 'レビューが見つからないか、編集権限がありません。')
        return redirect('graphics:my_reviews')

    if request.method == 'POST':
        form = SubjectReviewEditForm(request.POST, instance=review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.save(using='graphics')
            messages.success(request, '科目レビューを更新しました。')
            return redirect('graphics:my_reviews')
    else:
        form = SubjectReviewEditForm(instance=review)

    context = {
        'form': form,
        'review': review,
        'review_type': 'subject'
    }
    return render(request, 'teams/graphics/edit_review.html', context)