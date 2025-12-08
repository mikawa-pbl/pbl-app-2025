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
            'age', 
            'gender', 
            'club', 
            'one_word', 
            'github_account', 
            'hobby', 
            'birthplace', 
            'birth_date', 
            'relationship_status'
        ]
        
        # ユーザーID、メアド、パスワードは、セキュリティのためこのフォームでは編集不可とします

        # 誕生日(DateField)をカレンダーピッカーで入力しやすくします
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }