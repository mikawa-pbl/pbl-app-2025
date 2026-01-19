from .views import get_current_user

def takenoko_user(request):
    return {
        'takenoko_user': get_current_user(request),
    }