# ssk/forms.py
from django import forms
from django.forms.widgets import SelectDateWidget  # ★ 追加
from django.forms.widgets import PasswordInput
from .models import Post

class PostForm(forms.ModelForm):
    # イベント日を「年・月・日」のプルダウンにする（任意に変更）
    date = forms.DateField(
        label="イベント日",
        required=False,
        widget=SelectDateWidget(
            years=range(2024, 2031),              # 必要な年の範囲を指定
            empty_label=("年", "月", "日"),       # 最初の表示（プレースホルダ）
        )
    )

    # 開始/終了時刻は任意（HTML5 の time input を使用）
    start_time = forms.TimeField(
        label="開始時刻",
        required=False,
        widget=forms.TimeInput(format='%H:%M', attrs={"type": "time"})
    )
    end_time = forms.TimeField(
        label="終了時刻",
        required=False,
        widget=forms.TimeInput(format='%H:%M', attrs={"type": "time"})
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
        fields = ["title", "date", "start_time", "end_time", "body", "tags_text"]
