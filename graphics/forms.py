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
                'maxlength': '50'
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

    def clean_isbn(self):
        """
        ISBNコードのバリデーション
        - ハイフンを除去
        - 正確に13桁であること
        - 数字のみであること
        """
        isbn = self.cleaned_data.get('isbn')

        if not isbn:
            raise forms.ValidationError('ISBNコードを入力してください。')

        # ハイフンを除去
        isbn = isbn.replace('-', '')

        if len(isbn) != 13:
            print(f'13桁にしてください{isbn, len(isbn)}')
            raise forms.ValidationError('ISBNコードは13桁で入力してください。')

        if not isbn.isdigit():
            raise forms.ValidationError('ISBNコードは数字のみで入力してください。')

        return isbn
