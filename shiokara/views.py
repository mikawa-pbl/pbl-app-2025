from django.shortcuts import render, get_object_or_404
from django.db.models import Q  # ★ 追加：あいまい検索用
from django.db.models import Avg
from django.conf import settings  # ★追加
import json                       # ★追加
from pathlib import Path          # ★追加
from .models import Department, Company , CompanyReview 
from django.shortcuts import render, get_object_or_404, redirect


# このアプリが使う DB のエイリアス名
# settings.DATABASES / routers.py に合わせて変更してください
DB_ALIAS = "shiokara"  # 例: "team_a" などならそこに変える
FIXTURE_PATH = Path(settings.BASE_DIR) / "shiokara" / "fixtures" / "company_reviews.json"

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
    return render(request, "teams/shiokara/department_list.html", context)


def department_detail(request, short_name):
    """
    学科別 企業一覧ページ
    例: /shiokara/departments/cs/
    """
    department = get_object_or_404(
        Department.objects.using(DB_ALIAS),
        short_name=short_name,
    )
    # ManyToMany の関連企業
    companies = department.companies.all()

    context = {
        "department": department,
        "companies": companies,
    }
    return render(request, "teams/shiokara/department_detail.html", context)

'''
def company_search(request):
    """
    企業検索ページ
    ・q: キーワード（企業名・紹介文から部分一致）
    ・dept: 学科の short_name（任意）
    """
    query = request.GET.get("q", "").strip()
    dept_short = request.GET.get("dept", "").strip()

    # 検索対象のベースとなるクエリセット
    companies = Company.objects.using(
        DB_ALIAS).all().prefetch_related("departments")

    # 学科で絞り込み（dept パラメータが指定されていれば）
    selected_department = None
    if dept_short:
        companies = companies.filter(departments__short_name=dept_short)
        selected_department = Department.objects.using(DB_ALIAS).filter(
            short_name=dept_short
        ).first()

    # キーワード検索（企業名 or 紹介文）
    if query:
        companies = companies.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()

    # プルダウン用に全学科一覧も渡す
    departments = Department.objects.using(DB_ALIAS).all()

    context = {
        "query": query,
        "dept_short": dept_short,
        "selected_department": selected_department,
        "departments": departments,
        "companies": companies,
    }
    return render(request, "teams/shiokara/company_search.html", context)
'''
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Count  # ★ Count 追加
from django.conf import settings
from pathlib import Path
import json

from .models import Department, Company, CompanyReview

