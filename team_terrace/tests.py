from django.test import TestCase
from django.urls import reverse
from .models import ChatRoom
import uuid

class ChatRoomModelTests(TestCase):
    """Tests for the ChatRoom model."""

    databases = '__all__'

    def test_create_chat_room(self):
        """ChatRoomが正しく作成できるかテスト."""
        title = "Test Room"
        room = ChatRoom.objects.using('team_terrace').create(title=title)
        
        self.assertEqual(room.title, title)
        self.assertIsInstance(room.uuid, uuid.UUID)
        self.assertIsNotNone(room.created_at)
        
        # 取得できるか確認
        fetched_room = ChatRoom.objects.using('team_terrace').get(uuid=room.uuid)
        self.assertEqual(fetched_room.title, title)

    def test_create_room_view(self):
        """ルーム作成ビューのテスト."""
        url = reverse('team_terrace:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team Terrace")

        # POSTでルーム作成
        response = self.client.post(url, {'title': 'New Room'})
        # 作成されたルームを確認
        room = ChatRoom.objects.using('team_terrace').last()
        self.assertIsNotNone(room)
        self.assertEqual(room.title, 'New Room')
        
        # リダイレクト確認
        self.assertRedirects(response, reverse('team_terrace:room', args=[room.uuid]))

    def test_room_view(self):
        """ルーム画面の表示テスト."""
        room = ChatRoom.objects.using('team_terrace').create(title="Test Room View")
        url = reverse('team_terrace:room', args=[room.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Room View")

    def test_create_chat_message(self):
        """ChatMessageが正しく作成できるかテスト."""
        room = ChatRoom.objects.using('team_terrace').create(title="Message Test Room")
        
        # Test creating a message via model directly (though we don't have the model yet)
        # Since we are TDD, this test is expected to fail with NameError until model is defined
        from .models import ChatMessage
        message = ChatMessage.objects.using('team_terrace').create(
            room=room,
            content="Hello World"
        )
        self.assertEqual(message.content, "Hello World")
        self.assertEqual(message.room, room)
        self.assertFalse(message.is_question)
