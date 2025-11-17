from django.shortcuts import render
from .models import Member
# team_USL/views.py
from django.http import FileResponse, Http404
from pathlib import Path
import mimetypes

def index(request):
    return render(request, 'teams/team_USL/index.html')

def members(request):
    qs = Member.objects.using('team_USL').all()  # ← team_USL DBを明示
    return render(request, 'teams/team_USL/members.html', {'members': qs})
# Create your views here.
def serve_template_image(request, filename: str):
    """
    templates/team_USL/images/ 以下に置いた画像を、
    /team_USL/images/<filename> で配信するビュー。

    例:
      <img src="images/A-3.png"> →
      /team_USL/images/A-3.png を取りにくる
    """
    # プロジェクトルート = team_USL ディレクトリの1つ上
    base_dir = Path(__file__).resolve().parent.parent

    # templates/team_USL/images/<filename>
    images_dir = base_dir / 'templates' / 'teams' / 'team_USL' / 'images'
    file_path = (images_dir / filename).resolve()

    # ディレクトリトラバーサル対策：必ず images_dir 配下か確認
    if not str(file_path).startswith(str(images_dir)):
        raise Http404("Invalid path")

    if not file_path.exists():
        raise Http404("Image not found")

    # Content-Type を推定
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = 'application/octet-stream'

    return FileResponse(open(file_path, 'rb'), content_type=content_type)
