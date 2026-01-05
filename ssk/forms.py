# ssk/forms.py
from django import forms
from django.forms.widgets import DateInput
from django.forms.widgets import PasswordInput
from django.core.exceptions import ValidationError
from .models import Post

class PostForm(forms.ModelForm):
    # 開始日（任意）
    date = forms.DateField(
        label="開始日",
        required=False,
        widget=DateInput(attrs={"type": "date"})
    )

    end_date = forms.DateField(
        label="終了日（任意）",
        required=False,
        widget=DateInput(attrs={"type": "date"})
    )

    # 投稿に対して任意で設定する編集用パスワード（新規作成時のみ使用）
    password = forms.CharField(
        label="編集用パスワード（新しく設定する場合）",
        required=False,
        widget=PasswordInput(render_value=False),
        help_text="作成時のみ設定でき、設定すると編集時にパスワードが必要になります（任意）",
    )

    # ユーザーが自由にタグを書くフィールド
    tags_text = forms.CharField(
        label="タグ",
        required=False,
        help_text="例: #授業 #休講 #情報工学"
    )

    class Meta:
        model = Post
        fields = ["title", "date", "end_date", "body", "tags_text"]

    def clean_tags_text(self):
        """
        Ensure at least one tag is provided (server-side).
        Accepts input like '#授業 #休講' or '授業 休講'.
        """
        tags_text = self.cleaned_data.get("tags_text", "") or ""
        # normalize spaces (including fullwidth)
        normalized = tags_text.replace("　", " ").strip()
        names = []
        for raw in normalized.split():
            token = raw.strip()
            if token.startswith("#"):
                token = token[1:]
            if token:
                names.append(token)
        if not names:
            raise ValidationError("タグを1つ以上入力してください。例: #授業 #休講")
        return tags_text

    def clean(self):
        """Form-level validation: ensure end_date is not before start date."""
        cleaned = super().clean()
        start = cleaned.get("date")
        end = cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", ValidationError("終了日は開始日より前にできません。開始日より後の日付を指定してください。"))
        return cleaned
