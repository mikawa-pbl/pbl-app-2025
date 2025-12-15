from django.shortcuts import render, redirect
from .models import Member, Reservation, Notification
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime
import pytz
from django.conf import settings
from django.core import signing

# --- 既存の簡易ビュー ---
def index(request):
    return render(request, 'teams/team_scim/index.html')

def members(request):
    qs = Member.objects.using('team_scim').all()
    return render(request, 'teams/team_scim/members.html', {'members': qs})


# --- 認証関連 ---
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

def logout_view(request):
    """ ログアウト """
    response = redirect('team_scim:login')
    response.delete_cookie('user_role')
    return response


# --- メイン画面 ---
def home_view(request):
    """ ホーム画面（カレンダー表示 + 通知） """

    # 1. ログインチェック
    signed_role = request.COOKIES.get('user_role')
    try:
        user_role = signing.loads(signed_role)
    except Exception:
        return redirect('team_scim:login')

    # 2. 予約データの取得
    reservations = Reservation.objects.all()
    events_list = []

    for reservation in reservations:
        # ステータスに応じたCSSクラス
        css_class = 'status-default'
        if reservation.status == 'pending_signature':
            css_class = 'status-pending-signature' # 黄色（署名待ち）
        elif reservation.status == 'pending_approval':
            css_class = 'status-pending-approval'  # オレンジ（承認待ち）
        elif reservation.status == 'approved':
            css_class = 'status-approved'          # 緑（完了）
        elif reservation.status == 'rejected':
            css_class = 'status-rejected'          # 赤（却下）

        events_list.append({
            'title': f"{reservation.facility_name} ({reservation.get_status_display()})",
            'start': reservation.start_time,
            'end': reservation.end_time,
            'applicant': reservation.applicant_name,
            'className': css_class,
            'extendedProps': {
                'status': reservation.status,
                'status_display': reservation.get_status_display(),
                'applicant': reservation.applicant_name,
                'signer': reservation.signer_name,
                'comment': reservation.approver_comment
            }
        })

    events_json = json.dumps(events_list, cls=DjangoJSONEncoder)

    # 3. 通知の取得 (現在の役職宛のものだけ)
    notifications = Notification.objects.filter(recipient_role=user_role).order_by('-created_at')

    facility_list = ["会議室A", "会議室B", "体育館", "音楽室"]

    context = {
        'events_json': events_json,
        'facilities': facility_list,
        'user_role': user_role,
        'user_role_display': get_role_display(user_role),
        'notifications': notifications, # 通知リストを渡す
    }
    return render(request, 'teams/team_scim/home.html', context)


def get_role_display(role_key):
    roles = {
        'applicant': '申請者',
        'signer': '署名者（責任者）',
        'approver': '承認者',
    }
    return roles.get(role_key, 'ゲスト')


# --- 予約作成処理 ---
def create_reservation_view(request):
    """ (AJAX用) 予約作成ビュー """

    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    try:
        data = json.loads(request.body)
        date_str = data.get('date_str')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        facility_name = data.get('facility_name')
        signer_name = data.get('signer_name') # 責任者名を取得

        if not all([date_str, start_time_str, end_time_str, facility_name, signer_name]):
            return JsonResponse({'status': 'error', 'message': '必須項目が不足しています。'}, status=400)

        tz = pytz.timezone(settings.TIME_ZONE)
        try:
            start_dt = tz.localize(datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M"))
            end_dt = tz.localize(datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M"))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': '日時の形式が正しくありません。'}, status=400)

        if start_dt >= end_dt:
            return JsonResponse({'status': 'error', 'message': '終了時間は開始時間より後に設定してください。'}, status=400)

        # 重複チェック (承認済み or 承認待ち or 署名待ち のものと重複したらNG)
        overlapping = Reservation.objects.filter(
            facility_name=facility_name,
            status__in=['pending_signature', 'pending_approval', 'approved'],
            start_time__lt=end_dt,
            end_time__gt=start_dt
        ).exists()

        if overlapping:
            return JsonResponse({'status': 'error', 'message': 'その時間帯は既に予約または申請がされています。'}, status=409)

        # 予約作成 (ステータス: 署名待ち)
        new_reservation = Reservation.objects.create(
            facility_name=facility_name,
            applicant_name="（仮）申請者",
            signer_name=signer_name,
            start_time=start_dt,
            end_time=end_dt,
            status='pending_signature' # 初期ステータス
        )

        # 【通知作成】 署名者へ通知
        Notification.objects.create(
            recipient_role='signer',
            message=f"【署名依頼】{new_reservation.applicant_name}さんが「{facility_name}」の予約申請を出しました。",
            reservation=new_reservation
        )

        response_data = {
            'status': 'success',
            'message': '予約申請が完了しました。責任者へ署名依頼を送信しました。',
            # カレンダー反映用データ
            'newEvent': {
                'title': f"{new_reservation.facility_name} (署名待ち)",
                'start': new_reservation.start_time.isoformat(),
                'end': new_reservation.end_time.isoformat(),
                'applicant': new_reservation.applicant_name,
                'className': 'status-pending-signature',
                'extendedProps': {
                    'status': new_reservation.status,
                    'status_display': new_reservation.get_status_display(),
                    'applicant': new_reservation.applicant_name,
                    'signer': new_reservation.signer_name
                }
            }
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'サーバーエラー: {str(e)}'}, status=500)


# --- 新規追加: 通知処理（署名・承認・却下） ---
def process_notification_view(request):
    """ 通知からのアクション処理 """
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        notification_id = data.get('notification_id')
        action = data.get('action') # 'sign', 'approve', 'reject'
        comment = data.get('comment', '') # 承認者コメント

        reservation = Reservation.objects.get(id=reservation_id)

        # 通知を削除 (処理済みとするため)
        Notification.objects.filter(id=notification_id).delete()

        new_status = ''
        message_to_next = ''

        # --- 署名アクション ---
        if action == 'sign':
            reservation.status = 'pending_approval'
            reservation.save()

            # 承認者へ通知を作成
            Notification.objects.create(
                recipient_role='approver',
                message=f"【承認依頼】{reservation.signer_name}さんが「{reservation.facility_name}」の利用申請に署名しました。",
                reservation=reservation
            )
            return JsonResponse({'status': 'success', 'message': '署名しました。承認者へ通知を送りました。'})

        # --- 承認アクション ---
        elif action == 'approve':
            reservation.status = 'approved'
            reservation.approver_comment = comment
            reservation.save()

            # 申請者へ結果通知
            Notification.objects.create(
                recipient_role='applicant',
                message=f"【承認完了】「{reservation.facility_name}」の予約が承認されました。(コメント: {comment})",
                reservation=reservation
            )
            return JsonResponse({'status': 'success', 'message': '承認しました。申請者へ通知を送りました。'})

        # --- 却下アクション ---
        elif action == 'reject':
            reservation.status = 'rejected'
            reservation.approver_comment = comment
            reservation.save()

            # 申請者へ結果通知
            Notification.objects.create(
                recipient_role='applicant',
                message=f"【却下】「{reservation.facility_name}」の予約が却下されました。(理由: {comment})",
                reservation=reservation
            )
            return JsonResponse({'status': 'success', 'message': '却下しました。申請者へ通知を送りました。'})

        else:
            return JsonResponse({'status': 'error', 'message': '不正な操作です。'}, status=400)

    except Reservation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '予約データが見つかりません。'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)