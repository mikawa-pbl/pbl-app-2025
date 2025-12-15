from django.shortcuts import render, redirect
from .models import Member, Reservation
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime
import pytz
from django.conf import settings
from django.core import signing


def index(request):
    return render(request, 'teams/team_scim/index.html')


def members(request):
    qs = Member.objects.using('team_scim').all()
    return render(request, 'teams/team_scim/members.html', {'members': qs})


# ⬇️ 疑似ログイン（署名付き Cookie 版）⬇️
def login_view(request):
    """ 疑似ログイン画面 """
    if request.method == 'POST':
        role = request.POST.get('role')

        if role in ['applicant', 'signer', 'approver']:
            response = redirect('team_scim:home')
            signed_role = signing.dumps(role)
            response.set_cookie(
                'user_role',
                signed_role,
                httponly=True,
                samesite='Lax'
            )
            return response

    return render(request, 'teams/team_scim/login.html')


# ⬇️ ログアウト ⬇️
def logout_view(request):
    """ ログアウト（Cookie 削除） """
    response = redirect('team_scim:login')
    response.delete_cookie('user_role')
    return response


def home_view(request):
    """ ホーム画面（カレンダー表示） """

    # ⬇️ ログインチェック ⬇️
    signed_role = request.COOKIES.get('user_role')
    try:
        user_role = signing.loads(signed_role)
    except Exception:
        return redirect('team_scim:login')

    reservations = Reservation.objects.all()
    events_list = []

    for reservation in reservations:
        events_list.append({
            'title': f"{reservation.facility_name} ({reservation.get_status_display()})",
            'start': reservation.start_time,
            'end': reservation.end_time,
            'applicant': reservation.applicant_name,
            'className': f'status-{reservation.status}',
            'extendedProps': {
                'status': reservation.status,
                'applicant': reservation.applicant_name
            }
        })

    events_json = json.dumps(events_list, cls=DjangoJSONEncoder)

    facility_list = ["会議室A", "会議室B", "体育館", "音楽室"]

    context = {
        'events_json': events_json,
        'facilities': facility_list,
        'user_role': user_role,
        'user_role_display': get_role_display(user_role),
    }
    return render(request, 'teams/team_scim/home.html', context)


def get_role_display(role_key):
    """ 役職キーを日本語に変換する """
    roles = {
        'applicant': '申請者',
        'signer': '署名者（責任者）',
        'approver': '承認者',
    }
    return roles.get(role_key, 'ゲスト')


def create_reservation_view(request):
    """ (AJAX用) 予約作成ビュー（重複チェック対応） """

    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    try:
        data = json.loads(request.body)
        date_str = data.get('date_str')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        facility_name = data.get('facility_name')

        if not all([date_str, start_time_str, end_time_str, facility_name]):
            return JsonResponse(
                {'status': 'error', 'message': '必須項目が不足しています。'},
                status=400
            )

        tz = pytz.timezone(settings.TIME_ZONE)

        try:
            start_dt = tz.localize(
                datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            )
            end_dt = tz.localize(
                datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
            )
        except ValueError:
            return JsonResponse(
                {'status': 'error', 'message': '日時の形式が正しくありません。'},
                status=400
            )

        if start_dt >= end_dt:
            return JsonResponse(
                {'status': 'error', 'message': '終了時間は開始時間より後に設定してください。'},
                status=400
            )

        overlapping_reservations = Reservation.objects.filter(
            facility_name=facility_name,
            status__in=['pending', 'approved'],
            start_time__lt=end_dt,
            end_time__gt=start_dt
        ).exists()

        if overlapping_reservations:
            return JsonResponse(
                {'status': 'error', 'message': 'その時間帯は既に予約または申請がされています。'},
                status=409
            )

        new_reservation = Reservation.objects.create(
            facility_name=facility_name,
            applicant_name="（仮）申請者",
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
                'className': f'status-{new_reservation.status}',
                'extendedProps': {
                    'status': new_reservation.status,
                    'applicant': new_reservation.applicant_name
                }
            }
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format")
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': f'サーバーエラー: {str(e)}'},
            status=500
        )
