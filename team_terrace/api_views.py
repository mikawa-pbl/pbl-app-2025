import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import ChatMessage, ChatRoom


class PostMessageView(View):
    """メッセージを投稿するAPI."""

    def post(self, request, room_id):
        """メッセージ投稿処理."""
        room = get_object_or_404(ChatRoom.objects.using("team_terrace"), uuid=room_id)
        try:
            data = json.loads(request.body)
            content = data.get("content")
            is_question = data.get("is_question", False)

            if content:
                msg = ChatMessage.objects.using("team_terrace").create(
                    room=room, content=content, is_question=is_question
                )
                return JsonResponse({"id": msg.id, "content": msg.content, "is_question": msg.is_question}, status=201)
            return JsonResponse({"error": "Content is required"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


class GetMessagesView(View):
    """メッセージ一覧を取得するAPI."""

    def get(self, request, room_id):
        """メッセージ一覧取得処理."""
        room = get_object_or_404(ChatRoom.objects.using("team_terrace"), uuid=room_id)
        after_id = request.GET.get("after_id")
        messages = ChatMessage.objects.using("team_terrace").for_room(room, after_id)

        data = [{"id": m.id, "content": m.content, "is_question": m.is_question} for m in messages]
        return JsonResponse({"messages": data})


class PostReplyView(View):
    """スレッドへの返信を投稿するAPI."""

    def post(self, request, message_id):
        """返信投稿処理."""
        try:
            data = json.loads(request.body)
            content = data.get("content")
            if not content:
                return JsonResponse({"error": "Content is required"}, status=400)

            message = get_object_or_404(ChatMessage.objects.using("team_terrace"), id=message_id)
            reply = message.reply(content)

            return JsonResponse(
                {"id": reply.id, "content": reply.content, "created_at": reply.created_at.isoformat()}, status=201
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


class GetRepliesView(View):
    """スレッドの返信一覧を取得するAPI."""

    def get(self, request, message_id):
        """返信一覧取得処理."""
        message = get_object_or_404(ChatMessage.objects.using("team_terrace"), id=message_id)
        replies = message.get_replies()

        data = [{"id": r.id, "content": r.content, "created_at": r.created_at.isoformat()} for r in replies]

        return JsonResponse({"replies": data})
