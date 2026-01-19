# shiokara/context_processors.py
from .models import Person

def current_person(request):
    """
    セッションに person_id があれば Person を取得してテンプレートに渡す。
    全テンプレートで 'person' という変数名で参照できるようになる。
    """
    person = None
    person_id = request.session.get("person_id")
    if person_id:
        try:
            person = Person.objects.get(pk=person_id)
        except Person.DoesNotExist:
            person = None
    return {"person": person}
