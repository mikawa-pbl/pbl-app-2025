from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom

def index(request):
    """インデックスページをレンダリングし、ルーム作成を処理する.

    Args:
        request: HTTPリクエストオブジェクト.

    Returns:
        HttpResponse: レンダリングされたインデックスページ、または作成されたルームへのリダイレクト.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            room = ChatRoom.objects.using('team_terrace').create(title=title)
            return redirect('team_terrace:room', room_id=room.uuid)
    return render(request, 'teams/team_terrace/index.html')

def room(request, room_id):
    """チャットルームページをレンダリングする.

    Args:
        request: HTTPリクエストオブジェクト.
        room_id (uuid): 取得するチャットルームのUUID.

    Returns:
        HttpResponse: レンダリングされたチャットルームページ.
    """
    room = get_object_or_404(ChatRoom.objects.using('team_terrace'), uuid=room_id)
    return render(request, 'teams/team_terrace/room.html', {'room': room})