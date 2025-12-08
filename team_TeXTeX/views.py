from django.shortcuts import render, get_object_or_404
from .models import Member, Main, Editer, url, main_select, Group, Content


def index(request):
    return render(request, 'teams/team_TeXTeX/index.html')

def members(request):
    qs = Member.objects.using('team_TeXTeX').all()
    return render(request, 'teams/team_TeXTeX/members.html', {'members': qs})

def main(request):
    """
    エディタメインビュー。SQLiteからサイドバーのデータを取得し、HTMLに渡す
    """
    qs = Editer.objects.using('team_TeXTeX').all()

    # データベースからGroupとContentを取得し、テンプレートで扱いやすい辞書リストに変換
    content = []
    groups = Group.objects.prefetch_related('items')

    for group in groups:
        group_data = {
            "title": group.title,
            "items": []
        }
        
        # Contentのデータを取得
        for item in group.items.all():
            group_data["items"].append({
                "name": item.name,
                "tex_code": item.tex_code,
                "slug": item.function_slug
            })
            
        content.append(group_data)

    context = {
        'editer': qs,
        'content': content
    }
    
    return render(request, 'teams/team_TeXTeX/main.html', context)

def main_select(request, select):
    template_name = f'teams/team_TeXTeX/main/{select}.html'
    return render(request, template_name)

def url(request):
    qs = url.objects.using('team_TeXTeX').all()
    return render(request, 'teams/team_TeXTeX/main/url.html', {'temp': qs})

def editer(request):
    """
    エディタメインビュー。SQLiteからサイドバーのデータを取得し、HTMLに渡す
    """
    qs = Editer.objects.using('team_TeXTeX').all()

    # データベースからGroupとContentを取得し、テンプレートで扱いやすい辞書リストに変換
    content = []
    groups = Group.objects.prefetch_related('items')

    for group in groups:
        group_data = {
            "title": group.title,
            "items": []
        }
        
        # Contentのデータを取得
        for item in group.items.all():
            group_data["items"].append({
                "name": item.name,
                "tex_code": item.tex_code,
                "slug": item.function_slug
            })
            
        content.append(group_data)

    context = {
        'editer': qs,
        'content': content
    }
    
    return render(request, 'teams/team_TeXTeX/editer.html', context)

def function_template(request, function_slug):
    """
    TeX関数の詳細ガイドページをレンダリングするビュー。
    """
    # スラッグに基づいてSidebarItemオブジェクトを取得。見つからなければ404エラー
    item = get_object_or_404(Content, function_slug=function_slug)
    
    context = {
        'item': item,
    }
    return render(request, 'teams/team_TeXTeX/function_template.html', context)

def handle_404_not_found(request, unmatched_path=None):
    """
    team_TeXTeX/以下のURLで存在しないパスが指定された場合のカスタム404エラーを処理します。
    """
    # テンプレートに渡すコンテキスト
    context = {
        'message': 'お探しのページは見つかりませんでした。',
        # キャプチャしたマッチしなかったパスを渡す
        'unmatched_path': unmatched_path or request.path.lstrip('/team_TeXTeX/')
    }
    # custom_404.html をレンダリングし、ステータスコード404を返す
    return render(request, 'teams/team_TeXTeX/custom_404.html', context, status=404)
