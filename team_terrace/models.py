from __future__ import annotations

import uuid

from django.db import models

class DammyModel(models.Model):
    """migrationを行わない、ダミーのモデル."""
    name = models.CharField(max_length=100)

class Member(models.Model):
    """チームメンバーを表すモデル.

    Attributes:
        first_name (str): メンバーの名.
        last_name (str): メンバーの姓.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        """メンバーのフルネームを返す."""
        return f"{self.last_name} {self.first_name}"


class ChatRoom(models.Model):
    """チャットルームを表すモデル.

    Attributes:
        uuid (UUID): チャットルームの一意な識別子.
        title (str): チャットルームのタイトル.
        created_at (datetime): チャットルームが作成された日時.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """ChatRoomの文字列表現を返す.

        Returns:
            str: チャットルームのタイトル.
        """
        return self.title


class ChatMessageQuerySet(models.QuerySet):
    """ChatMessageのカスタムQuerySet."""

    def for_room(self, room: ChatRoom, after_id: int | None = None):
        """指定されたルームのメッセージを取得する.

        Args:
            room (ChatRoom): 対象のチャットルーム.
            after_id (int, optional): このID以降のメッセージを取得する.

        Returns:
            QuerySet: メッセージのクエリセット.
        """
        qs = self.filter(room=room).order_by("created_at")
        if after_id:
            qs = qs.filter(id__gt=after_id)
        return qs


class ChatMessage(models.Model):
    """チャットメッセージを表すモデル.

    Attributes:
        room (ChatRoom): メッセージが属するチャットルーム.
        content (str): メッセージの内容.
        created_at (datetime): メッセージの作成日時.
        is_question (bool): 質問かどうかを示すフラグ.
    """

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_question = models.BooleanField(default=False)
    like_count = models.IntegerField(default=0)

    objects = ChatMessageQuerySet.as_manager()

    def reply(self, content: str):
        """スレッドへの返信を作成する.

        Args:
            content (str): 返信内容.

        Returns:
            ThreadReply: 作成された返信オブジェクト.
        """
        return self.replies.create(content=content)

    def get_replies(self):
        """スレッドの返信一覧を取得する.

        Returns:
            QuerySet: 返信のクエリセット.
        """
        return self.replies.all().order_by("created_at")

    def __str__(self):
        """メッセージの文字列表現を返す.

        Returns:
            str: メッセージの内容（先頭20文字）.
        """
        return self.content[:20]


class ThreadReply(models.Model):
    """スレッドへの返信を表すモデル.

    Attributes:
        parent_message (ChatMessage): 返信元のメッセージ（質問）.
        content (str): 返信内容.
        created_at (datetime): 作成日時.
    """

    parent_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """返信の文字列表現を返す."""
        return f"Reply to {self.parent_message_id}: {self.content[:20]}"


class Reaction(models.Model):
    """リアクションを表すモデル.

    Attributes:
        room (ChatRoom): リアクションが行われたルーム.
        reaction_type (str): リアクションの種類 (like, love, laugh, surprised).
        created_at (datetime): 作成日時.
    """

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="reactions")
    reaction_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """文字列表現."""
        return f"{self.reaction_type} in {self.room}"
