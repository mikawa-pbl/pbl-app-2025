from django.shortcuts import render, get_object_or_404
from django.db.models import Q  # ★ 追加：あいまい検索用
from .models import Department, Company  # ★ Company も使う

# このアプリが使う DB のエイリアス名
# settings.DATABASES / routers.py に合わせて変更してください
DB_ALIAS = "shiokara"  # 例: "team_a" などならそこに変える


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
