from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from .models import ChatRoom


class IndexView(TemplateView):
    """インデックスページを表示するビュー."""

    template_name = "teams/team_terrace/index.html"

    def post(self, request, *args, **kwargs):
        """ルーム作成を処理する."""
        title = request.POST.get("title")
        if title:
            room = ChatRoom.objects.using("team_terrace").create(title=title)
            return redirect("team_terrace:room", room_id=room.uuid)
        return self.render_to_response(self.get_context_data())


class RoomView(TemplateView):
    """チャットルームページを表示するビュー."""

    template_name = "teams/team_terrace/room.html"

    def get_context_data(self, **kwargs):
        """コンテキストデータを取得する."""
        context = super().get_context_data(**kwargs)
        room_id = kwargs.get("room_id")
        context["room"] = get_object_or_404(ChatRoom.objects.using("team_terrace"), uuid=room_id)
        return context
