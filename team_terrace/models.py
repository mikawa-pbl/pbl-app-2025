from django.db import models
import uuid

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

class ChatMessage(models.Model):
    """チャットメッセージを表すモデル.

    Attributes:
        room (ChatRoom): メッセージが属するチャットルーム.
        content (str): メッセージの内容.
        created_at (datetime): メッセージの作成日時.
        is_question (bool): 質問かどうかを示すフラグ.
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_question = models.BooleanField(default=False)

    def __str__(self):
        """メッセージの文字列表現を返す.

        Returns:
            str: メッセージの内容（先頭20文字）.
        """
        return self.content[:20]
