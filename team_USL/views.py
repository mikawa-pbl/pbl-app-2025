# team_USL/views.py
from django.shortcuts import render
from django.http import FileResponse, Http404
from pathlib import Path
import mimetypes

from .models import Member, RoomTable, FloorTable, FloorRange


def index(request):
    building_id = request.GET.get("building_id", "").strip()
    room_number = request.GET.get("room_number", "").strip()
    requested_floor = request.GET.get("floor", "").strip()

    floor_image_url = None
    x = None
    y = None
    room_obj = None
    error_message = None
    
    current_floor = None
    min_floor = None
    max_floor = None

    # Get FloorRange information
    if building_id:
        fr = FloorRange.objects.using("team_USL").filter(building_name=building_id).first()
        if fr:
            min_floor = fr.min_floor
            max_floor = fr.max_floor

    # Determine current_floor from params or room
    if building_id:
        # Priority 1: explicitly requested floor
        if requested_floor.isdigit():
            current_floor = int(requested_floor)
        
        # Priority 2: inferred from room_number
        elif room_number:
            # Simple inference: first character. 
            # Note: This logic may need refinement for "B1" or "10F" 
            # but kept consistent with original logic for now (assuming single digit floors mostly)
            first_char = room_number[0]
            if first_char.isdigit():
                current_floor = int(first_char)

        # Apply Range Constraints
        if current_floor is not None:
            if min_floor is not None and current_floor < min_floor:
                current_floor = min_floor
            if max_floor is not None and current_floor > max_floor:
                current_floor = max_floor

    # Fetch Room Object (always try if room_number is present)
    if building_id and room_number:
        room_obj = (
            RoomTable.objects.using("team_USL")
            .filter(building_id=building_id, room_number=room_number, is_deleted=False)
            .first()
        )
        if room_obj is None:
            if not current_floor: # Only show error if we also failed to get a floor map
                error_message = "該当する部屋が見つかりません"
    
    # Check if we should show the floor map
    if building_id and (current_floor is not None):
        floor_key = f"{building_id}-{current_floor}"
        
        floor_obj = (
            FloorTable.objects.using("team_USL")
            .filter(floor=floor_key)
            .first()
        )

        if floor_obj:
            floor_image_url = floor_obj.url
            
            # Decide if we show the pin
            # Show pin ONLY if room_obj exists AND its logical floor matches current_floor
            if room_obj:
                # Calculate room's logical floor again to compare
                room_first_char = room_number[0]
                if room_first_char.isdigit() and int(room_first_char) == current_floor:
                    x = room_obj.x
                    y = room_obj.y
        else:
            # Map not found for this floor
            # error_message = f"フロア画像が見つかりません（{floor_key}）"
            pass
            
    # Define validation list for buildings
    building_list = ["A", "A1", "A2", "B", "C", "D", "E", "F", "G"]
    # Create options object for the template
    building_options = []
    # Add 'init' option
    building_options.append({
        "value": "init",
        "label": "選択",
        "selected": (building_id == "init" or not building_id)
    })
    
    for b in building_list:
        building_options.append({
            "value": b,
            "label": b,
            "selected": (building_id == b)
        })

    context = {
        "building_id": building_id,
        "room_number": room_number,
        "floor_image_url": floor_image_url,
        "x": x,
        "y": y,
        "room_obj": room_obj,
        "error_message": error_message,
        
        "current_floor": current_floor,
        "min_floor": min_floor,
        "max_floor": max_floor,
        "building_options": building_options, # Pass this to template
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
