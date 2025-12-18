from django.test import TestCase
from django.urls import reverse

from team_terrace.models import ChatMessage, ChatRoom, Reaction, ThreadReply


class MessageAPITests(TestCase):
    """メッセージ関連APIのテスト."""

    databases = "__all__"

    def test_post_message_api(self):
        """メッセージ送信APIのテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="API Test Room")
        url = reverse("team_terrace:post_message", args=[room.uuid])
        data = {"content": "API Message"}

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        # 保存確認
        self.assertTrue(ChatMessage.objects.using("team_terrace").filter(room=room, content="API Message").exists())

    def test_get_messages_api(self):
        """メッセージ一覧取得APIのテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Get API Room")

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


class ThreadAPITests(TestCase):
    """スレッドAPIのテスト."""

    databases = "__all__"

    def setUp(self):
        """テストデータのセットアップ."""
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
        reply = ThreadReply.objects.using("team_terrace").first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, "Answer via API")
        self.assertEqual(reply.parent_message, self.message)

    def test_post_like(self):
        """いいね投稿APIのテスト."""
        url = reverse("team_terrace:post_like", args=[self.message.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data["like_count"], 1)

        # DB確認
        self.message.refresh_from_db()
        self.assertEqual(self.message.like_count, 1)

    def test_post_unlike(self):
        """いいね解除APIのテスト."""
        # 先にいいねしておく
        self.message.like_count = 1
        self.message.save()

        url = reverse("team_terrace:post_unlike", args=[self.message.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["like_count"], 0)

        # DB確認
        self.message.refresh_from_db()
        self.assertEqual(self.message.like_count, 0)

    def test_get_replies(self):
        """返信一覧取得APIのテスト."""
        ThreadReply.objects.using("team_terrace").create(parent_message=self.message, content="Reply 1")

        url = reverse("team_terrace:get_replies", args=[self.message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data["replies"]), 1)
        self.assertEqual(data["replies"][0]["content"], "Reply 1")


class ReactionAPITests(TestCase):
    """リアクションAPIのテスト."""

    databases = "__all__"

    def setUp(self):
        """テストデータのセットアップ."""
        self.room = ChatRoom.objects.using("team_terrace").create(title="Reaction API Room")

    def test_post_reaction(self):
        """リアクション投稿APIのテスト."""
        url = reverse("team_terrace:post_reaction", args=[self.room.uuid])
        data = {"reaction_type": "love"}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        self.assertTrue(Reaction.objects.using("team_terrace").filter(room=self.room, reaction_type="love").exists())

    def test_get_reactions(self):
        """リアクション取得APIのテスト."""
        Reaction.objects.using("team_terrace").create(room=self.room, reaction_type="laugh")

        url = reverse("team_terrace:get_reactions", args=[self.room.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(len(data["reactions"]) > 0)
        self.assertEqual(data["reactions"][0]["reaction_type"], "laugh")
