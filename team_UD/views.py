from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Member, Event, Memo
from datetime import datetime, timedelta
import calendar
import json


def index(request):
    return render(request, "teams/team_UD/index.html")


def members(request):
    qs = Member.objects.using("team_UD").all()  # ← team_terrace DBを明示
    return render(request, "teams/team_UD/members.html", {"members": qs})


def calendar_view(request):
    # 現在の年月を取得（またはパラメータから）
    today = datetime.now()

    # 前月・次月のナビゲーション処理
    month_param = request.GET.get("month")
    if month_param == "prev":
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("current_month", today.month))
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    elif month_param == "next":
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("current_month", today.month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    else:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

    # 月の最初と最後の日を取得
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    # 今月のイベントを取得
    events = (
        Event.objects.using("team_UD")
        .filter(start_time__year=year, start_time__month=month)
        .order_by("start_time")
    )

    # カレンダーの日付データを生成
    cal = calendar.monthcalendar(year, month)
    calendar_days = []

    for week in cal:
        for day in week:
            if day == 0:
                # 前月または次月の日付（空欄）
                calendar_days.append(
                    {"day": "", "is_other_month": True, "is_today": False, "events": []}
                )
            else:
                # 今月の日付
                current_date = datetime(year, month, day)
                is_today = current_date.date() == today.date()

                # その日のイベントを取得
                day_events = [e for e in events if e.start_time.day == day]

                calendar_days.append(
                    {
                        "day": day,
                        "is_other_month": False,
                        "is_today": is_today,
                        "events": day_events,
                    }
                )

    context = {
        "events": events,
        "calendar_days": calendar_days,
        "current_month": f"{year}年{month}月",
        "year": year,
        "month": month,
    }

    return render(request, "teams/team_UD/calendar.html", context)


def memo_view(request):
    memos = Memo.objects.using("team_UD").all().order_by("-created_at")
    return render(request, "teams/team_UD/memo.html", {"memos": memos})


@csrf_exempt
def get_memo_by_date(request, year, month, day):
    """特定の日付のメモを取得するAPI"""
    if request.method == "GET":
        try:
            target_date = datetime(year, month, day).date()
            memos = Memo.objects.using("team_UD").filter(date=target_date).order_by("-created_at")
            memo_list = [
                {
                    "id": memo.id,
                    "company_name": memo.company_name,
                    "interview_stage": memo.interview_stage,
                    "interview_date": memo.interview_date.strftime("%Y-%m-%d") if memo.interview_date else None,
                    "status": memo.status,
                    "content": memo.content,
                    "created_at": memo.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": memo.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for memo in memos
            ]
            return JsonResponse({"memos": memo_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def save_memo(request):
    """メモを保存するAPI"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            date_str = data.get("date")
            content = data.get("content")
            company_name = data.get("company_name", "")
            interview_stage = data.get("interview_stage", "")
            interview_date_str = data.get("interview_date")
            status = data.get("status", "")
            memo_id = data.get("id")

            if not date_str or not content:
                return JsonResponse({"error": "日付と内容は必須です"}, status=400)

            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 面接日の処理
            interview_date = None
            if interview_date_str:
                interview_date = datetime.strptime(interview_date_str, "%Y-%m-%d").date()

            if memo_id:
                # 既存のメモを更新
                memo = Memo.objects.using("team_UD").get(id=memo_id)
                memo.content = content
                memo.date = target_date
                memo.company_name = company_name
                memo.interview_stage = interview_stage
                memo.interview_date = interview_date
                memo.status = status
                memo.save(using="team_UD")
            else:
                # 新しいメモを作成
                memo = Memo(
                    date=target_date,
                    content=content,
                    company_name=company_name,
                    interview_stage=interview_stage,
                    interview_date=interview_date,
                    status=status,
                )
                memo.save(using="team_UD")

            return JsonResponse(
                {
                    "id": memo.id,
                    "content": memo.content,
                    "company_name": memo.company_name,
                    "interview_stage": memo.interview_stage,
                    "interview_date": memo.interview_date.strftime("%Y-%m-%d") if memo.interview_date else None,
                    "status": memo.status,
                    "date": memo.date.strftime("%Y-%m-%d"),
                    "created_at": memo.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": memo.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def create_memo(request):
    """就活メモを作成する"""
    if request.method == "POST":
        try:
            # フォームデータを取得
            company_name = request.POST.get("company_name", "")
            interview_stage = request.POST.get("interview_stage", "")
            interview_date_str = request.POST.get("interview_date")
            status = request.POST.get("status", "")
            content = request.POST.get("content", "")

            # 必須フィールドのチェック
            if not company_name or not interview_stage or not status or not content:
                return JsonResponse({"error": "必須項目を入力してください"}, status=400)

            # 面接日の処理
            interview_date = None
            if interview_date_str:
                interview_date = datetime.strptime(interview_date_str, "%Y-%m-%d").date()

            # メモを作成
            memo = Memo(
                company_name=company_name,
                interview_stage=interview_stage,
                interview_date=interview_date,
                status=status,
                content=content,
                date=datetime.now().date(),
            )
            memo.save(using="team_UD")

            # メモ一覧ページにリダイレクト
            from django.shortcuts import redirect
            return redirect("team_UD:memo")

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "POSTメソッドのみ許可されています"}, status=405)


@csrf_exempt
def delete_memo(request, memo_id):
    """メモを削除するAPI"""
    if request.method == "DELETE":
        try:
            memo = Memo.objects.using("team_UD").get(id=memo_id)
            memo.delete(using="team_UD")
            return JsonResponse({"message": "削除しました"}, status=200)
        except Memo.DoesNotExist:
            return JsonResponse({"error": "メモが見つかりません"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
