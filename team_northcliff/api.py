from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db.models import Prefetch
from datetime import timedelta
from django.utils import timezone
from .models import User, Facility, Post, FacilityAccess

# Helper function to format time difference in Japanese
def format_time_diff(dt):
    if not dt:
        return "情報なし"
    
    now = timezone.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "たった今"
    elif diff < timedelta(hours=1):
        minutes = diff.total_seconds() // 60
        return f"{int(minutes)}分前"
    elif diff < timedelta(days=1):
        hours = diff.total_seconds() // 3600
        return f"{int(hours)}時間前"
    else:
        days = diff.days
        return f"{days}日前"

@require_http_methods(["GET"])
def user_data_view(request, username):
    """ユーザー情報とポイント取得"""
    try:
        user = User.objects.using("team_northcliff").get(name=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'ユーザーが見つかりません'}, status=404)
    
    return JsonResponse({
        'user_id': user.id,
        'points': user.points,
    })

@require_http_methods(["GET"])
def facilities_view(request):
    """施設一覧と最新の投稿情報を取得"""
    facilities = Facility.objects.using("team_northcliff").all()
    result = []
    
    for facility in facilities:
        latest_post = facility.posts.using("team_northcliff").first()  # 最新の投稿を取得
        
        result.append({
            'id': facility.id,
            'name': facility.name,
            'latest_status': latest_post.status if latest_post else 'empty',
            'last_post_time': format_time_diff(latest_post.created_at if latest_post else None),
        })
    
    return JsonResponse({'facilities': result})

@require_http_methods(["POST"])
@csrf_protect
def access_facility_view(request, username):
    """施設情報にアクセス（ポイント消費）"""
    import json
    
    try:
        user = User.objects.using("team_northcliff").get(name=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'ユーザーが見つかりません'}, status=401)
    
    try:
        data = json.loads(request.body)
        facility_id = data.get('facility_id')
    except:
        return JsonResponse({'error': 'リクエストが無効です'}, status=400)
    
    facility = Facility.objects.using("team_northcliff").get(id=facility_id)
    
    # ポイント確認
    if user.points < 1:
        return JsonResponse({'error': 'ポイントが不足しています'}, status=400)
    
    # ポイント消費
    user.points -= 1
    user.save(using="team_northcliff")
    
    # FacilityAccess レコード作成（既存なら更新）
    FacilityAccess.objects.using("team_northcliff").get_or_create(user=user, facility=facility)
    
    return JsonResponse({
        'success': True,
        'points': user.points,
    })

@require_http_methods(["POST"])
@csrf_protect
def create_post_view(request, username):
    """新しい投稿を作成（ポイント獲得）"""
    import json
    
    try:
        user = User.objects.using("team_northcliff").get(name=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'ユーザーが見つかりません'}, status=401)
    
    try:
        data = json.loads(request.body)
        facility_id = data.get('facility_id')
        status = data.get('status')
        comment = data.get('comment')
    except:
        return JsonResponse({'error': 'リクエストが無効です'}, status=400)
    
    facility = Facility.objects.using("team_northcliff").get(id=facility_id)
    
    # Post レコード作成
    post = Post.objects.using("team_northcliff").create(
        user=user,
        facility=facility,
        status=status,
        comment=comment if comment else None,
    )
    
    # ポイント獲得
    user.points += 1
    user.save(using="team_northcliff")
    
    # 投稿者は自動的に施設にアクセス可能
    FacilityAccess.objects.using("team_northcliff").get_or_create(user=user, facility=facility)
    
    return JsonResponse({
        'success': True,
        'post_id': post.id,
        'points': user.points,
    })