DB_ALIAS = "shiokara"
FIXTURE_PATH = Path(settings.BASE_DIR) / "shiokara" / "fixtures" / "company_reviews.json"

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
    ・q: キーワード（企業名・紹介文から部分一致）
    ・dept: 学科 short_name（複数可）
    ・lab: 研究室大別コード ("1.2" など, 複数可)
    ・area: 勤務地カテゴリ (tokai / capital / kansai / nationwide ...)
    ・recommend: 1 なら推薦ありのみ
    ・briefing: 1 なら学内説明会ありのみ
    ・logic: "and" / "or" でフィルタ条件の結合を切り替え
    ・sort: employees / starting_salary / annual_holidays / review_count
    """

    query = request.GET.get("q", "").strip()

    # 学科（複数選択対応: ?dept=cs&dept=ee）
    dept_shorts = request.GET.getlist("dept")  # ← 複数取る
    # 研究室大別（"1.2" みたいなコードを前提）
    lab_codes = request.GET.getlist("lab")

    area_key = request.GET.get("area", "").strip()
    recommend = request.GET.get("recommend", "").strip()  # "1" なら有り
    briefing = request.GET.get("briefing", "").strip()    # "1" なら有り

    filter_logic = request.GET.get("logic", "and")  # and / or
    sort = request.GET.get("sort", "name")          # デフォルトは名前順

    # ベースとなるクエリセット
    companies = (
        Company.objects.using(DB_ALIAS)
        .all()
        .prefetch_related("departments")
        .annotate(
            review_count=Count("companyreview")  # ★ レビュー数
        )
    )

    # ① キーワード検索
    if query:
        companies = companies.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # ② フィルタ条件を Q のリストとして用意
    filter_qs = []

    # --- 学科フィルタ (ORでまとめた1つのQにする) ---
    if dept_shorts:
        q_dept = Q()
        for short in dept_shorts:
            q_dept |= Q(departments__short_name=short)
        filter_qs.append(q_dept)

    # --- 研究室大別フィルタ (oncampus_briefingにコードが含まれるか) ---
    # oncampus_briefing が JSONField(List[str]) の想定で contains=[code] を使用
    if lab_codes:
        q_lab = Q()
        for code in lab_codes:
            # JSON配列に特定の文字列が含まれる場合
            q_lab |= Q(oncampus_briefing__contains=[code])
        filter_qs.append(q_lab)

    # --- 勤務地フィルタ ---
    if area_key:
        keywords = AREA_KEYWORDS.get(area_key)
        if keywords:
            q_area = Q()
            for kw in keywords:
                q_area |= Q(area__icontains=kw)
            filter_qs.append(q_area)

    # --- 推薦の有無 ---
    if recommend == "1":
        filter_qs.append(Q(tut_recommendation=1))

    # --- 学内説明会の有無 ---
    if briefing == "1":
        # 「なにかしら oncampus_briefing に入っている企業」
        # JSONField で空リスト以外をチェックしたい場合は
        # 長さ判定もありだが、簡易には空文字との比較でもOK
        filter_qs.append(~Q(oncampus_briefing=[]))

    # ③ AND / OR モードでフィルタをまとめて適用
    if filter_qs:
        combined_q = filter_qs[0]
        for q in filter_qs[1:]:
            if filter_logic == "or":
                combined_q |= q
            else:
                combined_q &= q
        companies = companies.filter(combined_q).distinct()

    # ④ ソート
    if sort == "employees":
        companies = companies.order_by("-employees")
    elif sort == "starting_salary":
        companies = companies.order_by("-starting_salary")
    elif sort == "annual_holidays":
        companies = companies.order_by("-annual_holidays")
    elif sort == "review_count":
        companies = companies.order_by("-review_count", "name")
    else:
        sort = "name"
        companies = companies.order_by("name")

    # 学科プルダウン用
    departments = Department.objects.using(DB_ALIAS).all()

    context = {
        "query": query,
        "departments": departments,

        # 選択状態をテンプレートで再現する用
        "dept_shorts": dept_shorts,
        "lab_codes": lab_codes,
        "area_key": area_key,
        "recommend": recommend,
        "briefing": briefing,
        "filter_logic": filter_logic,
        "sort": sort,

        "companies": companies,
    }
    return render(request, "teams/shiokara/company_search.html", context)


def company_detail(request, pk):
    company = get_object_or_404(Company.objects.using("shiokara"), pk=pk)

    # ★ sort パラメータ取得（?sort=new / ?sort=rating）
    sort = request.GET.get("sort", "new")

    qs = CompanyReview.objects.using("shiokara").filter(company=company)

    if sort == "rating":
        # 評価が高い順（同じ評価なら新しい順）
        reviews = qs.order_by("-rating", "-created_at")
    else:
        # デフォルト：新着順
        sort = "new"
        reviews = qs.order_by("-created_at")

    avg_rating = qs.aggregate(avg=Avg("rating"))["avg"]

    context = {
        "company": company,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "sort": sort,  # ★ テンプレで選択状態に使う
    }
    return render(request, "teams/shiokara/company_detail.html", context)

def company_experience_post(request, pk):
    """会社ごとの体験談投稿ページ（まだ保存はしない、表示だけ）"""
    company = get_object_or_404(Company, pk=pk)

    context = {
        "company": company,
    }
    return render(request, "teams/shiokara/company_experience_post.html", context)

def company_experience_post(request, pk):
    """企業ごとの口コミ投稿ページ（体験談と口コミをまとめて扱う）"""
    company = get_object_or_404(Company.objects.using("shiokara"), pk=pk)

    initial = {
        "grade": "",
        "department_name": "",
        "lab_field": "",
        "gender": "no_answer",
        "high_school": "",
        "comment": "",
        "rating": "",
    }
    error = None

    if request.method == "POST":
        grade = request.POST.get("grade", "").strip()
        department_name = request.POST.get("department_name", "").strip()
        lab_field = request.POST.get("lab_field", "").strip()
        gender = request.POST.get("gender", "").strip() or "no_answer"
        high_school = request.POST.get("high_school", "").strip()
        comment = request.POST.get("comment", "").strip()
        rating_str = request.POST.get("rating", "").strip()

        initial.update({
            "grade": grade,
            "department_name": department_name,
            "lab_field": lab_field,
            "gender": gender,
            "high_school": high_school,
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
            # ★ DB に保存
            review = CompanyReview.objects.using("shiokara").create(
                company=company,
                grade=grade,
                department_name=department_name,
                lab_field=lab_field,
                gender=gender,
                high_school=high_school,
                comment=comment,
                rating=rating,
            )

            # ★ JSON にも追記
            append_review_to_fixture(review)

            return redirect("shiokara:company_detail", pk=company.pk)

    context = {"company": company, "error": error, **initial}
    return render(request, "teams/shiokara/company_experience_post.html", context)

def append_review_to_fixture(review: CompanyReview) -> None:
    """投稿されたレビューを JSON フィクスチャに 1 件追記する"""

    # 既存の JSON を読む（なければ空配列）
    if FIXTURE_PATH.exists():
        try:
            text = FIXTURE_PATH.read_text(encoding="utf-8")
            data = json.loads(text) if text.strip() else []
        except json.JSONDecodeError:
            # 壊れていたら、とりあえず作り直す
            data = []
    else:
        data = []

    # フィクスチャ形式のオブジェクトを作成
    obj = {
        "model": "shiokara.companyreview",
        "pk": review.pk,
        "fields": {
            "company": review.company_id,
            "grade": review.grade,
            "department_name": review.department_name,
            "lab_field": review.lab_field,
            "gender": review.gender,
            "high_school": review.high_school,
            "comment": review.comment,
            "rating": review.rating,
            # loaddata で読めるよう ISO 形式の文字列にしておく
            "created_at": review.created_at.isoformat(),
        },
    }

    data.append(obj)

    # JSON として書き戻し
    FIXTURE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )