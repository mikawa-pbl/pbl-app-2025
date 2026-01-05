from django import forms
from .models import MyPage

class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = MyPage
        fields = [
            'name',
            'email',
            'password',
            'user_id',
                  ]  

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

from .models import Community, Post, Comment

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

