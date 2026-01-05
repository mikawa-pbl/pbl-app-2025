from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db.models import Prefetch
from datetime import timedelta
from django.utils import timezone
from .models import User, Facility, Post, FacilityAccess
from math import radians, sin, cos, sqrt, atan2

# Helper function to calculate distance between two lat/lon points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

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
    """ユーザー情報とポイント、位置情報を取得"""
    try:
        user = User.objects.using("team_northcliff").get(name=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'ユーザーが見つかりません'}, status=404)
    
    return JsonResponse({
        'user_id': user.id,
        'points': user.points,
        'latitude': user.latitude,
        'longitude': user.longitude,
    })

@require_http_methods(["GET"])
def facilities_view(request):
    """施設一覧と最新の投稿情報を取得"""
    facilities = Facility.objects.using("team_northcliff").all()
    result = []
    now = timezone.now()
    ten_minutes_ago = now - timedelta(minutes=10)
    
    for facility in facilities:
        # 最新の投稿（ステータス表示用）
        latest_post = facility.posts.using("team_northcliff").order_by('-created_at').first()
        
        # 過去10分以内のコメントを最大3件取得（最新順）
        recent_posts_qs = Post.objects.using("team_northcliff").filter(
            facility=facility,
            created_at__gte=ten_minutes_ago
        ).order_by('-created_at')[:3]
        
        recent_comments = []
        for p in recent_posts_qs:
            if p.comment:
                recent_comments.append({
                    'comment': p.comment,
                    'time_ago': format_time_diff(p.created_at),
                })
        
        result.append({
            'id': facility.id,
            'name': facility.name,
            'latitude': facility.latitude,
            'longitude': facility.longitude,
            'latest_status': latest_post.status if latest_post else 'empty',
            'last_post_time': format_time_diff(latest_post.created_at if latest_post else None),
            'recent_comments': recent_comments,
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

    # --- 距離チェック: ユーザーが施設から100m以内にいるか ---
    if user.latitude and user.longitude and facility.latitude and facility.longitude:
        distance = haversine(user.latitude, user.longitude, facility.latitude, facility.longitude)
        if distance > 100:
            return JsonResponse(
                {'error': '施設から100m以上離れているため、投稿できません。'},
                status=403
            )
    else:
        # ユーザーまたは施設の位置情報がない場合は投稿を許可しない
        return JsonResponse(
            {'error': '位置情報が利用できないため、投稿できません。'},
            status=403
        )

    # --- クールタイム: 同一ユーザーが同一施設に10分以内に投稿していないかチェック ---
    ten_minutes_ago = timezone.now() - timedelta(minutes=10)
    recent_same_posts = Post.objects.using("team_northcliff").filter(
        user=user,
        facility=facility,
        created_at__gte=ten_minutes_ago
    ).order_by('-created_at')
    if recent_same_posts.exists():
        return JsonResponse(
            {'error': '１０分以内に同一の施設情報を投稿することはできません'},
            status=400
        )
    
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

@require_http_methods(["GET"])
def users_list_view(request):
    """全ユーザーのリストを取得"""
    users = User.objects.using("team_northcliff").all().order_by('id')
    user_list = [{'name': u.name} for u in users]
    return JsonResponse({'users': user_list})
