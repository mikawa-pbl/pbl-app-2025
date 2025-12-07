import uuid

from django.test import TestCase

from team_terrace.models import ChatMessage, ChatRoom, Reaction, ThreadReply


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

    def test_create_chat_message(self):
        """ChatMessageが正しく作成できるかテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Message Test Room")

        message = ChatMessage.objects.using("team_terrace").create(room=room, content="Hello World")
        self.assertEqual(message.content, "Hello World")

    def test_message_manager_for_room(self):
        """ChatMessageManager.for_roomのテスト (Refactoring Red)."""
        room = ChatRoom.objects.using("team_terrace").create(title="Manager Test Room")

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
        parent = ChatMessage.objects.using("team_terrace").create(room=room, content="Question?", is_question=True)

        reply = ThreadReply.objects.using("team_terrace").create(parent_message=parent, content="Reply Answer")

        self.assertEqual(reply.parent_message, parent)
        self.assertEqual(reply.content, "Reply Answer")


class ReactionModelTests(TestCase):
    """リアクションモデルのテスト."""

    databases = "__all__"

    def test_create_reaction(self):
        """Reaction作成のテスト."""
        room = ChatRoom.objects.using("team_terrace").create(title="Reaction Room")
        reaction = Reaction.objects.using("team_terrace").create(room=room, reaction_type="like")

        self.assertEqual(reaction.reaction_type, "like")
        self.assertEqual(reaction.room, room)
        self.assertIsNotNone(reaction.created_at)
