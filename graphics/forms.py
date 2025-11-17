from django import forms
from .models import BookReview


class BookReviewForm(forms.ModelForm):
    """
    参考書レビュー入力フォーム
    """
    class Meta:
        model = BookReview
        fields = ['subject', 'isbn', 'review']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: データベース概論'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 9784000000000',
                'maxlength': '13'
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'この参考書のレビューを書いてください',
                'rows': 5
            }),
        }
        labels = {
            'subject': '科目名',
            'isbn': 'ISBN',
            'review': 'レビュー',
        }
