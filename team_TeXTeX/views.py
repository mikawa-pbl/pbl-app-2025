from django.shortcuts import render
from .models import Member, Main, Editer, url, main_select

def index(request):
    return render(request, 'teams/team_TeXTeX/index.html')

def members(request):
    qs = Member.objects.using('team_TeXTeX').all()
    return render(request, 'teams/team_TeXTeX/members.html', {'members': qs})

def main(request):
    qs = Main.objects.using('team_TeXTeX').all()
    return render(request, 'teams/team_TeXTeX/main.html', {'main': qs})

def editer(request):
    qs = Editer.objects.using('team_TeXTeX').all()
    
    # サイドバーのデータ構造をPythonで定義
    sidebar_items = [
        {
            "title": "体裁",
            "is_open": True,
            "items": [
                {"name": "タイトル", "tex_code": "\\title{タイトル}"},
                {"name": "概要", "tex_code": "\\abstract{概要}"},
                {"name": "目次", "tex_code": "\\tableofcontents"},
            ]
        },
        {
            "title": "図表",
            "is_open": True,
            "items": [
                {"name": "図の挿入", "tex_code": "\\begin{figure}...\end{figure}"},
            ]
        },
        {
            "title": "文字",
            "is_open": True,
            "items": [
                {"name": "書体", "tex_code": "\\textbf{太字}"},
                {"name": "文字サイズ", "tex_code": "\\large{文字サイズ}"},
                {"name": "文字色", "tex_code": "\\textcolor{red}{文字色}"},
            ]
        },
        {
            "title": "数式",
            "is_open": True,
            "items": [
                {"name": "平方根", "tex_code": "\\sqrt{x}"},
                {"name": "絶対値", "tex_code": "|x|"},
                {"name": "極限", "tex_code": "\\lim_{n \\to \\infty} x_n"},
            ]
        },
    ]

    context = {
        'editer': qs,            # 既存のクエリセットデータ
        'sidebar_items': sidebar_items # サイドバーデータを追加
    }
    
    return render(request, 'teams/team_TeXTeX/editer.html', context)

def main_select(request,select):
    template_name = f'teams/team_TeXTeX/main/{select}.html'
    return render(request, template_name)

def url(request):
    qs = url.objects.using('team_TeXTeX').all()
    return render(request, 'teams/team_TeXTeX/main/url.html', {'temp': qs})


