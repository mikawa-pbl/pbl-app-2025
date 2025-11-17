from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    """
    掲示板の投稿内容を入力するためのフォーム
    """
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            # フォームの <textarea> に属性を設定
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': 'ここに投稿内容を入力してください...'}),
        }
        labels = {
            'content': '新規投稿', # フォームのラベル名
        }