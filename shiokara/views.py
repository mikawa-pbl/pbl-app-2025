# shiokara/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.cache import never_cache
from django.conf import settings
import json
from pathlib import Path

from .models import Department, Company, CompanyReview, Person, CompanyView, SiteFeedback
from .forms import PersonLoginForm  # いまは未使用でもOK


# このアプリが使う DB のエイリアス名
DB_ALIAS = "shiokara"

# フィクスチャ用パス
FIXTURE_PATH = Path(settings.BASE_DIR) / "shiokara" / "fixtures" / "company_reviews.json"
PERSON_FIXTURE_PATH = Path(settings.BASE_DIR) / "shiokara" / "fixtures" / "persons.json"


# =========================
# ログイン関連（共通ヘルパー）
# =========================

def get_current_person(request):
    """
    セッションに保存された person_id から Person を取得する。
    ログイン中なら Person、未ログインなら None を返す。
    """
    person_id = request.session.get("person_id")
    if not person_id:
        return None
    try:
        return Person.objects.using(DB_ALIAS).get(pk=person_id)
    except Person.DoesNotExist:
        return None


def render_with_person(request, template_name, context=None):
    """
    どの画面でも person と departments をテンプレートに渡すためのラッパー。
    context_processors をいじらずに person と departments を渡すための実装。
    """
    if context is None:
        context = {}
    context["person"] = get_current_person(request)
    # 全ページでサイドバーに表示するために departments を追加
    if "departments" not in context:
        context["departments"] = Department.objects.using(DB_ALIAS).prefetch_related("companies").all()
    return render(request, template_name, context)


def logout_view(request):
    """
    ログアウト処理:
    - セッションを全クリア
    - ログインメニューにリダイレクト
    """
    request.session.flush()
    return redirect("shiokara:login")


def append_person_to_fixture(person: Person) -> None:
    """登録された Person を JSON フィクスチャに 1 件追記する"""

    if PERSON_FIXTURE_PATH.exists():
        try:
            text = PERSON_FIXTURE_PATH.read_text(encoding="utf-8")
            data = json.loads(text) if text.strip() else []
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    obj = {
        "model": "shiokara.person",
        "pk": person.pk,
        "fields": {
            "student_id": person.student_id,
            "course": person.course,
            "grade": person.grade,
            "department_name": person.department_name,
            "lab_field": person.lab_field,
            "gender": getattr(person, 'gender', ''),
            "password": person.password,
            "nickname": getattr(person, 'nickname', ''),
            "icon_picture": getattr(person, 'icon_picture', ''),
            "created_at": person.created_at.isoformat(),
            "seen_dept_tutorial": person.seen_dept_tutorial,
            "seen_search_tutorial": person.seen_search_tutorial,
            "seen_points_tutorial": person.seen_points_tutorial,
            "points": person.points,
        },
    }

    data.append(obj)

    PERSON_FIXTURE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def update_person_in_fixture(person: Person) -> None:
    """既存の Person をフィクスチャで更新する（チュートリアル表示済み etc）"""
    
    if not PERSON_FIXTURE_PATH.exists():
        return
    
    try:
        text = PERSON_FIXTURE_PATH.read_text(encoding="utf-8")
        data = json.loads(text) if text.strip() else []
    except json.JSONDecodeError:
        return
    
    # 該当する pk を持つ Person を探して更新
    for obj in data:
        if obj.get("pk") == person.pk and obj.get("model") == "shiokara.person":
            obj["fields"].update({
                "student_id": person.student_id,
                "course": person.course,
                "grade": person.grade,
                "department_name": person.department_name,
                "lab_field": person.lab_field,
                "gender": getattr(person, 'gender', ''),
                "password": person.password,
                "created_at": person.created_at.isoformat(),
                "seen_dept_tutorial": person.seen_dept_tutorial,
                "seen_search_tutorial": person.seen_search_tutorial,
                "seen_points_tutorial": person.seen_points_tutorial,
                "points": person.points,
            })
            break
    
    PERSON_FIXTURE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# =========================
# ログイン / 新規登録画面
# =========================

def login_menu(request):
    """
    ログイン or 新規登録を選ぶメニュー画面。
    """
    return render_with_person(request, "teams/shiokara/login_menu.html")


