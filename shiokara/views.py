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

def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)

    reviews = company.reviews.all()  # related_name="reviews"
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    context = {
        "company": company,
        "reviews": reviews,
        "avg_rating": avg_rating,
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