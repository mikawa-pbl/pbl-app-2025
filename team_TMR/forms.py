from django import forms
from .models import Profile, Roadmap, ES, InvitationCode

DEFAULT_CODES = ['TMR_DEFAULT_2025', 'PBL_FIGHT_ON']

class InvitationCodeForm(forms.Form):
    """
    招待コードを入力するフォーム
    """
    invitation_code = forms.CharField(label="招待コード", max_length=50)

    def clean_invitation_code(self):
        code_str = self.cleaned_data.get('invitation_code')

        # 1. デフォルトコードのリストに含まれているかチェック
        if code_str in DEFAULT_CODES:
            return code_str # 有効なコードとして返す

        # 2. デフォルトコードでない場合、DBに存在するか（従来のロジック）
        try:
            # 未使用の有効なコードかチェック
            code_obj = InvitationCode.objects.get(code=code_str, used=False)
        except InvitationCode.DoesNotExist:
            raise forms.ValidationError("有効な招待コードではありません。")
        
        return code_str

class ProfileForm(forms.ModelForm):
    """
    プロフィール編集フォーム
    """
    class Meta:
        model = Profile
        fields = ['nickname', 'affiliation', 'contact']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'affiliation': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class RoadmapForm(forms.ModelForm):
    """
    ロードマップ登録・編集フォーム
    """
    class Meta:
        model = Roadmap
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

class ESForm(forms.ModelForm):
    """
    ES登録・編集フォーム
    """
    class Meta:
        model = ES
        fields = ['company', 'question', 'answer']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }