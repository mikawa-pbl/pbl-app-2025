from django.test import TestCase
from django.urls import reverse

from team_terrace.models import ChatRoom


class RoomViewTests(TestCase):
    """画面表示のテスト."""

    databases = "__all__"

    def test_create_room_view(self):
        """ルーム作成ビューのテスト."""
        url = reverse("team_terrace:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team Terrace")

        # POSTでルーム作成
        response = self.client.post(url, {"title": "New Room"})
        # 作成されたルームを確認
        room = ChatRoom.objects.using("team_terrace").last()
        self.assertIsNotNone(room)
        self.assertEqual(room.title, "New Room")

        # リダイレクト確認
        self.assertRedirects(response, reverse("team_terrace:room", args=[room.uuid]))

    def test_room_view(self):
        """ルーム画面の表示テスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Test Room View")
        url = reverse("team_terrace:room", args=[room.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Room View")
