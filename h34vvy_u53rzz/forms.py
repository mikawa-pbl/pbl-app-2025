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
                    "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
                    "placeholder": "コメントを書いて送信すると、下に積み上がっていきます",
                }
            ),
        }
