from django.shortcuts import render
from .models import Member, Reservation
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime, timedelta
import pytz
from django.conf import settings
from django.db.models import Q # ⬅️ 複雑なクエリのために Q をインポート

def index(request):
    return render(request, 'teams/team_scim/index.html')

def members(request):
    qs = Member.objects.using('team_scim').all()
    return render(request, 'teams/team_scim/members.html', {'members': qs})

def home_view(request):
    """ ホーム画面（カレンダー表示） """
    
    reservations = Reservation.objects.all()
    events_list = []
    for reservation in reservations:
        events_list.append({
            'title': f"{reservation.facility_name} ({reservation.get_status_display()})",
            'start': reservation.start_time,
            'end': reservation.end_time,
            'applicant': reservation.applicant_name,
            'className': f'status-{reservation.status}' 
        })
    
    events_json = json.dumps(events_list, cls=DjangoJSONEncoder)

    # ⬇️ （仮の）施設マスタ。本当は Facility モデルを作るのがベストです。
    facility_list = ["テニスコート", "サカキパーク", "教室A", "教室B"]

    context = {
        'events_json': events_json,
        'facilities': facility_list, # ⬅️ 施設リストをテンプレートに渡す
    }
    return render(request, 'teams/team_scim/home.html', context)


# ⬇️ 予約作成ビューを大幅に変更 (重複チェック機能) ⬇️

def create_reservation_view(request):
    """ (AJAX/Fetch用) 予約作成ビュー (重複チェック対応) """
    
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    try:
        data = json.loads(request.body)
        date_str = data.get('date_str')
        start_time_str = data.get('start_time') # "HH:MM"
        end_time_str = data.get('end_time')     # "HH:MM"
        facility_name = data.get('facility_name')
        
        if not all([date_str, start_time_str, end_time_str, facility_name]):
            return JsonResponse({'status': 'error', 'message': '必須項目が不足しています。'}, status=400)

        # タイムゾーン設定
        tz = pytz.timezone(settings.TIME_ZONE)
        
        # 文字列を datetime オブジェクトに結合・変換
        try:
            start_dt = tz.localize(datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M"))
            end_dt = tz.localize(datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M"))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': '日時の形式が正しくありません。'}, status=400)

        if start_dt >= end_dt:
            return JsonResponse({'status': 'error', 'message': '終了時間は開始時間より後に設定してください。'}, status=400)

        # --- 予約重複チェック ---
        # 以下の条件に一致する予約を検索
        # 1. 施設名が同じ
        # 2. ステータスが「却下(rejected)」以外 (申請中 or 承認済み)
        # 3. 時間帯が重複している
        
        overlapping_reservations = Reservation.objects.filter(
            facility_name=facility_name,
            status__in=['pending', 'approved'],
            start_time__lt=end_dt, # (既存の開始 < 新規の終了)
            end_time__gt=start_dt  # (既存の終了 > 新規の開始)
        ).exists() # .exists() で、存在するかどうか (True/False) だけを取得

        if overlapping_reservations:
            # 重複がある場合
            return JsonResponse({'status': 'error', 'message': 'その時間帯は既に予約または申請がされています。'}, status=409) # 409 Conflict

        # --- 重複がない場合、予約を作成 ---
        new_reservation = Reservation.objects.create(
            facility_name=facility_name,
            applicant_name="（仮）申請者", # 本来はログインユーザー情報など
            start_time=start_dt,
            end_time=end_dt,
            status='pending'
        )

        response_data = {
            'status': 'success',
            'message': '予約申請が完了しました。',
            'newEvent': {
                'title': f"{new_reservation.facility_name} ({new_reservation.get_status_display()})",
                'start': new_reservation.start_time.isoformat(),
                'end': new_reservation.end_time.isoformat(),
                'applicant': new_reservation.applicant_name,
                'className': f'status-{new_reservation.status}'
            }
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'サーバーエラー: {str(e)}'}, status=500)