def login_view(request):
    """
    学籍番号 + パスワードだけでログインする画面。
    """
    error = None

    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()

        if not student_id or not password:
            error = "学籍番号とパスワードを入力してください。"
        else:
            try:
                person = Person.objects.using(DB_ALIAS).get(
                    student_id=student_id,
                    password=password,
                )
                request.session["person_id"] = person.id
                # ログイン後は学科一覧へ
                return redirect("shiokara:department_list")
            except Person.DoesNotExist:
                error = "学籍番号またはパスワードが正しくありません。"

    context = {"error": error}
    return render_with_person(request, "teams/shiokara/login_form.html", context)


def register_view(request):
    """
    学生情報の新規登録画面。
    （画像のようなフル項目フォーム）
    """
    error = None

    # エラー時に入力を戻すための初期値
    initial = {
        "student_id": "",
        "course": "",
        "grade": "",
        "department_name": "",
        "lab_field": "",
        "password": "",
        "gender": "",
    }

    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        course = request.POST.get("course", "").strip()          # B/M/D
        grade = request.POST.get("grade", "").strip()            # "1","2",...
        department_name = request.POST.get("department_name", "").strip()
        lab_field = request.POST.get("lab_field", "").strip()
        password = request.POST.get("password", "").strip()

        gender = request.POST.get("gender", "").strip()

        initial.update(
            student_id=student_id,
            course=course,
            grade=grade,
            department_name=department_name,
            lab_field=lab_field,
            password=password,
            gender=gender,
        )

        # --- バリデーション ---
        if not (student_id and course and grade and department_name and lab_field and password):
            error = "すべての項目を入力してください。"
        elif Person.objects.using(DB_ALIAS).filter(student_id=student_id).exists():
            error = "この学籍番号は既に登録されています。ログインを試してください。"
        else:
            # --- 登録 ---
            person = Person.objects.using(DB_ALIAS).create(
                student_id=student_id,
                course=course,
                grade=int(grade),
                department_name=department_name,
                lab_field=lab_field,
                gender=gender,
                password=password,
            )
            append_person_to_fixture(person)
            request.session["person_id"] = person.id
            return redirect("shiokara:department_list")

    context = {"error": error, **initial}
    return render_with_person(request, "teams/shiokara/register.html", context)


def my_page(request):
    """
    とりあえずのマイページ。
    ログインしていなければログインメニューにリダイレクト。
    """
    person = get_current_person(request)
    if not person:
        return redirect("shiokara:login")

    # POST処理: ニックネームとアイコンの更新
    if request.method == "POST":
        nickname = request.POST.get("nickname", "").strip()
        icon_file = request.FILES.get("icon")
        
        # ニックネームを更新
        if nickname != person.nickname:
            Person.objects.using(DB_ALIAS).filter(pk=person.pk).update(nickname=nickname)
        
        # アイコン画像をアップロード
        if icon_file:
            import os
            from django.conf import settings
            
            # ファイル名を生成（学籍番号_元のファイル名）
            ext = os.path.splitext(icon_file.name)[1]
            safe_filename = f"{person.student_id}{ext}"
            
            # shiokara/static/icon_picture/ に保存
            icon_dir = Path(settings.BASE_DIR) / "shiokara" / "static" / "icon_picture"
            icon_dir.mkdir(parents=True, exist_ok=True)
            icon_path = icon_dir / safe_filename
            
            # ファイルを保存
            with open(icon_path, 'wb+') as destination:
                for chunk in icon_file.chunks():
                    destination.write(chunk)
            
            # DBに相対パスを保存（staticから見た相対パス）
            relative_path = f"icon_picture/{safe_filename}"
            Person.objects.using(DB_ALIAS).filter(pk=person.pk).update(icon_picture=relative_path)
            
            # フィクスチャのicon_pictureディレクトリにもコピー
            fixture_icon_dir = Path(settings.BASE_DIR) / "shiokara" / "fixtures" / "icon_picture"
            fixture_icon_dir.mkdir(parents=True, exist_ok=True)
            fixture_icon_path = fixture_icon_dir / safe_filename
            with open(fixture_icon_path, 'wb+') as destination:
                icon_path_obj = open(icon_path, 'rb')
                destination.write(icon_path_obj.read())
                icon_path_obj.close()
            
            # フィクスチャも更新
            append_person_to_fixture(Person.objects.using(DB_ALIAS).get(pk=person.pk))
        
        return redirect("shiokara:my_page")

    # リフレッシュして favorites を取得
    try:
        refreshed = Person.objects.using(DB_ALIAS).get(pk=person.pk)
        favorites = refreshed.favorites.all()
    except Exception:
        refreshed = person
        favorites = []

    return render_with_person(request, "teams/shiokara/my_page.html", {"person": refreshed, "favorites": favorites})


