from django.shortcuts import render
from .models import Room, Floor
from .forms import RoomSearchForm

def room_search_view(request):
    form = RoomSearchForm(request.GET or None)

    rooms = Room.objects.select_related('floor_fk').filter(is_deleted=False).order_by('room_number')
    selected_room = None
    selected_floor = None

    if form.is_valid():
        rn = form.cleaned_data.get('room_number')
        fl = form.cleaned_data.get('floor')

        if rn:
            rooms = rooms.filter(room_number__icontains=rn)
        if fl:
            rooms = rooms.filter(floor_fk=fl)
            selected_floor = fl
        else:
            first = rooms.first()
            if first:
                selected_floor = first.floor_fk

        selected_room = rooms.first()

    if not selected_floor:
        selected_floor = Floor.objects.order_by('floor').first()

    context = {
        'form': form,
        'rooms': rooms[:100],
        'selected_room': selected_room,
        'selected_floor': selected_floor,
    }
    return render(request, 'team_USL/room_search.html', context)
