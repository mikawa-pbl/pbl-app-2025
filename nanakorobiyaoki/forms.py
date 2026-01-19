from django import forms
from .models import MyPage, Community, Post, Comment, Message

class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = MyPage
        fields = [
            'name',
            'email',
            'user_id',
            'password',
                  ]
        widgets = {
            'password': forms.PasswordInput(),
            'email': forms.EmailInput(attrs={
                'pattern': r'.*@tut\.jp$',
                'title': '豊橋技術科学大学のメールアドレスを入力してください',
                'placeholder': 'example@tut.jp'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@tut.jp'):
            raise forms.ValidationError("大学のメールアドレスである必要があります。")
        return email

class MyPageEditForm(forms.ModelForm):
    class Meta:
        model = MyPage
        
        # フォームに表示し、編集可能にするフィールドを指定します
        fields = [
            'name', 
            'icon', 
            'grade',
            'department', 
            'gender', 
            'club', 
            'one_word', 
            'github_account', 
            'hobby', 
            'birthplace', 
            'birth_date', 
        ]
        
        # ユーザーID、メアド、パスワードは、セキュリティのためこのフォームでは編集不可とします

        # 誕生日(DateField)をカレンダーピッカーで入力しやすくします
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class LoginForm(forms.Form):
    user_id = forms.CharField(label='学籍番号', max_length=100)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'image']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'メッセージを入力...'})
        }
