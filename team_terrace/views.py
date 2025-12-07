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
        is_question = data.get("is_question", False)

        if content:
            msg = ChatMessage.objects.using("team_terrace").create(room=room, content=content, is_question=is_question)
            return JsonResponse({"id": msg.id, "content": msg.content, "is_question": msg.is_question}, status=201)
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


def post_reply(request, message_id):
    """スレッドへの返信を投稿するAPI.

    Args:
        request (HttpRequest): リクエストオブジェクト.
        message_id (int): 親メッセージ（質問）のID.

    Returns:
        JsonResponse: 作成された返信データ.
    """
    import json
    from django.http import JsonResponse
    from .models import ChatMessage, ThreadReply

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        content = data.get("content")
        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)
        
        message = get_object_or_404(ChatMessage.objects.using('team_terrace'), id=message_id)
        reply = message.reply(content)
        
        return JsonResponse({
            "id": reply.id,
            "content": reply.content,
            "created_at": reply.created_at.isoformat()
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def get_replies(request, message_id):
    """スレッドの返信一覧を取得するAPI.

    Args:
        request (HttpRequest): リクエストオブジェクト.
        message_id (int): 親メッセージ（質問）のID.

    Returns:
        JsonResponse: 返信一覧データ.
    """
    import json
    from django.http import JsonResponse
    from .models import ChatMessage
    message = get_object_or_404(ChatMessage.objects.using('team_terrace'), id=message_id)
    replies = message.get_replies()
    
    data = [{
        "id": r.id,
        "content": r.content,
        "created_at": r.created_at.isoformat()
    } for r in replies]
    
    return JsonResponse({"replies": data})
