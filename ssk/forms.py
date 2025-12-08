# ssk/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    # ユーザーが自由にタグを書くフィールド
    tags_text = forms.CharField(
        label="タグ",
        required=False,
        help_text="例: #授業 #休講 #情報工学"
    )

    class Meta:
        model = Post
        # ManyToManyField の 'tags' はここには入れない
        fields = ["title", "date", "body", "tags_text"]
