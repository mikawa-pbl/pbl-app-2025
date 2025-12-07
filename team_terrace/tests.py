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

    def test_get_messages_polling(self):
        """ポーリング用の差分取得テスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Polling Room")
        from .models import ChatMessage

        m1 = ChatMessage.objects.using("team_terrace").create(room=room, content="Msg 1")
        m2 = ChatMessage.objects.using("team_terrace").create(room=room, content="Msg 2")

        # m1のID以降を取得
        url = reverse("team_terrace:get_messages", args=[room.uuid])
        response = self.client.get(url, {"after_id": m1.id})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # m2だけが返るはず
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["id"], m2.id)
        self.assertEqual(data["messages"][0]["content"], "Msg 2")

    def test_message_manager_for_room(self):
        """ChatMessageManager.for_roomのテスト (Refactoring Red)."""
        room = ChatRoom.objects.using("team_terrace").create(title="Manager Test Room")
        from .models import ChatMessage

        m1 = ChatMessage.objects.using("team_terrace").create(room=room, content="Msg 1")
        m2 = ChatMessage.objects.using("team_terrace").create(room=room, content="Msg 2")

        # Room指定のみ
        messages = ChatMessage.objects.using("team_terrace").for_room(room)
        self.assertEqual(len(messages), 2)

        # after_id 指定
        messages_after = ChatMessage.objects.using("team_terrace").for_room(room, after_id=m1.id)
        self.assertEqual(len(messages_after), 1)
        self.assertEqual(messages_after[0].id, m2.id)


class ThreadModelTests(TestCase):
    """スレッド機能に関連するモデルのテスト."""

    databases = "__all__"

    def test_create_thread_reply(self):
        """スレッド返信作成のテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Thread Room")
        # 親メッセージ（質問）
        from .models import ChatMessage  # 循環回避のため内部インポートまたはトップレベル移動検討

        parent = ChatMessage.objects.using("team_terrace").create(room=room, content="Question?", is_question=True)

        # 返信作成 (まだモデルがないのでImportError/NameErrorになるはず)
        from .models import ThreadReply

        reply = ThreadReply.objects.using("team_terrace").create(parent_message=parent, content="Reply Answer")

        self.assertEqual(reply.parent_message, parent)
        self.assertEqual(reply.content, "Reply Answer")


class ThreadAPITests(TestCase):
    """スレッドAPIのテスト."""

    databases = "__all__"

    def setUp(self):
        """テストデータのセットアップ."""
        from .models import ChatMessage

        self.room = ChatRoom.objects.using("team_terrace").create(title="Thread API Room")
        self.message = ChatMessage.objects.using("team_terrace").create(
            room=self.room, content="Question?", is_question=True
        )

    def test_post_reply(self):
        """返信投稿APIのテスト."""
        url = reverse("team_terrace:post_reply", args=[self.message.id])
        data = {"content": "Answer via API"}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        # 保存確認
        from .models import ThreadReply

        reply = ThreadReply.objects.using("team_terrace").first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, "Answer via API")
        self.assertEqual(reply.parent_message, self.message)

    def test_get_replies(self):
        """返信一覧取得APIのテスト."""
        from .models import ThreadReply

        ThreadReply.objects.using("team_terrace").create(parent_message=self.message, content="Reply 1")

        url = reverse("team_terrace:get_replies", args=[self.message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["replies"]), 1)
        self.assertEqual(data["replies"][0]["content"], "Reply 1")
