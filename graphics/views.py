from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Member, BookReview, SubjectReview, CourseOffering, Teacher
from .forms import BookReviewForm, SubjectReviewForm
from .utils import fetch_book_info_from_openbd   


def index(request):
    return render(request, 'teams/graphics/index.html')


def members(request):
    qs = Member.objects.using('graphics').all()
    return render(request, 'teams/graphics/members.html', {'members': qs})


def add_book_review(request):
    """
    レビュー追加ビュー（科目レビュー・参考書レビュー）
    """
    book_form = BookReviewForm()

    # 年度の選択肢を取得
    years = CourseOffering.objects.using('graphics').values_list('year', flat=True).distinct().order_by('-year')
    year_choices = [(year, f'{year}年度') for year in years]

    # 開講学期の選択肢を取得
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

    subject_form = SubjectReviewForm()
    subject_form.fields['year'].choices = year_choices
    subject_form.fields['semester'].choices = semester_choices
    if year_choices:
        subject_form.fields['year'].initial = year_choices[0][0]  # 最新年度をデフォルト

    if request.method == 'POST':
        book_form = BookReviewForm(request.POST)
        if book_form.is_valid():
            # graphicsデータベースに保存
            review = book_form.save(commit=False)

            # ISBNから書籍情報を取得
            if review.isbn:
                isbn = review.isbn
                book_info = fetch_book_info_from_openbd(isbn)

                if book_info:
                    review.title = book_info.get('title')
                    review.author = book_info.get('author')
                    review.publication_date = book_info.get('publication_date')

            review.save(using='graphics')
            messages.success(request, '参考書レビューを登録しました。')
            return redirect('graphics:book_reviews')

    context = {
        'book_form': book_form,
        'subject_form': subject_form,
    }
    return render(request, 'teams/graphics/add_book_review.html', context)


def add_subject_review(request):
    """
    科目レビュー追加ビュー
    """
    if request.method == 'POST':
        # 年度と開講学期の選択肢を取得
        years = CourseOffering.objects.using('graphics').values_list('year', flat=True).distinct().order_by('-year')
        year_choices = [(year, f'{year}年度') for year in years]

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
            review.save(using='graphics')
            messages.success(request, '科目レビューを登録しました。')
            return redirect('graphics:book_reviews')

    # POSTでない場合やバリデーションエラーの場合は、add_book_reviewにリダイレクト
    return redirect('graphics:add_book_review')


def book_reviews(request):
    """
    レビュー一覧ビュー（参考書レビュー・科目レビュー）
    """
    # 参考書レビューと科目レビューを取得
    book_reviews = BookReview.objects.using('graphics').all()
    subject_reviews = SubjectReview.objects.using('graphics').all()

    # 両方のレビューをリストにまとめて、作成日時でソート
    all_reviews = []

    # 参考書レビューをリストに追加（subjectが空でないもののみ）
    for review in book_reviews:
        if review.subject:  # subjectが空でない場合のみ追加
            all_reviews.append({
                'type': 'book',
                'subject': review.subject,
                'isbn': review.isbn,
                'title': review.title,
                'author': review.author,
                'publication_date': review.publication_date,
                'review': review.review,
                'rating': review.rating,
                'created_at': review.created_at,
            })

    # 科目レビューをリストに追加
    for review in subject_reviews:
        # 担当教員のリストを取得
        teachers = review.course_offering.teachers.all()
        teacher_names = ', '.join([teacher.name for teacher in teachers])

        all_reviews.append({
            'type': 'subject',
            'subject': review.course_offering.subject.name,
            'year': review.course_offering.year,
            'semester': review.course_offering.semester,
            'course_info': f"{review.course_offering.year}年度 {review.course_offering.semester} {review.course_offering.grade}",
            'teachers': teacher_names,
            'review': review.review,
            'rating': review.rating,
            'created_at': review.created_at,
        })

    # 作成日時でソート（新しい順）
    all_reviews.sort(key=lambda x: x['created_at'], reverse=True)

    return render(request, 'teams/graphics/book_reviews.html', {'reviews': all_reviews})


def search_courses(request):
    """
    科目検索ビュー
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

        # 各コースに学科数を追加
        for course in courses:
            course.dept_count = course.departments.count()

        total_count = courses.count()

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