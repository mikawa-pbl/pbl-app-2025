from django.shortcuts import render, get_object_or_404, redirect
from .models import Member, Groups, Contents, Users, Favorites, Slugs
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import F
import json
from django.views.decorators.clickjacking import xframe_options_exempt
import subprocess
import tempfile
import os
from .models import Member, Groups, Contents, Users, Favorites, Slugs, Project, ProjectFile

@xframe_options_exempt
def compile_project(request, project_id):
    """
    指定されたプロジェクトのファイルを一時ディレクトリに展開し、latexmkでコンパイルしてPDFを返す
    """
    project = get_object_or_404(Project, pk=project_id)
    files = project.files.all()
    
    # メインファイルを特定
    main_file_obj = files.filter(is_main=True).first()
    if not main_file_obj:
        # メイン指定がない場合は、拡張子が.texの最初のファイルを使用するか、エラーにする
        # ここでは簡易的に最初の.texファイルを使用
        main_file_obj = files.filter(filename__endswith='.tex').first()
    
    if not main_file_obj:
         return HttpResponse("Main TeX file not found.", status=400)

    # 一時ディレクトリで作業
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # ファイルを展開
            for f in files:
                file_path = os.path.join(tmpdirname, f.filename)
                # ディレクトリ階層がある場合は作成
                dirname = os.path.dirname(file_path)
                if dirname and not os.path.exists(dirname):
                    os.makedirs(dirname, exist_ok=True)
                
                if f.content and f.content.startswith("[BASE64]"):
                    # Base64デコードしてバイナリ書き込み
                    import base64
                    binary_data = base64.b64decode(f.content[8:])
                    with open(file_path, 'wb') as dst:
                        dst.write(binary_data)
                else:
                    # 通常のテキスト書き込み
                    with open(file_path, 'w', encoding='utf-8') as dst:
                        dst.write(f.content or "")
            
            # latexmk実行
            # -interaction=nonstopmode: エラーで止まらないようにする
            # -pdf: PDFを出力 (pdflatex) -> jsarticle等の場合エラーになる
            # -pdfdvi: DVI経由でPDFを作成 (uplatex + dvipdfmx) -> .latexmkrcの設定に従うはず
            # -pdfdvi: DVI経由でPDFを作成 (uplatex + dvipdfmx) -> .latexmkrcの設定に従うはず
            # 明示的に .latexmkrc を読み込ませる (-r .latexmkrc) -> 自動読み込みと重複して警告が出るため削除
            cmd = ['latexmk', '-interaction=nonstopmode', main_file_obj.filename]
            
            try:
                # Capture output for debugging
                process = subprocess.run(cmd, cwd=tmpdirname, check=True, timeout=60, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.TimeoutExpired:
                 return HttpResponse("Compilation timed out.", status=500)
            except FileNotFoundError:
                 return HttpResponse("Backend Error: 'latexmk' command not found on server.", status=500)
            except subprocess.CalledProcessError as e:
                 # コンパイルエラーの場合
                 error_msg = e.stderr.decode('utf-8', errors='replace')
                 print(f"Compilation Failed: {error_msg}") # Console log
                 return HttpResponse(f"Compilation failed:<br><pre>{error_msg}</pre>", status=500)
            
            # 生成されたPDFを探す
            pdf_filename = os.path.splitext(main_file_obj.filename)[0] + '.pdf'
            pdf_path = os.path.join(tmpdirname, pdf_filename)
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{pdf_filename}"'
                return response
            else:
                return HttpResponse("PDF not generated.", status=500)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Internal Server Error: {str(e)}", status=500)

def get_data_for_table(request):
    """
    JavaScriptのfetchリクエストに応答し、SQLからデータを取得してJSONを返す
    """
    table_type = request.GET.get('table_type', 'default')
    data_list = []

    if table_type == 'users':
        data_objects = Contents.objects.select_related('slug').annotate(
            function_slug=F('slug__function_slug')
        ).values('name', 'tex_code', 'function_slug')
        data_list = list(data_objects)

    elif table_type == 'products':
        data_objects = Contents.objects.filter(group__title__contains="数式").select_related('slug').annotate(
            function_slug=F('slug__function_slug')
        ).values('name', 'tex_code', 'function_slug')
        data_list = list(data_objects)

    else:
        data_list = []

    return JsonResponse({'data': data_list})


def index(request):
    return render(request, 'teams/team_TeXTeX/index.html')

def members(request):
    qs = Member.objects.using('team_TeXTeX').all()
    return render(request, 'teams/team_TeXTeX/members.html', {'members': qs})

@require_POST
def toggle_favorite(request):
    """
    お気に入りの登録/解除を切り替えるAPI
    """
    try:
        data = json.loads(request.body)
        slug_value = data.get('slug')
        
        # ダミーユーザー "Alice" を取得
        user = Users.objects.get(user="Alice")
        slug = get_object_or_404(Slugs, function_slug=slug_value)
        
        favorite, created = Favorites.objects.get_or_create(user=user, slug=slug)
        
        if created:
            return JsonResponse({'status': 'added', 'slug': slug.function_slug})
        else:
            favorite.delete()
            return JsonResponse({'status': 'removed', 'slug': slug.function_slug})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def save_file(request):
    """
    ファイル保存API
    POST JSON: { project_id: int, content: str, file_id: int (optional), filename: str (optional) }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        content = data.get('content')
        file_id = data.get('file_id') # 特定ファイルを更新する場合

        if not project_id:
             return JsonResponse({'error': 'Project ID required'}, status=400)

        project = get_object_or_404(Project, id=project_id)
        
        project_file = None
        
        if file_id:
            # ID指定があればそれを更新
            project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
        else:
            # 指定なければメインファイルを検索
            project_file = ProjectFile.objects.filter(project=project, is_main=True).first()
            if not project_file:
                # メインもなければ新規作成(main.tex)
                project_file = ProjectFile.objects.create(
                    project=project,
                    filename="main.tex",
                    content=content,
                    is_main=True
                )
                return JsonResponse({'status': 'saved', 'filename': project_file.filename})

        # 内容更新
        project_file.content = content
        project_file.save()
            
        return JsonResponse({'status': 'saved', 'filename': project_file.filename})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def get_project_files(request):
    """
    プロジェクトのファイル一覧を取得
    GET message: project_id
    """
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'Project ID required'}, status=400)
    
    project = get_object_or_404(Project, id=project_id)
    files = project.files.all().order_by('filename')
    
    file_list = []
    for f in files:
        file_list.append({
            'id': f.id,
            'filename': f.filename,
            'is_main': f.is_main,
        })
        
    return JsonResponse({'files': file_list, 'project_name': project.name})

@require_POST
def rename_project(request):
    """
    プロジェクトリネーム
    POST JSON: { project_id, new_project_name }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        new_project_name = data.get('new_project_name')

        if not project_id or not new_project_name:
             return JsonResponse({'error': 'Missing parameters'}, status=400)

        project = get_object_or_404(Project, id=project_id)
        project.name = new_project_name
        project.save()

        return JsonResponse({'status': 'renamed', 'project_name': project.name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def get_file_content(request):
    """
    ファイルの内容を取得
    GET message: file_id
    """
    file_id = request.GET.get('file_id')
    if not file_id:
        return JsonResponse({'error': 'File ID required'}, status=400)
    
    project_file = get_object_or_404(ProjectFile, id=file_id)
    return JsonResponse({
        'id': project_file.id,
        'filename': project_file.filename,
        'content': project_file.content or "",
        'is_main': project_file.is_main
    })

@require_POST
def create_file(request):
    """
    新規ファイル作成
    POST JSON: { project_id, filename }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        filename = data.get('filename')
        
        if not project_id or not filename:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
            
        project = get_object_or_404(Project, id=project_id)
        
        # 重複チェック
        if ProjectFile.objects.filter(project=project, filename=filename).exists():
             return JsonResponse({'error': 'File already exists'}, status=400)
             
        new_file = ProjectFile.objects.create(
            project=project,
            filename=filename,
            content=""
        )
        
        return JsonResponse({'status': 'created', 'file': {'id': new_file.id, 'filename': new_file.filename}})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def delete_file(request):
    """
    ファイル削除
    POST JSON: { file_id }
    """
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        
        if not file_id:
             return JsonResponse({'error': 'File ID required'}, status=400)

        project_file = get_object_or_404(ProjectFile, id=file_id)
        if project_file.is_main or project_file.filename == '.latexmkrc':
             return JsonResponse({'error': 'Cannot delete main file or configuration file (.latexmkrc)'}, status=400)
             
        project_file.delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def rename_file(request):
    """
    ファイルリネーム
    POST JSON: { file_id, new_filename }
    """
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        new_filename = data.get('new_filename')
        
        if not file_id or not new_filename:
             return JsonResponse({'error': 'Missing parameters'}, status=400)
             
        project_file = get_object_or_404(ProjectFile, id=file_id)
        
        # 重複チェック
        if ProjectFile.objects.filter(project=project_file.project, filename=new_filename).exclude(id=file_id).exists():
             return JsonResponse({'error': 'Filename already exists'}, status=400)
             
        project_file.filename = new_filename
        project_file.save()
        
        return JsonResponse({'status': 'renamed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def upload_file(request):
    """
    ファイルアップロード
    POST multipart/form-data: { project_id, file, upload_path (optional) }
    """
    try:
        project_id = request.POST.get('project_id')
        upload_path = request.POST.get('upload_path', '') # アップロード先フォルダパス (e.g. "folder/subfolder")
        if not project_id or 'file' not in request.FILES:
             return JsonResponse({'error': 'Missing parameters'}, status=400)

        project = get_object_or_404(Project, id=project_id)
        uploaded_file = request.FILES['file']
        
        # ファイル名とパスの構築
        filename = uploaded_file.name
        
        # upload_path の調整 (末尾の / 除去など)
        if upload_path and upload_path != "undefined" and upload_path != "null" and upload_path != "Project Root" and upload_path != project.name:
             # プロジェクト名が含まれている場合、それは除外する必要があるかもしれないが、
             # フロントエンドからは "ProjectName/folder" の形式で送られてくる可能性がある。
             # しかし、DB上の filename は "folder/file.tex" のような相対パス。
             # frontendの getLastContextPath はルートなら "" を返すはず。
             
             # 安全のため、プロトコルとして "path/to/folder" が来る前提
             final_filename = f"{upload_path}/{filename}".replace('//', '/')
        else:
             final_filename = filename

        # コンテンツの読み込み
        try:
             # まずテキストとして試みる
             content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
             # 失敗した場合はバイナリとみなし、Base64エンコードして保存
             import base64
             uploaded_file.seek(0)
             binary_data = uploaded_file.read()
             content = "[BASE64]" + base64.b64encode(binary_data).decode('utf-8')

        # 保存 (上書き or エラー?) -> 上書き許可にするか、別名にするか。
        # 今回は上書き許可とする (単純化)
        
        project_file, created = ProjectFile.objects.update_or_create(
            project=project,
            filename=final_filename,
            defaults={'content': content}
        )

        return JsonResponse({'status': 'uploaded', 'filename': final_filename})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def download_project(request, project_id):
    """
    プロジェクトの全ファイルをZIPとしてダウンロード
    """
    import zipfile
    import io
    from urllib.parse import quote

    project = get_object_or_404(Project, pk=project_id)
    files = project.files.all()

    # メモリ上でZIP作成
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for f in files:
            # フォルダ構造は filename に含まれている (e.g. "subdir/test.tex")
            content = f.content if f.content else ""
            
            if content.startswith("[BASE64]"):
                 import base64
                 binary_data = base64.b64decode(content[8:])
                 zip_file.writestr(f.filename, binary_data)
            else:
                 zip_file.writestr(f.filename, content)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    # 日本語ファイル名対応 (一応urlquote)
    filename = f"{project.name}.zip"
    response['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quote(filename)}'
    return response

@require_POST
def create_folder(request):
    """
    新規フォルダ作成 (疑似敵に .keep ファイルを作成)
    POST JSON: { project_id, folder_name }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        folder_name = data.get('folder_name')
        
        if not project_id or not folder_name:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
            
        project = get_object_or_404(Project, id=project_id)
        
        # フォルダパスの末尾に .keep をつける
        # folder_name が "chapters" なら "chapters/.keep"
        keep_filename = os.path.join(folder_name, ".keep").replace("\\", "/")
        
        if ProjectFile.objects.filter(project=project, filename=keep_filename).exists():
             return JsonResponse({'error': 'Folder already exists'}, status=400)
             
        ProjectFile.objects.create(
            project=project,
            filename=keep_filename,
            content=""
        )
        
        return JsonResponse({'status': 'created', 'folder': folder_name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def rename_folder(request):
    """
    フォルダリネーム (プレフィックス置換)
    POST JSON: { project_id, old_folder_name, new_folder_name }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        old_folder_name = data.get('old_folder_name')
        new_folder_name = data.get('new_folder_name')
        
        if not project_id or not old_folder_name or not new_folder_name:
             return JsonResponse({'error': 'Missing parameters'}, status=400)

        project = get_object_or_404(Project, id=project_id)
        
        # old_folder_name で始まるファイルを全て取得
        # "chapters" -> "chapters/" をプレフィックスとする
        old_prefix = old_folder_name if old_folder_name.endswith('/') else old_folder_name + '/'
        new_prefix = new_folder_name if new_folder_name.endswith('/') else new_folder_name + '/'
        
        files = ProjectFile.objects.filter(project=project, filename__startswith=old_prefix)
        
        count = 0
        for f in files:
            # プレフィックスを置換
            new_filename = f.filename.replace(old_prefix, new_prefix, 1)
            f.filename = new_filename
            f.save()
            count += 1
            
        return JsonResponse({'status': 'renamed', 'count': count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def main(request):
    """
    エディタメインビュー。SQLiteからサイドバーのデータを取得し、HTMLに渡す
    """
    content = []
    groups = Groups.objects.prefetch_related('contents', 'contents__slug')

    for group in groups:
        group_data = {
            "title": group.title,
            "items": group.contents.all()
        }
        content.append(group_data)

    # Aliceのお気に入り一覧を取得
    try:
        alice = Users.objects.get(user="Alice")
        favorites = Favorites.objects.filter(user=alice).select_related('slug')
        favorites_list = [fav.slug.function_slug for fav in favorites]
        
        # お気に入りアイテムの詳細情報も取得して渡す（サイドバー表示用）
        # Favoritesに関連するContentsを取得
        favorite_contents = Contents.objects.filter(slug__function_slug__in=favorites_list).select_related('slug')
    except Users.DoesNotExist:
        favorites_list = []
        favorite_contents = []

    context = {
        'content': content,
        'favorites_list': favorites_list,
        'favorite_contents': favorite_contents
    }

    return render(request, 'teams/team_TeXTeX/main.html', context)

def url(request):
    return render(request, 'teams/team_TeXTeX/main/url.html', {'temp': []})

def editer(request):
    """
    エディタメインビュー。SQLiteからサイドバーのデータを取得し、HTMLに渡す
    """
    content = []
    groups = Groups.objects.prefetch_related('contents', 'contents__slug')

    for group in groups:
        group_data = {
            "title": group.title,
            "items": group.contents.all()
        }
        content.append(group_data)

    # Aliceのお気に入り一覧を取得
    try:
        alice = Users.objects.get(user="Alice")
        favorites = Favorites.objects.filter(user=alice).select_related('slug')
        favorites_list = [fav.slug.function_slug for fav in favorites]
        
        favorite_contents = Contents.objects.filter(slug__function_slug__in=favorites_list).select_related('slug')
    except Users.DoesNotExist:
        favorites_list = []
        favorite_contents = []

    # ダミープロジェクト（Hello World Project）を取得（なければ最初のプロジェクト）
    # ダミープロジェクト（Hello World Project）を取得（なければ最初のプロジェクト）
    # テストのため、所有者に関わらず最初のプロジェクトを取得する
    project = Project.objects.first()
    file_content = ""
    if project:
        main_file = project.files.filter(is_main=True).first()
        if main_file:
            file_content = main_file.content

    context = {
        'content': content,
        'favorites_list': favorites_list,
        'favorite_contents': favorite_contents,
        'project': project,
        'file_content': file_content, # メインファイルの内容
    }

    return render(request, 'teams/team_TeXTeX/editer.html', context)

def function_template(request, function_slug):
    """
    TeX関数の詳細ガイドページをレンダリングするビュー。
    """
    item = get_object_or_404(Contents.objects.select_related('guide', 'slug'), slug__function_slug=function_slug)

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
