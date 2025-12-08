# ssk/forms.py
from django import forms
from django.forms.widgets import SelectDateWidget  # ★ 追加
from .models import Post

class PostForm(forms.ModelForm):
    # イベント日を「年・月・日」のプルダウンにする
    date = forms.DateField(
        label="イベント日",
        widget=SelectDateWidget(
            years=range(2024, 2031),              # 必要な年の範囲を指定
            empty_label=("年", "月", "日"),       # 最初の表示（プレースホルダ）
        )
    )

    # ユーザーが自由にタグを書くフィールド
    tags_text = forms.CharField(
        label="タグ",
        required=False,
        help_text="例: #授業 #休講 #情報工学"
    )

    class Meta:
        model = Post
        fields = ["title", "date", "body", "tags_text"]
