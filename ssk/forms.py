# ssk/forms.py
from django import forms
from django.forms.widgets import DateInput, TimeInput, PasswordInput
from django.core.exceptions import ValidationError
from .models import Post
from datetime import datetime, time

class PostForm(forms.ModelForm):
    # 開始日（任意）
    start_date = forms.DateField(
        label="開始日",
        required=False,
        widget=DateInput(attrs={"type": "date"})
    )

    start_time = forms.TimeField(
        label="開始時刻",
        required=False,
        widget=TimeInput(attrs={"type": "time"})
    )

    end_date = forms.DateField(
        label="終了日（任意）",
        required=False,
        widget=DateInput(attrs={"type": "date"})
    )

    end_time = forms.TimeField(
        label="終了時刻（任意）",
        required=False,
        widget=TimeInput(attrs={"type": "time"})
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
        fields = ["title", "start_date", "start_time", "end_date", "end_time", "body", "tags_text"]

    def __init__(self, *args, **kwargs):
        # allow initializing fields from existing instance (for edit)
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance is not None:
            if instance.start is not None:
                initial.setdefault('start_date', instance.start.date())
                if not instance.all_day:
                    initial.setdefault('start_time', instance.start.time().replace(microsecond=0))
            if instance.end is not None:
                initial.setdefault('end_date', instance.end.date())
                if not instance.all_day and instance.end.time() is not None:
                    initial.setdefault('end_time', instance.end.time().replace(microsecond=0))
            # tags_text is handled by the view (initial passed there)
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

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
        """Form-level validation: combine date+time into datetimes and ensure end is not before start."""
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        start_time = cleaned.get('start_time')
        end_date = cleaned.get('end_date')
        end_time = cleaned.get('end_time')

        # default values
        start_dt = None
        end_dt = None
        all_day = True

        if start_date:
            if start_time:
                start_dt = datetime.combine(start_date, start_time)
                all_day = False
            else:
                # treat as all-day -> start at 00:00
                start_dt = datetime.combine(start_date, time(0, 0, 0))
        if end_date:
            if end_time:
                end_dt = datetime.combine(end_date, end_time)
                all_day = False
            else:
                # treat as all-day -> end at 23:59:59
                end_dt = datetime.combine(end_date, time(23, 59, 59))

        # If only start provided, set end to start (single-day)
        if start_dt and not end_dt:
            end_dt = start_dt
        # If only end provided, set start to end
        if end_dt and not start_dt:
            start_dt = end_dt

        if start_dt and end_dt and end_dt < start_dt:
            self.add_error('end_date', ValidationError("終了日は開始日より前にできません。開始日より後の日付を指定してください。"))

        cleaned['start'] = start_dt
        cleaned['end'] = end_dt
        cleaned['all_day'] = all_day
        return cleaned
