# Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from .models import Member

from .models import Post # Post_content をインポート
from .forms import PostForm # PostForm をインポート

# データベース名を定数化 (settings.py や routers.py で設定した名前)
APP_DB = 'team_empiricism' 

def index(request):
    return render(request, 'teams/team_empiricism/index.html')

def members(request):
    qs = Member.objects.using('team_empiricism').all()  # ← team_empiricism DBを明示
    return render(request, 'teams/team_empiricism/members.html', {'members': qs})


class BoardView(View):
    """
    掲示板ページ（投稿一覧と投稿フォーム）のビュー
    （マルチDB構成対応）
    """
    
    # テンプレートのパス（APP_DIRS=False のため、プロジェクト直下からのパス）
    template_name = 'teams/team_empiricism/board.html'

    def get(self, request, *args, **kwargs):
        """ GETリクエスト時の処理 """
        
        # データベースを明示的に指定
        posts = Post.objects.using(APP_DB).all()
        form = PostForm()
        
        context = {
            'posts': posts,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """ POSTリクエスト時の処理（フォームが送信された時） """
        
        form = PostForm(request.POST)
        
        if form.is_valid():
            # 1. データをまだDBに保存しない (commit=False)
            post_instance = form.save(commit=False)
            
            # 2. データベースを明示的に指定して保存
            post_instance.save(using=APP_DB) 
            
            # 'team_empiricism:board' (urls.py で設定した name='board') にリダイレクト
            return redirect('team_empiricism:board')
        else:
            # バリデーション失敗時
            posts = Post.objects.using(APP_DB).all()
            context = {
                'posts': posts,
                'form': form, # エラー情報が含まれたフォーム
            }
            return render(request, self.template_name, context)