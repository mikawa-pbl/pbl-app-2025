from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["comment"]
        labels = {
            "comment": "コメント",
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "コメントを書いて送信すると、下に積み上がっていきます",
                }
            ),
        }