def site_feedback(request):
    """
    サイトへの要望・フィードバックを投稿するページ。
    投稿すると1ポイント付与される。
    """
    person = get_current_person(request)
    if not person:
        return redirect("shiokara:login")

    error = None
    success = False

    if request.method == "POST":
        feedback_text = request.POST.get("feedback_text", "").strip()

        if not feedback_text:
            error = "要望を入力してください。"
        elif len(feedback_text) < 10:
            error = "要望は10文字以上入力してください。"
        else:
            # フィードバックを保存
            SiteFeedback.objects.using(DB_ALIAS).create(
                person=person,
                feedback_text=feedback_text
            )

            # ポイントを付与（+1）
            Person.objects.using(DB_ALIAS).filter(pk=person.pk).update(points=F('points') + 1)

            # セッションに付与情報を入れてリダイレクト先でポップアップ表示する
            request.session['points_awarded'] = 1
            success = True

    # 既存のフィードバック件数を取得
    feedback_count = SiteFeedback.objects.using(DB_ALIAS).filter(person=person).count()

    context = {
        "error": error,
        "success": success,
        "feedback_count": feedback_count,
    }
    return render_with_person(request, "teams/shiokara/site_feedback.html", context)


# =========================
# 既存の画面
# =========================

def department_list(request):
    """
    学科一覧ページ
    """
    departments = (
        Department.objects.using(DB_ALIAS)
        .all()
        .prefetch_related("companies")
    )
    context = {
        "departments": departments,
    }
    # チュートリアルの自動起動判定（ログイン中かつ未表示の場合）
    person = get_current_person(request)
    context["auto_start_tutorial"] = bool(person and not getattr(person, "seen_dept_tutorial", False))
    return render_with_person(request, "teams/shiokara/department_list.html", context)


@csrf_exempt
def tutorial_seen(request):
    """
    フロントからチュートリアルを表示済みにするために呼ばれる API。
    POST で呼び出すことを想定。
    
    クエリパラメータ:
    - type: 'dept' (学科別企業一覧), 'search' (企業検索), 'points' (ポイント) 
    デフォルトは 'search'
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required"}, status=405)

    person = get_current_person(request)
    if not person:
        return JsonResponse({"ok": False, "error": "not authenticated"}, status=403)

    # チュートリアルの種類を取得（デフォルトは 'search'）
    tutorial_type = request.GET.get('type', 'search').strip()
    
    # 更新するフィールドを決定
    if tutorial_type == 'dept':
        update_field = 'seen_dept_tutorial'
    elif tutorial_type == 'points':
        update_field = 'seen_points_tutorial'
    else:  # 'search' or その他
        update_field = 'seen_search_tutorial'
    
    # 更新（using DB alias を指定）
    Person.objects.using(DB_ALIAS).filter(pk=person.pk).update(**{update_field: True})
    
    # DB から最新の person データを取得して persons.json にも保存
    updated_person = Person.objects.using(DB_ALIAS).get(pk=person.pk)
    update_person_in_fixture(updated_person)
    
    # セッション内の person は次回取得時に DB から刷新されるためそのままで良い
    return JsonResponse({"ok": True, "type": tutorial_type})




# =========================
# 企業検索
# =========================

# 勤務地カテゴリ → area のキーワード例
AREA_KEYWORDS = {
    "tokai": ["愛知", "岐阜", "三重", "静岡"],
    "capital": ["東京", "神奈川", "千葉", "埼玉"],
    "kansai": ["大阪", "京都", "兵庫", "滋賀", "奈良"],
    "nationwide": ["全国", "全国勤務", "全国拠点"],
}


def company_search(request):
    """
    企業検索ページ
    ・q: キーワード
    ・dept: 学科 short_name（複数可）
    ・area: 勤務地カテゴリ
    ・recommend: 1 なら推薦ありのみ
    ・briefing: 1 なら学内説明会ありのみ
    ・logic: and / or
    ・sort: employees / starting_salary / annual_holidays / review_count / name
    ・lab: 研究室コード（oncampus_briefing に含まれている想定）
    """

    query = request.GET.get("q", "").strip()

    # 学科は getlist で（今はセレクト1個だけど将来チェックボックスにも対応できる）
    dept_shorts = request.GET.getlist("dept")
    dept_short = dept_shorts[0] if dept_shorts else ""

    area_key = request.GET.get("area", "").strip()
    recommend = request.GET.get("recommend", "").strip()
    briefing = request.GET.get("briefing", "").strip()
    filter_logic = request.GET.get("logic", "and")
    sort = request.GET.get("sort", "name")
    lab_code = request.GET.get("lab", "").strip()

    # ベースとなるクエリセット ＋ レビュー件数を annotate
    companies = (
        Company.objects.using(DB_ALIAS)
        .all()
        .prefetch_related("departments")
        .annotate(
            review_count=Count("reviews")  # related_name="reviews" を想定
        )
    )

    # キーワード検索（常にAND条件で適用）
    if query:
        companies = companies.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # 学科フィルタ（常にAND条件で適用、複数指定なら OR）
    if dept_shorts:
        q_dept = Q()
        for short in dept_shorts:
            if short:
                q_dept |= Q(departments__short_name=short)
        if q_dept:
            companies = companies.filter(q_dept)

    # 研究室コード（常にAND条件で適用）
    if lab_code:
        companies = companies.filter(Q(oncampus_briefing__icontains=lab_code))

    # 企業フィルタ（勤務地、推薦あり、学内説明会あり）のみAND/OR対象
    company_filter_qs = []

    # 勤務地フィルタ
    if area_key:
        keywords = AREA_KEYWORDS.get(area_key, [])
        if keywords:
            q_area = Q()
            for kw in keywords:
                q_area |= Q(area__icontains=kw)
            company_filter_qs.append(q_area)

    # 推薦あり
    if recommend == "1":
        company_filter_qs.append(Q(tut_recommendation=True))

    # 学内説明会あり（oncampus_briefing が空/NULLでないもの）
    if briefing == "1":
        company_filter_qs.append(
            Q(oncampus_briefing__isnull=False) & ~Q(oncampus_briefing="")
        )

    # 企業フィルタのみAND / OR でまとめて適用
    if company_filter_qs:
        combined_q = company_filter_qs[0]
        for q in company_filter_qs[1:]:
            if filter_logic == "or":
                combined_q |= q
            else:
                combined_q &= q
        companies = companies.filter(combined_q).distinct()

    # ソート
    if sort == "employees":
        companies = companies.order_by("-employees", "name")
    elif sort == "starting_salary":
        companies = companies.order_by("-starting_salary", "name")
    elif sort == "annual_holidays":
        companies = companies.order_by("-annual_holidays", "name")
    elif sort == "review_count":
        companies = companies.order_by("-review_count", "name")
    else:
        sort = "name"
        companies = companies.order_by("name")

    # 学科プルダウン用
    departments = Department.objects.using(DB_ALIAS).all()

    # 閲覧済み企業一覧（ログイン中のみ）
    person = get_current_person(request)
    if person:
        viewed_company_ids = list(CompanyView.objects.using(DB_ALIAS).filter(person=person).values_list('company_id', flat=True))
        # お気に入り企業一覧（ログイン中のみ）
        favorite_company_ids = list(Person.objects.using(DB_ALIAS).filter(pk=person.pk).values_list('favorites__pk', flat=True))
    else:
        viewed_company_ids = []
        favorite_company_ids = []

    # 企業検索ページ初回訪問判定
    first_visit_search = request.GET.get('first_visit') == '1'

    # チュートリアルの自動起動判定（ログイン中かつ未表示の場合）
    auto_start_tutorial = bool(person and not getattr(person, "seen_search_tutorial", False))

    context = {
        "query": query,
        "departments": departments,
        "companies": companies,
        "viewed_company_ids": viewed_company_ids,
        "viewed_company_ids_json": json.dumps(viewed_company_ids),
        "first_visit_search": first_visit_search,
        "auto_start_tutorial": auto_start_tutorial,
        "person": person,
        "favorite_company_ids": favorite_company_ids,
        "favorite_company_ids_json": json.dumps(favorite_company_ids),

        # テンプレ側で選択状態を再現する用
        "dept_short": dept_short,
        "dept_shorts": dept_shorts,
        "area_key": area_key,
        "recommend": recommend,
        "briefing": briefing,
        "filter_logic": filter_logic,
        "sort": sort,
        "lab_code": lab_code,
    }
    return render_with_person(request, "teams/shiokara/company_search.html", context)


@never_cache
def company_detail(request, pk):
    company = get_object_or_404(Company.objects.using(DB_ALIAS), pk=pk)
    # ポイント制：企業詳細は1ポイント消費して閲覧
    person = get_current_person(request)
    if not person:
        # 未ログインならログイン画面へ
        return redirect("shiokara:login")

    # リフレッシュされた person 情報を取得
    person = Person.objects.using(DB_ALIAS).get(pk=person.pk)
    # ポイント付与ポップアップ用フラグ（POST→redirect 後に表示するため session から取得）
    points_awarded = request.session.pop('points_awarded', None)

    # oncampus_briefingの数字をコース名に変換
    FIELD_OPTIONS = {
        '1系': [
            '機械・システムデザインコース',
            '材料・生産加工コース',
            'システム制御・ロボットコース',
            '環境・エネルギーコース',
        ],
        '2系': [
            '材料エレクトロニクスコース',
            '機能電気システムコース',
            '集積電子システムコース',
            '情報通信システムコース',
        ],
        '3系': [
            '計算機数理科学分野',
            'データ情報学分野',
            'ヒューマン・ブレイン情報学分野',
            'メディア・ロボット情報学分野',
        ],
        '4系': [
            '分子制御化学分野',
            '分子生物化学分野',
            '分子機能化学分野',
        ],
        '5系': [
            '建築・都市デザイン学分野',
            '都市・地域マネジメント学分野',
        ],
    }
    
    oncampus_briefing_names = []
    if company.oncampus_briefing:
        # "1.2,4.2,5.1" のような形式をパース
        codes = [code.strip() for code in company.oncampus_briefing.split(',')]
        for code in codes:
            try:
                if '.' in code:
                    dept, idx = code.split('.')
                    dept_key = f"{dept}系"
                    idx_num = int(idx) - 1  # 1-indexedから0-indexedへ
                    if dept_key in FIELD_OPTIONS and 0 <= idx_num < len(FIELD_OPTIONS[dept_key]):
                        oncampus_briefing_names.append(FIELD_OPTIONS[dept_key][idx_num])
            except (ValueError, IndexError):
                # パースエラーは無視
                pass

    if person.points < 1:
        # ポイント不足: 専用のロック画面を表示
        return render_with_person(request, "teams/shiokara/company_detail_locked.html", {"company": company})

    # 既にこのユーザーがこの企業を閲覧済みかを確認
    viewed_exists = CompanyView.objects.using(DB_ALIAS).filter(person=person, company=company).exists()
    first_point_usage = False
    if not viewed_exists:
        # 1ポイント消費（条件付きで安全に更新）
        updated = Person.objects.using(DB_ALIAS).filter(pk=person.pk, points__gte=1).update(points=F('points') - 1)
        if not updated:
            # まれに同時更新で失敗した場合
            return render_with_person(request, "teams/shiokara/company_detail_locked.html", {"company": company})

        # 初回ポイント消費判定
        first_point_usage = True

        # 閲覧履歴を作成（以後この企業はポイントを消費しない）
        try:
            CompanyView.objects.using(DB_ALIAS).create(person=person, company=company)
        except Exception:
            # unique 制約違反等は無視して続行
            pass

        # 再取得して最新ポイント反映
        person = Person.objects.using(DB_ALIAS).get(pk=person.pk)

    sort = request.GET.get("sort", "new")

    qs = CompanyReview.objects.using(DB_ALIAS).filter(company=company)

    if sort == "rating":
        reviews = qs.order_by("-rating", "-created_at")
    else:
        sort = "new"
        reviews = qs.order_by("-created_at")

    avg_rating = qs.aggregate(avg=Avg("rating"))["avg"]

    context = {
        "company": company,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "sort": sort,
        "points_awarded": points_awarded,
        "first_point_usage": first_point_usage,
        "seen_points_tutorial": getattr(person, "seen_points_tutorial", False) if person else False,
        # このユーザーがこの企業をお気に入り登録しているか
        "is_favorite": bool(person and Person.objects.using(DB_ALIAS).filter(pk=person.pk, favorites__pk=company.pk).exists()),
        "oncampus_briefing_names": oncampus_briefing_names,
    }
    return render_with_person(request, "teams/shiokara/company_detail.html", context)


def company_experience_post(request, pk):
    """企業ごとの口コミ投稿ページ（体験談と口コミをまとめて扱う）"""
    company = get_object_or_404(Company.objects.using(DB_ALIAS), pk=pk)

    # ログインしていない場合はログインへリダイレクト
    person = get_current_person(request)
    if not person:
        return redirect("shiokara:login")

    # 初期値はログイン中の person 情報から取る（手入力を減らす）
    initial = {
        "grade": "",
        "department_name": "",
        "lab_field": "",
        "gender": "no_answer",
        "comment": "",
        "rating": "",
    }
    # ログインユーザーの情報があればプリセット
    try:
        refreshed = Person.objects.using(DB_ALIAS).get(pk=person.pk)
        initial.update({
            "grade": f"{refreshed.course}{refreshed.grade}",
            "department_name": refreshed.department_name,
            "lab_field": refreshed.lab_field,
            "gender": getattr(refreshed, "gender", "no_answer") or "no_answer",
        })
    except Exception:
        pass
    error = None

    if request.method == "POST":
        grade = request.POST.get("grade", "").strip()
        department_name = request.POST.get("department_name", "").strip()
        lab_field = request.POST.get("lab_field", "").strip()
        gender = request.POST.get("gender", "").strip() or "no_answer"
        # 高校名は不要になったため取得しない
        comment = request.POST.get("comment", "").strip()
        rating_str = request.POST.get("rating", "").strip()

        initial.update({
            "grade": grade,
            "department_name": department_name,
            "lab_field": lab_field,
            "gender": gender,
            "comment": comment,
            "rating": rating_str,
        })

        try:
            rating = int(rating_str)
        except ValueError:
            rating = 0

        if rating < 1 or rating > 5:
            error = "評価（★）は1〜5のいずれかを選んでください。"
        else:
            # 直近の投稿時間を確認して、同一企業への投稿が10分以内であれば拒否する
            ten_minutes_ago = timezone.now() - timedelta(minutes=10)
            latest = (
                CompanyReview.objects.using(DB_ALIAS)
                .filter(company=company)
                .order_by("-created_at")
                .first()
            )
            if latest and latest.created_at and latest.created_at >= ten_minutes_ago:
                error = "この企業には直近10分以内に口コミが投稿されています。しばらく待ってから再度投稿してください。"
            else:
                review = CompanyReview.objects.using(DB_ALIAS).create(
                    company=company,
                    grade=grade,
                    department_name=department_name,
                    lab_field=lab_field,
                    gender=gender,
                    comment=comment,
                    rating=rating,
                )

                append_review_to_fixture(review)

                # 投稿者にポイント付与（+5）
                Person.objects.using(DB_ALIAS).filter(pk=person.pk).update(points=F('points') + 5)
                # セッションに付与情報を入れてリダイレクト先でポップアップ表示する
                request.session['points_awarded'] = 5

                return redirect("shiokara:company_detail", pk=company.pk)

    context = {"company": company, "error": error, **initial}
    return render_with_person(request, "teams/shiokara/company_experience_post.html", context)


@csrf_exempt
def toggle_favorite(request, pk):
    """
    企業のお気に入りを追加/削除する。POST を想定。
    非 AJAX の場合は企業詳細へリダイレクトする。
    """
    company = get_object_or_404(Company.objects.using(DB_ALIAS), pk=pk)
    person = get_current_person(request)
    if not person:
        return redirect("shiokara:login")

    # リフレッシュ
    person = Person.objects.using(DB_ALIAS).get(pk=person.pk)

    # トグル
    exists = person.favorites.filter(pk=company.pk).exists()
    try:
        if exists:
            person.favorites.remove(company)
            added = False
        else:
            person.favorites.add(company)
            added = True
    except Exception:
        added = not exists

    # AJAX リクエストには JSON を返す
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"ok": True, "added": added})

    return redirect("shiokara:company_detail", pk=company.pk)

def append_review_to_fixture(review: CompanyReview) -> None:
    """投稿されたレビューを JSON フィクスチャに 1 件追記する"""

    if FIXTURE_PATH.exists():
        try:
            text = FIXTURE_PATH.read_text(encoding="utf-8")
            data = json.loads(text) if text.strip() else []
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    obj = {
        "model": "shiokara.companyreview",
        "pk": review.pk,
        "fields": {
            "company": review.company_id,
            "grade": review.grade,
            "department_name": review.department_name,
            "lab_field": review.lab_field,
            "gender": review.gender,
            "comment": review.comment,
            "rating": review.rating,
            "created_at": review.created_at.isoformat(),
        },
    }

    data.append(obj)

    FIXTURE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def sitemap(request):
    """
    サイトマップページ。
    サイト全体の構造を表示する。
    """
    return render_with_person(request, "teams/shiokara/sitemap.html")
