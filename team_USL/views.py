# team_USL/views.py
from django.shortcuts import render
from django.http import FileResponse, Http404
from pathlib import Path
import mimetypes

from .models import Member, RoomTable, FloorTable # FloorTableはRoomTable経由で取れるので必須ではない


def index(request):
    building_id = request.GET.get("building_id", "").strip()
    room_number = request.GET.get("room_number", "").strip()

    floor_image_url = None
    x = None
    y = None
    room_obj = None
    error_message = None

    if building_id and room_number:
        # 1) 部屋を検索
        room_obj = (
            RoomTable.objects.using("team_USL")
            .filter(building_id=building_id, room_number=room_number, is_deleted=False)
            .first()
        )

        if room_obj is None:
            error_message = "該当する部屋が見つかりません"
        else:
            # 2) floor_key を作って floor_table を検索
            #    例: building_id="A", room_number="101" → "A-1"
            first_digit = room_number[0]  # room_numberは空でない前提
            floor_key = f"{building_id}-{first_digit}"

            floor_obj = (
                FloorTable.objects.using("team_USL")
                .filter(floor=floor_key)
                .first()
            )

            if floor_obj is None:
                error_message = f"フロア画像が見つかりません（{floor_key}）"
            else:
                floor_image_url = floor_obj.url
                x = room_obj.x
                y = room_obj.y

    context = {
        "building_id": building_id,
        "room_number": room_number,
        "floor_image_url": floor_image_url,
        "x": x,
        "y": y,
        "room_obj": room_obj,        # デバッグ用
        "error_message": error_message,  # index.htmlで表示できる
    }
    return render(request, "teams/team_USL/index.html", context)


def members(request):
    qs = Member.objects.using("team_USL").all()  # ← team_USL DBを明示
    return render(request, "teams/team_USL/members.html", {"members": qs})


# 画像配信用（既存のまま）
def serve_template_image(request, filename: str):
    """
    templates/teams/team_USL/images/ 以下に置いた画像を、
    /team_USL/images/<filename> で配信するビュー。
    """
    # プロジェクトルート = team_USL ディレクトリの1つ上
    base_dir = Path(__file__).resolve().parent.parent

    # templates/teams/team_USL/images/<filename>
    images_dir = base_dir / "templates" / "teams" / "team_USL" / "images"
    file_path = (images_dir / filename).resolve()

    # ディレクトリトラバーサル対策：必ず images_dir 配下か確認
    if not str(file_path).startswith(str(images_dir)):
        raise Http404("Invalid path")

    if not file_path.exists():
        raise Http404("Image not found")

    # Content-Type を推定
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"

    return FileResponse(open(file_path, "rb"), content_type=content_type)
