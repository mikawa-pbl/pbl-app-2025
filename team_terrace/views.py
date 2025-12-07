from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom


def index(request):
    """インデックスページをレンダリングし、ルーム作成を処理する.

    Args:
        request: HTTPリクエストオブジェクト.

    Returns:
        HttpResponse: レンダリングされたインデックスページ、または作成されたルームへのリダイレクト.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        if title:
            room = ChatRoom.objects.using("team_terrace").create(title=title)
            return redirect("team_terrace:room", room_id=room.uuid)
    return render(request, "teams/team_terrace/index.html")


def room(request, room_id):
    """チャットルームページをレンダリングする.

    Args:
        request: HTTPリクエストオブジェクト.
        room_id (uuid): 取得するチャットルームのUUID.

    Returns:
        HttpResponse: レンダリングされたチャットルームページ.
    """
    room = get_object_or_404(ChatRoom.objects.using("team_terrace"), uuid=room_id)
    return render(request, "teams/team_terrace/room.html", {"room": room})


def post_message(request, room_id):
    """メッセージを投稿するAPI.

    Args:
        request: HTTPリクエストオブジェクト.
        room_id (uuid): チャットルームのUUID.

    Returns:
        JsonResponse: 作成されたメッセージの情報.
    """
    if request.method == "POST":
        import json
        from django.http import JsonResponse
        from .models import ChatMessage

        room = get_object_or_404(ChatRoom.objects.using("team_terrace"), uuid=room_id)
        data = json.loads(request.body)
        content = data.get("content")

        if content:
            msg = ChatMessage.objects.using("team_terrace").create(room=room, content=content)
            return JsonResponse({"id": msg.id, "content": msg.content}, status=201)
    return JsonResponse({"error": "Invalid request"}, status=400)


def get_messages(request, room_id):
    """メッセージ一覧を取得するAPI.

    Args:
        request: HTTPリクエストオブジェクト.
        room_id (uuid): チャットルームのUUID.

    Returns:
        JsonResponse: メッセージのリスト.
    """
    from django.http import JsonResponse
    from .models import ChatMessage

    room = get_object_or_404(ChatRoom.objects.using("team_terrace"), uuid=room_id)
    after_id = request.GET.get("after_id")
    messages = ChatMessage.objects.using("team_terrace").for_room(room, after_id)

    data = [{"id": m.id, "content": m.content, "is_question": m.is_question} for m in messages]
    return JsonResponse({"messages": data})
