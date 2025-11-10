from django.shortcuts import render
from .models import Member, Event, Memo
from datetime import datetime, timedelta
import calendar


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
