from django.shortcuts import render
from .models import Member, Event, Memo


def index(request):
    return render(request, "teams/team_UD/index.html")


def members(request):
    qs = Member.objects.using("team_UD").all()  # ← team_terrace DBを明示
    return render(request, "teams/team_UD/members.html", {"members": qs})


def calendar_view(request):
    events = Event.objects.using("team_UD").all().order_by("start_time")
    return render(request, "teams/team_UD/calendar.html", {"events": events})


def memo_view(request):
    memos = Memo.objects.using("team_UD").all().order_by("-created_at")
    return render(request, "teams/team_UD/memo.html", {"memos": memos})
