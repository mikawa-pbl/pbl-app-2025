from django.test import TestCase
from django.urls import reverse
from .models import ChatRoom
import uuid


class ChatRoomModelTests(TestCase):
    """Tests for the ChatRoom model."""

    databases = "__all__"

    def test_create_chat_room(self):
        """ChatRoomが正しく作成できるかテスト."""
        title = "Test Room"
        room = ChatRoom.objects.using("team_terrace").create(title=title)

        self.assertEqual(room.title, title)
        self.assertIsInstance(room.uuid, uuid.UUID)
        self.assertIsNotNone(room.created_at)

        # 取得できるか確認
        fetched_room = ChatRoom.objects.using("team_terrace").get(uuid=room.uuid)
        self.assertEqual(fetched_room.title, title)

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

    def test_create_chat_message(self):
        """ChatMessageが正しく作成できるかテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Message Test Room")

        # Test creating a message via model directly (though we don't have the model yet)
        # Since we are TDD, this test is expected to fail with NameError until model is defined
        from .models import ChatMessage

        message = ChatMessage.objects.using("team_terrace").create(room=room, content="Hello World")
        self.assertEqual(message.content, "Hello World")

    def test_post_message_api(self):
        """メッセージ送信APIのテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="API Test Room")
        url = reverse("team_terrace:post_message", args=[room.uuid])
        data = {"content": "API Message"}

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        # 保存確認
        from .models import ChatMessage

        self.assertTrue(ChatMessage.objects.using("team_terrace").filter(room=room, content="API Message").exists())

    def test_get_messages_api(self):
        """メッセージ一覧取得APIのテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Get API Room")
        from .models import ChatMessage

        ChatMessage.objects.using("team_terrace").create(room=room, content="Msg 1")
        ChatMessage.objects.using("team_terrace").create(room=room, content="Msg 2")

        url = reverse("team_terrace:get_messages", args=[room.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["messages"]), 2)
        self.assertEqual(data["messages"][0]["content"], "Msg 1")
        self.assertEqual(data["messages"][1]["content"], "Msg 2")
