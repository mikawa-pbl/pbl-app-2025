from django import forms
from .models import Paper

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        # id と submit_time は自動なので含めない
        fields = [
            'title', 'author', 'booktitle', 'year', 'doi', 'url',
            'submitter', 'keywords',
            'imp_overview', 'imp_comparison', 'imp_idea',
            'imp_usefulness', 'imp_discussion',
            'imp_relation', 'note',
            'paper_file', 'rc_slide', 'paper_figure',
        ]
