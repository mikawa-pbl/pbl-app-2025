from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Member, Event, Memo, Account, Company
from datetime import datetime, timedelta
import calendar
import json

# カレンダーを日曜日始まりに設定
calendar.setfirstweekday(calendar.SUNDAY)


def index(request):
    return redirect("team_UD:calendar")


def calendar_view(request):
    # ログインチェック
    if "user_id" not in request.session:
        return redirect("team_UD:login")
    
    user_id = request.session["user_id"]
    
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

    # 今月のメモを取得
    memos = (
        Memo.objects.using("team_UD")
        .filter(date__year=year, date__month=month, account_id=user_id)
        .select_related("company")
    )

    # メモを日付でグループ化
    memos_by_date = {}
    for memo in memos:
        date_key = memo.date.day
        if date_key not in memos_by_date:
            memos_by_date[date_key] = []
        memos_by_date[date_key].append(memo)

    # カレンダーの日付データを生成
    cal = calendar.monthcalendar(year, month)
    calendar_days = []

    for week in cal:
        for day in week:
            if day == 0:
                # 前月または次月の日付（空欄）
                calendar_days.append(
                    {"day": "", "is_other_month": True, "is_today": False, "events": [], "memos": []}
                )
            else:
                # 今月の日付
                current_date = datetime(year, month, day)
                is_today = current_date.date() == today.date()

                # その日のイベントを取得
                day_events = [e for e in events if e.start_time.day == day]
                
                # その日のメモを取得
                day_memos = memos_by_date.get(day, [])

                calendar_days.append(
                    {
                        "day": day,
                        "is_other_month": False,
                        "is_today": is_today,
                        "events": day_events,
                        "memos": day_memos,
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


@csrf_exempt
def get_companies(request):
    """会社リストを取得するAPI（検索機能付き）"""
    if request.method == "GET":
        try:
            search_query = request.GET.get("search", "").strip()
            
            if search_query:
                # 検索クエリがある場合は部分一致で検索
                companies = Company.objects.using("team_UD").filter(name__icontains=search_query)
            else:
                # 検索クエリがない場合は全件取得
                companies = Company.objects.using("team_UD").all()
            
            company_list = [
                {
                    "id": company.id,
                    "name": company.name,
                }
                for company in companies
            ]
            
            return JsonResponse({"companies": company_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def get_memo_by_date(request, year, month, day):
    """特定の日付のメモを取得するAPI"""
    if request.method == "GET":
        try:
            # ログインチェック
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            user_id = request.session["user_id"]
            target_date = datetime(year, month, day).date()
            memos = Memo.objects.using("team_UD").filter(date=target_date, account_id=user_id).order_by("-created_at")
            memo_list = [
                {
                    "id": memo.id,
                    "title": memo.title,
                    "date": memo.date.strftime("%Y-%m-%d"),
                    "company_id": memo.company.id if memo.company else None,
                    "company_name": memo.company.name if memo.company else "",
                    "interview_stage": memo.interview_stage,
                    "interview_date": memo.interview_date.strftime("%Y-%m-%d") if memo.interview_date else None,
                    "content": memo.content,
                    "interview_questions": memo.interview_questions,
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
            # ログインチェック
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            user_id = request.session["user_id"]
            data = json.loads(request.body)
            date_str = data.get("date")
            title = data.get("title", "").strip()[:100]  # 最大100文字に制限
            content = data.get("content", "")  # デフォルト値を空文字に設定
            company_id = data.get("company_id")
            interview_stage = data.get("interview_stage", "")
            interview_date_str = data.get("interview_date")
            interview_questions = data.get("interview_questions", "")
            memo_id = data.get("id")

            if not date_str:
                return JsonResponse({"error": "日付は必須です"}, status=400)

            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 会社の取得
            company = None
            if company_id:
                try:
                    company = Company.objects.using("team_UD").get(id=company_id)
                except Company.DoesNotExist:
                    return JsonResponse({"error": "指定された会社が見つかりません"}, status=400)

            # 面接日の処理
            interview_date = None
            if interview_date_str:
                interview_date = datetime.strptime(interview_date_str, "%Y-%m-%d").date()

            if memo_id:
                # 既存のメモを更新（自分のメモのみ）
                memo = Memo.objects.using("team_UD").get(id=memo_id, account_id=user_id)
                memo.title = title
                memo.content = content
                memo.date = target_date
                memo.company = company
                memo.interview_stage = interview_stage
                memo.interview_date = interview_date
                memo.interview_questions = interview_questions
                memo.save(using="team_UD")
            else:
                # 新しいメモを作成
                account = Account.objects.using("team_UD").get(id=user_id)
                memo = Memo(
                    account=account,
                    title=title,
                    date=target_date,
                    content=content,
                    company=company,
                    interview_stage=interview_stage,
                    interview_date=interview_date,
                    interview_questions=interview_questions,
                )
                memo.save(using="team_UD")

            return JsonResponse(
                {
                    "id": memo.id,
                    "title": memo.title,
                    "content": memo.content,
                    "company_id": memo.company.id if memo.company else None,
                    "company_name": memo.company.name if memo.company else "",
                    "interview_stage": memo.interview_stage,
                    "interview_date": memo.interview_date.strftime("%Y-%m-%d") if memo.interview_date else None,
                    "interview_questions": memo.interview_questions,
                    "date": memo.date.strftime("%Y-%m-%d"),
                    "created_at": memo.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": memo.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def delete_memo(request, memo_id):
    """メモを削除するAPI"""
    if request.method == "DELETE":
        try:
            # ログインチェック
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            user_id = request.session["user_id"]
            # 自分のメモのみ削除可能
            memo = Memo.objects.using("team_UD").get(id=memo_id, account_id=user_id)
            memo.delete(using="team_UD")
            return JsonResponse({"message": "削除しました"}, status=200)
        except Memo.DoesNotExist:
            return JsonResponse({"error": "メモが見つかりません"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# アカウント関連のビュー
def register_view(request):
    """アカウント登録ページ"""
    if request.method == "GET":
        return render(request, "teams/team_UD/register.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if not username or not password:
            return render(request, "teams/team_UD/register.html", {"error": "ユーザー名とパスワードは必須です"})
        
        # ユーザー名の重複チェック
        if Account.objects.using("team_UD").filter(username=username).exists():
            return render(request, "teams/team_UD/register.html", {"error": "このユーザー名は既に使用されています"})
        
        # アカウントを作成
        account = Account(username=username, password=password)
        account.save(using="team_UD")
        
        # セッションにユーザー情報を保存
        request.session["user_id"] = account.id
        request.session["username"] = account.username
        
        return redirect("team_UD:calendar")


def login_view(request):
    """ログインページ"""
    if request.method == "GET":
        return render(request, "teams/team_UD/login.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "teams/team_UD/login.html", {"error": "ユーザー名とパスワードを入力してください"})

        try:
            account = Account.objects.using("team_UD").get(username=username, password=password)
            # セッションにユーザー情報を保存
            request.session["user_id"] = account.id
            request.session["username"] = account.username
            return redirect("team_UD:calendar")
        except Account.DoesNotExist:
            return render(request, "teams/team_UD/login.html", {"error": "ユーザー名かパスワードのどちらかが間違っています"})
        except Exception as e:
            # 予期しないエラーの場合も、セキュリティのため詳細を隠す
            return render(request, "teams/team_UD/login.html", {"error": "ユーザー名かパスワードのどちらかが間違っています"})


def logout_view(request):
    """ログアウト"""
    if "user_id" in request.session:
        del request.session["user_id"]
    if "username" in request.session:
        del request.session["username"]
    return redirect("team_UD:login")


def statistics_view(request):
    """統計ページ"""
    # ログインチェック
    if "user_id" not in request.session:
        return redirect("team_UD:login")
    
    return render(request, "teams/team_UD/statistics.html")


@csrf_exempt
def get_statistics(request):
    """統計データを取得するAPI"""
    if request.method == "GET":
        try:
            # ログインチェック
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            search_query = request.GET.get("search", "").strip()
            
            # 面接系イベントのみを対象
            interview_stages = ['一次面接', '二次面接', '三次面接', '最終面接', 'グループディスカッション']
            
            # interview_questionsが空でないメモのみを取得
            memos = Memo.objects.using("team_UD").filter(
                interview_stage__in=interview_stages,
                interview_questions__isnull=False
            ).exclude(interview_questions='').select_related('company')
            
            # 会社名で検索
            if search_query:
                memos = memos.filter(company__name__icontains=search_query)
            
            # 会社×面接段階でグループ化
            statistics = {}
            for memo in memos:
                if not memo.company:
                    continue
                    
                company_name = memo.company.name
                stage = memo.interview_stage
                
                if company_name not in statistics:
                    statistics[company_name] = {}
                
                if stage not in statistics[company_name]:
                    statistics[company_name][stage] = []
                
                # 質問をリストに追加
                questions = memo.interview_questions.split('\n')
                for question in questions:
                    question = question.strip()
                    if question:
                        statistics[company_name][stage].append(question)
            
            # レスポンス用にフォーマット
            result = []
            for company_name in sorted(statistics.keys()):
                company_data = {
                    "company_name": company_name,
                    "stages": []
                }
                for stage in interview_stages:
                    if stage in statistics[company_name]:
                        company_data["stages"].append({
                            "stage": stage,
                            "questions": statistics[company_name][stage]
                        })
                if company_data["stages"]:
                    result.append(company_data)
            
            return JsonResponse({"statistics": result}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# 質問対策ページ
def questions_view(request):
    """質問対策ページ"""
    if "user_id" not in request.session:
        return redirect("team_UD:login")
    
    return render(request, "teams/team_UD/questions.html")


@csrf_exempt
def get_upcoming_companies(request):
    """今後予定がある会社のリストを取得"""
    if request.method == "GET":
        try:
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            user_id = request.session["user_id"]
            today = datetime.now().date()
            
            # 今日以降の予定がある会社を取得
            upcoming_memos = Memo.objects.using("team_UD").filter(
                account_id=user_id,
                date__gte=today,
                company__isnull=False
            ).select_related('company').order_by('date')
            
            # 会社ごとに最も近い予定日を取得
            companies = {}
            for memo in upcoming_memos:
                company_id = memo.company.id
                if company_id not in companies:
                    companies[company_id] = {
                        "id": company_id,
                        "name": memo.company.name,
                        "next_date": memo.date.strftime("%Y-%m-%d"),
                        "stage": memo.interview_stage
                    }
            
            return JsonResponse({"companies": list(companies.values())}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def get_company_questions(request, company_id):
    """特定の会社の質問リストを取得（過去の質問 + 回答状況）"""
    if request.method == "GET":
        try:
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            user_id = request.session["user_id"]
            
            # 会社情報を取得
            try:
                company = Company.objects.using("team_UD").get(id=company_id)
            except Company.DoesNotExist:
                return JsonResponse({"error": "会社が見つかりません"}, status=404)
            
            # 過去のメモから質問を抽出
            interview_stages = ['一次面接', '二次面接', '三次面接', '最終面接', 'グループディスカッション']
            memos = Memo.objects.using("team_UD").filter(
                company_id=company_id,
                interview_stage__in=interview_stages,
                interview_questions__isnull=False
            ).exclude(interview_questions='')
            
            # 質問を収集
            questions_from_memos = []
            for memo in memos:
                questions = memo.interview_questions.split('\n')
                for question in questions:
                    question = question.strip()
                    if question:
                        questions_from_memos.append({
                            "question": question,
                            "stage": memo.interview_stage,
                            "date": memo.interview_date.strftime("%Y-%m-%d") if memo.interview_date else None,
                            "memo_id": memo.id
                        })
            
            # ユーザーの回答を取得
            from .models import QuestionAnswer
            answers = QuestionAnswer.objects.using("team_UD").filter(
                account_id=user_id,
                company_id=company_id
            )
            
            answer_dict = {ans.question: ans for ans in answers}
            
            # 質問と回答をマージ
            result = []
            for q in questions_from_memos:
                question_text = q["question"]
                answer = answer_dict.get(question_text)
                result.append({
                    "question": question_text,
                    "stage": q["stage"],
                    "date": q["date"],
                    "memo_id": q["memo_id"],
                    "answer": answer.answer if answer else "",
                    "answer_id": answer.id if answer else None,
                    "has_answer": bool(answer and answer.answer)
                })
            
            return JsonResponse({
                "company_name": company.name,
                "questions": result
            }, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def save_question_answer(request):
    """質問への回答を保存"""
    if request.method == "POST":
        try:
            if "user_id" not in request.session:
                return JsonResponse({"error": "ログインが必要です"}, status=401)
            
            user_id = request.session["user_id"]
            data = json.loads(request.body)
            
            company_id = data.get("company_id")
            question = data.get("question")
            answer = data.get("answer", "")
            
            if not company_id or not question:
                return JsonResponse({"error": "会社と質問は必須です"}, status=400)
            
            account = Account.objects.using("team_UD").get(id=user_id)
            company = Company.objects.using("team_UD").get(id=company_id)
            
            from .models import QuestionAnswer
            # 既存の回答があれば更新、なければ作成
            answer_obj, created = QuestionAnswer.objects.using("team_UD").get_or_create(
                account=account,
                company=company,
                question=question,
                defaults={"answer": answer}
            )
            
            if not created:
                answer_obj.answer = answer
                answer_obj.save(using="team_UD")
            
            return JsonResponse({
                "message": "保存しました",
                "answer_id": answer_obj.id
            }, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

