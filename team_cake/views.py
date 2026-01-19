from django.shortcuts import render, redirect
from .models import Good, SOSMessage
from .forms import GoodsForm, SOSMessageForm
from types import SimpleNamespace
from django.db import connections
from pathlib import Path
import mimetypes
import uuid
from django.http import FileResponse, Http404
from django.conf import settings
from django.utils import timezone

# def index(request):
#     return render(request, 'teams/team_cake/index.html')

def _get_index_context():
    try:
        # Auto-delete expired goods before fetching
        Good.objects.using('team_cake').filter(expiration_time__lt=timezone.now()).delete()
        
        # 通常はORMで取得（UUIDField の変換が走る）
        qs = Good.objects.using('team_cake').all()
        
        # スライダー用に最後の3件を取得（登録順と仮定）
        all_goods = list(qs)
        slider_goods = all_goods[-3:] if len(all_goods) >= 3 else all_goods
        slider_goods = list(reversed(slider_goods))

        sos_message = SOSMessage.objects.using('team_cake').filter(is_active=True).order_by('-created_at').first()
        
        return {'goods': qs, 'slider_goods': slider_goods, 'sos_message': sos_message}
    except ValueError:
        # DB に古い整数 ID 等、UUID として変換できない値が入っている場合のフォールバック。
        # テンプレートは objects の `.name` / `.price` を参照する想定のため SimpleNamespace を作る。
        conn = connections['team_cake']
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, price, description, image_filename, original_price FROM team_cake_good')
            rows = cur.fetchall()

        goods = [SimpleNamespace(id=row[0], name=row[1], price=row[2], description=row[3], image_filename=row[4], original_price=row[5]) for row in rows]
        
        slider_goods = goods[-3:] if len(goods) >= 3 else goods
        slider_goods = list(reversed(slider_goods))
        
        return {'goods': goods, 'slider_goods': slider_goods, 'sos_message': None}

def index(request):
    context = _get_index_context()
    context['is_staff'] = False
    return render(request, 'teams/team_cake/index.html', context)

def admin_index(request):
    context = _get_index_context()
    context['is_staff'] = True
    return render(request, 'teams/team_cake/index.html', context)

def registration_goods(request):
    if request.method == 'POST':
        form = GoodsForm(request.POST, request.FILES)
        if form.is_valid():
            # create instance but don't commit so we can set image_filename
            good = form.save(commit=False)

            # handle uploaded file (if any) and save it under this app's templates images dir
            uploaded = request.FILES.get('image')
            if uploaded:
                base_dir = Path(__file__).resolve().parent.parent
                images_dir = base_dir / 'templates' / 'teams' / 'team_cake' / 'images'
                images_dir.mkdir(parents=True, exist_ok=True)

                # generate unique filename preserving extension
                orig_name = uploaded.name
                ext = ''
                if '.' in orig_name:
                    ext = '.' + orig_name.split('.')[-1]
                filename = f"{uuid.uuid4().hex}{ext}"
                dest_path = (images_dir / filename).resolve()

                # prevent directory traversal
                if not str(dest_path).startswith(str(images_dir)):
                    raise Http404("Invalid target path")

                with open(dest_path, 'wb') as out:
                    for chunk in uploaded.chunks():
                        out.write(chunk)

                good.image_filename = filename

            # Save to the team_cake db explicitly (router may handle but be explicit)
            good.save(using='team_cake')
            return redirect('team_cake:registration_goods')
    else:
        form = GoodsForm()
    return render(request, 'teams/team_cake/registrationGoods.html', {'form': form})


def edit_good(request, pk):
    try:
        good = Good.objects.using('team_cake').get(pk=pk)
    except Exception:
        raise Http404("Good not found")

    if request.method == 'POST':
        form = GoodsForm(request.POST, request.FILES, instance=good)
        if form.is_valid():
            good = form.save(commit=False)

            uploaded = request.FILES.get('image')
            if uploaded:
                base_dir = Path(__file__).resolve().parent.parent
                images_dir = base_dir / 'templates' / 'teams' / 'team_cake' / 'images'
                images_dir.mkdir(parents=True, exist_ok=True)

                orig_name = uploaded.name
                ext = ''
                if '.' in orig_name:
                    ext = '.' + orig_name.split('.')[-1]
                filename = f"{uuid.uuid4().hex}{ext}"
                dest_path = (images_dir / filename).resolve()

                if not str(dest_path).startswith(str(images_dir)):
                    raise Http404("Invalid target path")

                with open(dest_path, 'wb') as out:
                    for chunk in uploaded.chunks():
                        out.write(chunk)

                # Delete old image
                if good.image_filename:
                    old_image_path = images_dir / good.image_filename
                    if old_image_path.exists():
                        old_image_path.unlink()

                good.image_filename = filename

            good.save(using='team_cake')
            return redirect('team_cake:index')
    else:
        form = GoodsForm(instance=good)
    
    return render(request, 'teams/team_cake/registrationGoods.html', {'form': form, 'is_edit': True})


def delete_good(request, pk):
    if request.method == 'POST':
        try:
            good = Good.objects.using('team_cake').get(pk=pk)
            image_filename = good.image_filename
            good.delete()

            if image_filename:
                base_dir = Path(__file__).resolve().parent.parent
                images_dir = base_dir / 'templates' / 'teams' / 'team_cake' / 'images'
                image_path = images_dir / image_filename
                if image_path.exists():
                    image_path.unlink()

        except Exception:
            conn = connections['team_cake']
            with conn.cursor() as cur:
                cur.execute('SELECT image_filename FROM team_cake_good WHERE id = %s', [pk])
                row = cur.fetchone()
                if row:
                    image_filename = row[0]
                    cur.execute('DELETE FROM team_cake_good WHERE id = %s', [pk])

                    if image_filename:
                        base_dir = Path(__file__).resolve().parent.parent
                        images_dir = base_dir / 'templates' / 'teams' / 'team_cake' / 'images'
                        image_path = images_dir / image_filename
                        if image_path.exists():
                            image_path.unlink()

        return redirect('team_cake:index')
    return redirect('team_cake:index')



def add_sos_message(request):
    if request.method == 'POST':
        form = SOSMessageForm(request.POST)
        if form.is_valid():
            sos = form.save(commit=False)
            sos.save(using='team_cake')
            return redirect('team_cake:index')
    else:
        form = SOSMessageForm()
    
    return render(request, 'teams/team_cake/add_sos_message.html', {'form': form})


def serve_template_image(request, filename: str):
    """
    Serve files placed under templates/teams/team_cake/images/ at
    /team_cake/images/<filename> similar to `team_USL.serve_template_image`.
    """
    base_dir = Path(__file__).resolve().parent.parent
    images_dir = base_dir / 'templates' / 'teams' / 'team_cake' / 'images'

    file_path = (images_dir / filename).resolve()

    if not str(file_path).startswith(str(images_dir)):
        raise Http404("Invalid path")

    if not file_path.exists():
        raise Http404("Image not found")

    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = 'application/octet-stream'

    return FileResponse(open(file_path, 'rb'), content_type=content_type)